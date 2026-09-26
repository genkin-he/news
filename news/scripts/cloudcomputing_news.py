# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点（TechForge 旗下）在 Cloudflare 后面，用 curl_cffi 走指纹伪装；被拒时逐档降级，
# 命中的档位在本轮内缓存复用。
IMPERSONATE_PROFILES = ("chrome120", "safari18_0", "firefox133")

headers = {
    "accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}

base_url = "https://www.cloudcomputing-news.net"
feed_url = "https://www.cloudcomputing-news.net/feed/"
filename = "./news/data/cloudcomputing_news/list.json"

# feed 只用来拿标题、链接、作者与发布时间：它的 content:encoded 不是正文，而是
# 一段以 "[…]" 结尾的摘要，外加一句 "The post ... appeared first on ..." 的版权尾巴
# （线上实测首条仅 665 字符）。正文一律回详情页取。
# bs4 的 xml 解析器会剥掉命名空间前缀，故 dc:creator 按 creator 取。

# 详情页是 Elementor 模板，正文在 div.elementor-widget-container 里。该 class 在页面上
# 会出现很多次（每个 widget 一个），取文字最多的那个作为正文。
CONTENT_SELECTOR = "div.elementor-widget-container"
STRIP_SELECTOR = "figure,script,style,iframe,noscript,img,picture,source,form"
# 正文末尾固定三段推广：See also 链接、Cyber Security & Cloud Expo 的招商、
# "powered by TechForge Media"。段落数多于这个数量时才剥，避免把短稿清空。
TRAILING_PARAGRAPHS = 3

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 6
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；链内单次被拒记 info，整链耗尽才是失败"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        if response is not None and util.out_of_time():
            util.info("out of time, stop retrying: {}".format(url))
            break
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}".format(
                url, profile, response.status_code
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
    """RSS 的 pubDate 是 RFC 822，形如 Fri, 19 Sep 2026 10:12:33 +0000"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return util.current_time_string()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def get_detail(link):
    """详情页取正文：选文字最多的 elementor-widget-container，剥图，去掉末尾推广段"""
    util.info("link: {}".format(link))
    try:
        response = request(link)
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.error("request: {} error: {}".format(link, status))
        return ""

    body = BeautifulSoup(response.text, "lxml")
    candidates = body.select(CONTENT_SELECTOR)
    if not candidates:
        util.info("content not found, skipped: {}".format(link))
        return ""
    soup = max(candidates, key=lambda node: len(node.get_text(" ", strip=True)))

    for element in soup.select(STRIP_SELECTOR):
        element.decompose()

    paragraphs = soup.select("p")
    if len(paragraphs) > TRAILING_PARAGRAPHS:
        for paragraph in paragraphs[-TRAILING_PARAGRAPHS:]:
            paragraph.decompose()
    else:
        util.info(
            "only {} paragraphs, trailing promos kept: {}".format(
                len(paragraphs), link
            )
        )

    if not soup.get_text(strip=True):
        util.info("content empty after strip, skipped: {}".format(link))
        return ""
    util.info("content: {} chars".format(len(soup.get_text(" ", strip=True))))
    return str(soup).strip()


def parse_rss(xml_content):
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
        author_node = item.find("creator")
        items.append(
            {
                "title": title,
                "link": link,
                "author": author_node.get_text(strip=True) if author_node else "",
                "pub_date": parse_pub_date(item),
            }
        )
    return items


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(feed_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(feed_url, repr(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(feed_url, status))
        return

    entries = parse_rss(response.text)
    if not entries:
        util.log_action_error("request url: {}, no item parsed".format(feed_url))
        return
    util.info("{} items".format(len(entries)))

    for item in entries:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue
        description = get_detail(item["link"])
        if not description:
            continue
        links.add(item["link"])
        new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "author": item["author"] or "cloudcomputing_news",
                "pub_date": item["pub_date"],
                "source": "cloudcomputing_news",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
