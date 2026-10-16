# -*- coding: UTF-8 -*-
import base64
import hashlib
import time
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点用 Automattic（a8c-cdn）的 Hashcash 工作量证明拦截可疑来源：首次请求 403，正文为
# "Checking your browser..."，并下发 _hcc cookie。挑战不看 TLS 指纹——chrome131 /
# safari18_0 / firefox133 表现完全一致，故单档位不做降级。
#
# _hcc 形如 "<hmac>:<base64>"，base64 解出 "客户端IP|时间戳|token|难度"。需找到 nonce 使
# sha256(seed + str(nonce)) 的十六进制以 CHALLENGE_PREFIX 开头，再把 base64(seed+nonce)
# 放进 X-Hashcash-Solution 头 POST /__challenge，服务端即下发 _hcp 放行。
#
# 关键点：页面 JS 里 m() 的守卫是 `r || !l || c || (a && !s) || fetch(...)`，其中 c 是一个
# 3500ms 定时器——浏览器必然在拿到挑战 3.5 秒后才提交解，服务端会校验这个最小耗时。
# 立刻提交会得到 400 且 _hcc 被作废（实测），因此必须等满 MIN_CHALLENGE_SECONDS。
IMPERSONATE = "chrome131"
CHALLENGE_PREFIX = "0000"
CHALLENGE_MAX_NONCE = 2000000
MIN_CHALLENGE_SECONDS = 3.6
CHALLENGE_URL = "https://pharmatimes.com/__challenge"
CHALLENGE_HOST = "pharmatimes.com"

base_url = "https://pharmatimes.com/feed/"
filename = "./news/data/pharmatimes/list.json"
util = SpiderUtil()

# 详情页正文容器（Divi 主题，et_pb_ 前缀）。feed 自带的 description 仅约 180 字符的摘要，
# 不能用，正文必须回详情页取。
CONTENT_SELECTOR = "div.et_pb_post_content"
# select() 只匹配后代，不含容器自身，因此不会把 et_pb_post_content 本身剥掉
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript"

# 详情页约 450KB，且首次可能要付 3.6 秒挑战成本；CI 端 gtimeout 为 15 秒，故收敛条数
MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None
_challenge_done = False


def get_session():
    """列表与详情共用一个 session，挑战通过后的 _hcp 才能复用"""
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


def solve_hashcash(seed):
    for nonce in range(CHALLENGE_MAX_NONCE):
        candidate = seed + str(nonce)
        digest = hashlib.sha256(candidate.encode()).hexdigest()
        if digest.startswith(CHALLENGE_PREFIX):
            return candidate, nonce
    return None, None


def pass_challenge(session, issued_at):
    """按站点 JS 的流程完成挑战：解 PoW -> 等满最小耗时 -> POST /__challenge"""
    raw = session.cookies.get("_hcc")
    if not raw or ":" not in raw:
        util.error("hashcash: no _hcc cookie to solve")
        return False

    try:
        seed = base64.b64decode(raw.split(":")[1]).decode()
    except Exception as e:
        util.error("hashcash: bad _hcc payload: {}".format(str(e)))
        return False

    solution, nonce = solve_hashcash(seed)
    if solution is None:
        util.error("hashcash: no solution within {} nonces".format(CHALLENGE_MAX_NONCE))
        return False

    remaining = MIN_CHALLENGE_SECONDS - (time.time() - issued_at)
    if remaining > 0:
        time.sleep(remaining)

    response = session.post(
        CHALLENGE_URL,
        headers={
            "X-Hashcash-Solution": base64.b64encode(solution.encode()).decode(),
            "X-Hashcash-Host": CHALLENGE_HOST,
            "accept": "*/*",
            "origin": "https://" + CHALLENGE_HOST,
            "referer": base_url,
        },
        timeout=TIMEOUT,
    )
    passed = response.status_code == 200 and "_hcp" in session.cookies
    util.info(
        "hashcash: nonce={}, post={}, passed={}".format(
            nonce, response.status_code, passed
        )
    )
    return passed


def request(url):
    """被挑战时求解一次；同一 session 内只求解一次，之后靠 _hcp 通行"""
    global _challenge_done

    session = get_session()
    issued_at = time.time()
    response = session.get(url, timeout=TIMEOUT)

    if response.status_code == 403 and not _challenge_done and "_hcc" in session.cookies:
        util.info("hashcash challenge received, solving...")
        _challenge_done = True
        if pass_challenge(session, issued_at):
            response = session.get(url, timeout=TIMEOUT)

    if response.status_code != 200:
        text = response.text or ""
        util.error(
            "request url: {}, error: {}, challenge: {}, body: {}".format(
                url,
                response.status_code,
                "Checking your browser" in text,
                " ".join(text.split())[:120],
            )
        )
    return response


def parse_pub_date(item):
    """RSS pubDate 为 RFC 822，交给 email.utils 解析以容忍 +0000 与 GMT 等写法差异"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            parsedate_to_datetime(value)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except (TypeError, ValueError):
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        # 记录剥离前后的文本量：若某篇文章的正文段落被包在 div 里，剥离会造成大幅缩水，
        # 从日志即可发现，而不是等到入库后才察觉正文残缺。
        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def parse_rss_xml(xml_content):
    soup = BeautifulSoup(xml_content, "xml")
    items = []
    for item in soup.find_all("item"):
        title_node = item.find("title")
        link_node = item.find("link")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = link_node.get_text(strip=True)
        if not title or not link:
            continue
        items.append({"title": title, "link": link, "pub_date": parse_pub_date(item)})
    return items


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    try:
        response = request(link)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(link, str(e)))
        return

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(link, response.status_code)
        )
        return

    rss_items = parse_rss_xml(response.text)
    if not rss_items:
        util.log_action_error("request url: {}, no rss item parsed".format(link))
        return

    for item in rss_items:
        if len(_new_articles) >= MAX_POSTS:
            break
        if item["link"] in _links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description = get_detail(item["link"])
        if description == "":
            continue

        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "pharmatimes",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
