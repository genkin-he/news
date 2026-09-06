# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 托管质询后面（cf-mitigated: challenge，正文 "Just a moment..."）。
# 已知会被拦的出口：香港共享代理、Anthropic 抓取器的美国数据中心 IP；chrome120/131/136、
# safari15_5/17_0/18_0、firefox133、edge101、chrome99_android 九档表现一致，与 TLS
# 指纹无关，故单档位不做降级；同 session 原地重试亦无效（只得 __cf_bm，拿不到
# cf_clearance）。GitHub Actions 的出口 IP 实测可以通过质询，故本采集器在 CI 可用。
IMPERSONATE = "chrome131"

# 列表走 https://ambcrypto.com/category/new-news/ 对应的 WordPress 分类 feed：
# 拿链接、标题与发布时间不必依赖任何 CSS 选择器。正文则回详情页取 .entry-content，
# 因为 feed 里的 description 只是摘要。
base_url = "https://ambcrypto.com/category/new-news/feed/"
filename = "./news/data/ambcrypto/list.json"
util = SpiderUtil(notify=False)

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def get_session():
    """列表与详情共用一个 session，Cloudflare 下发的 cookie 才能复用"""
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


def request(url):
    response = get_session().get(url, timeout=TIMEOUT)
    if response.status_code != 200:
        util.error(
            "request url: {}, error: {}, cf-mitigated: {}, body: {}".format(
                url,
                response.status_code,
                response.headers.get("cf-mitigated"),
                (response.text or "").replace("\n", " ")[:120],
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
        items.append(
            {"title": title, "link": link, "pub_date": parse_pub_date(item)}
        )
    return items


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(".entry-content")
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        for element in soup.select("script,style,iframe,noscript,div"):
            element.decompose()
        if not soup.get_text(strip=True):
            util.error("article content empty: {}".format(link))
            return ""
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


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
            "request url: {}, error: {}, cf-mitigated: {}".format(
                link, response.status_code, response.headers.get("cf-mitigated")
            )
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
                "source": "ambcrypto",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
