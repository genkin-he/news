# -*- coding: UTF-8 -*-
import time
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 后面，规则只盯 Chromium 系指纹：chrome131 对两个 feed 均返回
# 403，而 safari18_0 返回 200。档位链在此有实据（各档位结果不同）。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari15_5")

# 两个分类 feed，各取前 MAX_PER_CATEGORY 条。同一篇文章可能同时出现在两个分类里
# （实测 item 带多个 category，如同时含 LATEST 与 Technology），已入库的链接集合在整轮内
# 共享，故跨 feed 不会重复收录。
CATEGORY_FEEDS = (
    ("technology", "https://evcentral.com.au/category/technology/feed/"),
    ("news", "https://evcentral.com.au/category/news/feed/"),
)

filename = "./news/data/evcentral/list.json"
util = SpiderUtil()

# content:encoded 为全文（实测纯文本 3481-8603 字符）；description 仅 414-531 字符的摘要，
# 不作回落。正文含 28 处 figure/img 配图与 figcaption 说明，无 div 与 script。
STRIP_SELECTOR = "figure,img,picture,script,style,iframe,noscript"

MAX_PER_CATEGORY = 2
KEEP_POSTS = 10
TIMEOUT = 6
REQUEST_GAP_SECONDS = 0.5
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；链内单次被拒记 info，整链耗尽才是失败"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile)
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
            )
        )
    util.error(
        "request url: {}, all {} impersonate profiles rejected, last error: {}".format(
            url,
            len(IMPERSONATE_PROFILES),
            response.status_code if response is not None else "no response",
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


def parse_description(item):
    """只取 content:encoded（全文）；description 是摘要，不作回落"""
    node = item.find("encoded")
    raw = node.get_text() if node else ""
    if not raw or not raw.strip():
        return ""
    soup = BeautifulSoup(raw, "lxml")
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()
    if not soup.get_text(strip=True):
        return ""
    # RSS 里给的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


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


def collect(name, url, links, new_articles):
    try:
        response = request(url)
    except Exception as e:
        util.error("request {} exception: {}".format(url, str(e)))
        return

    if response is None or response.status_code != 200:
        return

    items = parse_rss_xml(response.text)
    if not items:
        util.error("request url: {}, no rss item parsed".format(url))
        return
    util.info("{}: {} items".format(name, len(items)))

    for item in items[:MAX_PER_CATEGORY]:
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue
        util.info("link: {}".format(item["link"]))
        links.add(item["link"])
        new_articles.append(
            {
                "title": item["title"],
                "description": item["description"],
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "evcentral",
                "kind": 1,
                "language": "en",
            }
        )


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    for index, (name, url) in enumerate(CATEGORY_FEEDS):
        if index:
            time.sleep(REQUEST_GAP_SECONDS)
        if util.out_of_time():
            util.info("out of budget, stop before {}".format(name))
            break
        collect(name, url, links, new_articles)

    if not new_articles:
        return

    # 两个 feed 各自有序，合并后按发布时间倒序，保证最新的排最前
    new_articles.sort(key=lambda item: item["pub_date"], reverse=True)
    util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
