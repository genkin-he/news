# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 后面，规则只盯 Chromium 系指纹：实测 chrome131 / chrome136 /
# chrome99_android / edge101 一律 403 + cf-mitigated: challenge，而 safari18_0 /
# safari17_0 / safari15_5 / firefox133 均返回 200。此处档位降级有实据（各档位结果不同），
# 与 electrive 那种"所有档位表现一致"的情形不同。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari15_5")

base_url = "https://www.asiafinancial.com/markets/feed"
filename = "./news/data/asiafinancial/list.json"
util = SpiderUtil()

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))
# feed 的 content:encoded 里含 figure / img / figcaption 与 div 包裹的插件块，需剥离
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript"

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
        session = curl_requests.Session(impersonate=profile)
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
    """只取 content:encoded（全文）；description 仅是约 400 余字符的摘要，不作回落"""
    node = item.find("encoded")
    if node is None:
        return ""
    raw = node.get_text()
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

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        blocked = response.headers.get("cf-mitigated") if response is not None else None
        util.log_action_error(
            "request url: {}, error: {}, cf-mitigated: {}".format(link, status, blocked)
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
        util.info("link: {}".format(item["link"]))
        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": item["description"],
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "asiafinancial",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
