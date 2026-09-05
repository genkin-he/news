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
util = SpiderUtil(notify=False)

LIST_SELECTOR = "h3.elementor-post__title a"
# 详情页有两种正文容器，按顺序尝试
CONTENT_SELECTORS = ("div.standard-markdown", "div.elementor-widget-theme-post-content")
# 正文里的 div 都是 Elementor 的包装层与广告位；实测剥离 31 个 div 仅损失 64 字符
STRIP_SELECTOR = "script,style,iframe,noscript,div"

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
        util.error(
            "request url: {}, impersonate: {}, error: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
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
        for selector in CONTENT_SELECTORS:
            soup = body.select_one(selector)
            if soup is not None:
                break
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""

        # 记录剥离前后的文本量，正文若因剥离 div 而大幅缩水可从日志直接看出
        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return "", ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip(), parse_pub_date(body)
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
    items = soup.select(LIST_SELECTOR)
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
