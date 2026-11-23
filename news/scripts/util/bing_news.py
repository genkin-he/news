# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

# 官网被 Cloudflare 人机验证拦截，改由 Bing News 的公开 RSS 中转；
# 详情页同样被拦，正文只能用 Bing 给的摘要
BING_NEWS_RSS = "https://www.bing.com/news/search?q=site%3a{site}&format=rss&setlang=en"
LOCAL_TZ = timezone(timedelta(hours=8))
KEEP_POSTS = 30

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}


def unwrap_link(link):
    """Bing 的 link 是带随机 tid 的跳转地址，每次请求都不同，必须还原成原文地址才能去重"""
    target = parse_qs(urlparse(link).query).get("url", [""])[0]
    return target or link


def parse_pub_date(util, item):
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


def collect(util, site, link_prefix, source, filename):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    response = requests.get(
        BING_NEWS_RSS.format(site=site),
        headers=headers,
        timeout=util.request_timeout(5),
    )
    if response.status_code != 200:
        util.log_action_error("list error: {}".format(response.status_code))
        return

    soup = BeautifulSoup(response.content, "xml")
    for item in soup.find_all("item"):
        title_node = item.find("title")
        link_node = item.find("link")
        desc_node = item.find("description")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = unwrap_link(link_node.get_text(strip=True))
        description = desc_node.get_text(strip=True) if desc_node else ""
        # Bing 偶尔混入转载站或站内非文章页，只留原站文章
        if not title or not description or not link.startswith(link_prefix):
            continue
        if link in _links:
            continue
        _links.add(link)
        _new_articles.append(
            {
                "title": title,
                "description": "<p>{}</p>".format(description),
                "link": link,
                "pub_date": parse_pub_date(util, item),
                "source": source,
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(_new_articles)))
    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)
