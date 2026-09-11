# -*- coding: UTF-8 -*-
from datetime import datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 列表仍走站点的 Algolia 索引（本机实测 200，返回 20 条）；正文改为回详情页取 div.content
# ——索引里的 subhead 只是约 137 字符的一句副标题，不是正文。
#
# 详情页在 Cloudflare 托管质询后面：本机出口下 chrome131/136、safari15_5/17_0/18_0、
# firefox133、edge101 七个档位一律 403 + cf-mitigated: challenge，故无法本地验证。
# 与 electrive 同一模式（API/feed 放行、文章页被拦），而 electrive 在补齐扩展 client hints
# 后详情页转为可取，故此处照用同一份完整请求头。
IMPERSONATE = "chrome136"

ALGOLIA_URL = (
    "https://rsx8q1fola-dsn.algolia.net/1/indexes/*/queries"
    "?x-algolia-agent=Algolia%20for%20JavaScript%20(4.18.0)"
    "&x-algolia-api-key=62bbeeff0c155050d813eec2f8bb0b36"
    "&x-algolia-application-id=RSX8Q1FOLA"
)
ALGOLIA_PAYLOAD = {
    "requests": [
        {
            "indexName": "wp_searchable_posts_genre",
            "params": (
                "facetingAfterDistinct=true"
                "&facets=%5B%22genre%22%2C%22taxonomies.vertical%22%5D"
                "&filters=taxonomies.genre%3A'News'"
                "&highlightPostTag=__%2Fais-highlight__"
                "&highlightPreTag=__ais-highlight__"
                "&maxValuesPerFacet=50&page=0&query=&tagFilters="
            ),
        }
    ]
}

api_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "Referer": "https://www.digitalcommerce360.com/type/news/",
}

# 完整扩展 client hints —— Cloudflare 会检查其完整性
page_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"142.0.7444.176"',
    "sec-ch-ua-full-version-list": '"Chromium";v="142.0.7444.176", "Google Chrome";v="142.0.7444.176", "Not_A Brand";v="99.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

base_url = "https://www.digitalcommerce360.com/"
filename = "./news/data/digitalcommerce360/list.json"

CONTENT_SELECTOR = "div.content"
# 正文里的 div 多为版式与推广容器；但多个站点上已见到「正文整体嵌在 div 内」的情形
# （worldpharmaceuticals 会被清成 0，rollingout 有个别文章如此），故剥离后为空时退回保守范围
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript"
STRIP_SELECTOR_SAFE = "figure,script,style,iframe,noscript"

MAX_POSTS = 3
KEEP_POSTS = 5
TIMEOUT = 15

_session = None


def get_session():
    """列表与详情共用一个 session，质询通过后的 cookie 才能复用"""
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


def get_detail(link):
    """索引里的 subhead 只是副标题，正文回详情页取 div.content"""
    util.info("link: {}".format(link))
    try:
        response = get_session().get(link, headers=page_headers, timeout=TIMEOUT)
        if response.status_code != 200:
            util.error(
                "request: {} error: {}, cf-mitigated: {}".format(
                    link, response.status_code, response.headers.get("cf-mitigated")
                )
            )
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        before = len(soup.get_text(" ", strip=True))
        stripped = BeautifulSoup(str(soup), "lxml").select_one(CONTENT_SELECTOR)
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
                return ""
            util.info("content text: {} -> {} chars (safe strip)".format(before, after))
        else:
            util.info("content text: {} -> {} chars".format(before, after))
        return str(stripped).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = get_session().post(
            ALGOLIA_URL, json=ALGOLIA_PAYLOAD, headers=api_headers, timeout=TIMEOUT
        )
    except Exception as e:
        util.log_action_error("request algolia exception: {}".format(str(e)))
        return

    if response.status_code != 200:
        util.log_action_error("request error: {}".format(response.status_code))
        return

    try:
        posts = response.json()["results"][0]["hits"]
    except (ValueError, KeyError, IndexError) as e:
        util.log_action_error("bad algolia payload: {}".format(str(e)))
        return

    if not posts:
        util.log_action_error("no hit in algolia payload")
        return
    util.info("{} hits".format(len(posts)))

    for post in posts:
        if len(new_articles) >= MAX_POSTS:
            break

        link = (post.get("permalink") or "").strip()
        title = (post.get("post_title") or "").strip()
        if not link or not title:
            continue
        # 原实现此处用 break，遇到第一条已入库的文章就整轮停止；应为 continue
        if link in links:
            util.info("exists link: {}".format(link))
            continue

        description = get_detail(link)
        if description == "":
            continue

        try:
            pub_date = datetime.fromtimestamp(post["post_date"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except (KeyError, TypeError, ValueError, OSError):
            pub_date = util.current_time_string()

        links.add(link)
        new_articles.append(
            {
                "id": post.get("post_id", ""),
                "title": title,
                "description": description,
                "link": link,
                "pub_date": pub_date,
                "source": "digitalcommerce360",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
