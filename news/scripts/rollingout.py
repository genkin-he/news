# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 后面。原实现用裸 requests 且带一串 2025-11-10 签发、早已过期的
# cf_clearance——该 cookie 绑定签发时的 IP 与 UA，硬编码在仓库里对 CI 毫无作用。
# 实测各档位结果不同：chrome131 被 403 + cf-mitigated: challenge，而 chrome136 /
# safari15_5 / safari17_0 / safari18_0 / firefox133 / edge101 均返回 200，
# 故此处档位降级有实据。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "chrome136")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

base_url = "https://rollingout.com"
list_url = "https://rollingout.com/category/tech/"
filename = "./news/data/rollingout/list.json"
util = SpiderUtil()

# 2026-11 站点由 Elementor 换成 Bricks 主题：列表项变为 li.bricks-layout-item，
# 正文容器变为 div.brxe-post-content（外面再套两层无 class 的 div）。旧选择器保留兜底。
LIST_SELECTORS = ("li.bricks-layout-item h3 a", "h3.elementor-post__title a")
# 详情页正文容器，按顺序尝试
CONTENT_SELECTORS = (
    "div.brxe-post-content",
    "div.standard-markdown",
    "div.elementor-widget-theme-post-content",
)
# 多数文章的 div 只是 Elementor 的包装层与广告位（实测剥离 31 个 div 仅损失 64 字符），
# 但并非全部：CI 实测 /2026/09/05/what-a-150000-scam-reveals-about-ai/ 的正文段落整体嵌在
# div 内，按此范围剥离会把正文清空。故先按完整范围剥，若结果为空再退回保守范围（保留 div）。
STRIP_SELECTOR = "script,style,iframe,noscript,div"
STRIP_SELECTOR_SAFE = "script,style,iframe,noscript"

MAX_POSTS = 5
KEEP_POSTS = 10
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
    """详情页的 meta[article:published_time] 带完整时区，无需推断"""
    node = soup.select_one('meta[property="article:published_time"]')
    value = (node.get("content") or "").strip() if node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except ValueError:
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200:
            return "", ""

        body = BeautifulSoup(response.text, "lxml")
        soup = None
        for candidate in CONTENT_SELECTORS:
            soup = body.select_one(candidate)
            if soup is not None:
                break
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""
        # Bricks 主题把段落包在只有一个子 div 的包装层里，剥 div 前先下钻到段落那一层，
        # 否则整段正文会随包装层一起被剥掉
        while True:
            children = soup.find_all(recursive=False)
            if len(children) == 1 and children[0].name == "div":
                soup = children[0]
            else:
                break

        # 记录剥离前后的文本量，正文若因剥离 div 而缩水可从日志直接看出
        before = len(soup.get_text(" ", strip=True))
        stripped = BeautifulSoup(str(soup), "html.parser").find()
        # 正文表格也包在 div 里（如 /2026/11/16/phone-storage-full-quick-fixes/），
        # 先拆掉这层包装保留表格，再按 div 剥广告位
        for wrapper in stripped.find_all("div"):
            if wrapper.find("table") is not None:
                wrapper.unwrap()
        for element in stripped.select(STRIP_SELECTOR):
            element.decompose()
        after = len(stripped.get_text(" ", strip=True))

        if after == 0:
            # 该文正文整体嵌在 div 内，退回保守范围重剥一次
            stripped = soup
            for element in stripped.select(STRIP_SELECTOR_SAFE):
                element.decompose()
            after = len(stripped.get_text(" ", strip=True))
            if after == 0:
                util.error("article content empty after strip: {}".format(link))
                return "", ""
            util.info(
                "content text: {} -> {} chars (safe strip, body nested in div)".format(
                    before, after
                )
            )
        else:
            util.info("content text: {} -> {} chars".format(before, after))
        return str(stripped).strip(), parse_pub_date(body)
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return "", ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    try:
        response = request(list_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(list_url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error(
            "request url: {}, error: {}".format(list_url, status)
        )
        return

    soup = BeautifulSoup(response.text, "lxml")
    items = []
    for selector in LIST_SELECTORS:
        items = soup.select(selector)
        if items:
            break
    if not items:
        util.log_action_error(
            "request url: {}, no article node parsed".format(list_url)
        )
        return

    for item in items:
        if len(_new_articles) >= MAX_POSTS:
            break
        href = (item.get("href") or "").strip()
        title = item.get_text().strip()
        if not href or not title:
            continue
        if href in _links:
            util.info("exists link: {}".format(href))
            continue

        description, pub_date = get_detail(href)
        if description == "":
            continue

        _links.add(href)
        _new_articles.append(
            {
                "title": title,
                "description": description,
                "link": href,
                "pub_date": pub_date,
                "source": "rollingout",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
