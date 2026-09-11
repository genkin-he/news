# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点整站挂在 Cloudflare 托管质询后面（cf-mitigated: challenge），
# 首页 / RSS / wp-json / sitemap / api.invezz.com 全部 403。已验证 chrome131、
# chrome136、safari18_0、safari17_0、firefox133、edge101 六个档位表现一致，
# 故与 TLS 指纹无关，不做档位降级——那只会让被拒时的请求数翻倍。
# 香港出口与美国数据中心 IP 均被拦，能否通行取决于出口 IP。
IMPERSONATE = "chrome131"

base_url = "https://invezz.com/feed/"
filename = "./news/data/invezz/list.json"
util = SpiderUtil(notify=False)

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

def request(url):
    session = curl_requests.Session(impersonate=IMPERSONATE)
    response = session.get(url, timeout=TIMEOUT)
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
    """RSS pubDate 为 RFC 822，交给 email.utils 解析，比手写 strptime 更能容忍时区写法差异"""
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


def parse_description(item):
    """WordPress 源同时给 description（摘要）与 content:encoded（全文），优先取全文"""
    for tag in ("encoded", "description"):
        node = item.find(tag)
        if node is None:
            continue
        raw = node.get_text()
        if not raw or not raw.strip():
            continue
        soup = BeautifulSoup(raw, "lxml")
        for element in soup.select("script,style,iframe,noscript"):
            element.decompose()
        if not soup.get_text(strip=True):
            continue
        # RSS 里给的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
        return (soup.body.decode_contents() if soup.body else str(soup)).strip()
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
        description = parse_description(item)
        if not title or not link or not description:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "pub_date": parse_pub_date(item),
            }
        )
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
        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": item["description"],
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "invezz",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
