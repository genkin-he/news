# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点在 Cloudflare 后面，规则只盯 Chromium 系指纹：chrome131 / chrome136 / edge101 一律
# 403 + cf-mitigated: challenge（正文为 "Just a moment..."），而 safari17_0 / safari18_0 /
# firefox133 均返回 200。原实现用裸 requests（无任何指纹伪装）且携带一串 2025-09-28 签发的
# 硬编码 cookie（含 __cf_bm）——该类 cookie 绑定签发时的 IP 与 UA，硬编码对 CI 毫无作用。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari17_0")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

base_url = "https://apnews.com"
list_url = "https://apnews.com/hub/financial-markets"
filename = "./news/data/apnews/list.json"

LIST_SELECTOR = "h3.PagePromo-title a"
CONTENT_SELECTOR = ".RichTextStoryBody"
# 正文里的 div 是图片与嵌入容器，实测剥离 5534 -> 4808 字符、不会伤到正文；
# 但多个站点上出现过「正文整体嵌在 div 内」的结构（worldpharmaceuticals 会被清成 0），
# 故剥离后为空时退回保守范围
STRIP_SELECTOR = "div,script,style,iframe,noscript"
STRIP_SELECTOR_SAFE = "script,style,iframe,noscript"

MAX_POSTS = 3
KEEP_POSTS = 40
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；被质询时自动降级到下一个档位"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
            )
        )
    # 只有整条降级链都失败才是真正的失败；中间某个档位被拒属于预期内的降级过程，
    # 记为 info 即可，否则日志里会出现「报错但整轮其实成功」的误导。
    util.error(
        "request url: {}, all {} impersonate profiles rejected, last error: {}".format(
            url,
            len(IMPERSONATE_PROFILES),
            response.status_code if response is not None else "no response",
        )
    )
    return response


def parse_pub_date(soup):
    """详情页带 meta[article:published_time]（形如 2026-09-11T04:59:38，无时区，按 UTC 处理）"""
    node = soup.select_one('meta[property="article:published_time"]')
    value = (node.get("content") or "").strip() if node else ""
    if not value:
        return util.current_time_string()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return util.current_time_string()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200:
            return "", ""

        text = response.text
        if "Access Restricted" in text:
            util.error("access restricted: {}".format(link))
            return "", ""

        body = BeautifulSoup(text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""

        before = len(soup.get_text(" ", strip=True))
        stripped = BeautifulSoup(str(soup), "lxml").select_one(CONTENT_SELECTOR)
        for element in stripped.select(STRIP_SELECTOR):
            element.decompose()
        after = len(stripped.get_text(" ", strip=True))

        if after == 0:
            stripped = soup
            for element in stripped.select(STRIP_SELECTOR_SAFE):
                element.decompose()
            after = len(stripped.get_text(" ", strip=True))
            if after == 0:
                util.error("article content empty after strip: {}".format(link))
                return "", ""
            util.info("content text: {} -> {} chars (safe strip)".format(before, after))
        else:
            util.info("content text: {} -> {} chars".format(before, after))

        # 文末两段是 AP 的版权与订阅声明，原实现即已剔除；此处补上越界保护
        paragraphs = stripped.select("p")
        for paragraph in paragraphs[-2:]:
            paragraph.decompose()

        return str(stripped).replace("\n", "").replace("\r", ""), parse_pub_date(body)
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return "", ""


def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(url, status))
        return

    soup = BeautifulSoup(response.text, "lxml")
    nodes = soup.select(LIST_SELECTOR)
    if not nodes:
        util.log_action_error("request url: {}, no article node parsed".format(url))
        return
    util.info("nodes: {}".format(len(nodes)))

    for node in nodes:
        if len(new_articles) >= MAX_POSTS:
            break

        link = (node.get("href") or "").strip()
        title = node.get_text().replace("\n", "").strip()
        if not link or not title:
            continue
        if link in links:
            util.info("exists link: {}".format(link))
            continue

        description, pub_date = get_detail(link)
        if description == "":
            continue

        links.add(link)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "author": "apnews",
                "pub_date": pub_date,
                "source": "apnews",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, list_url)
