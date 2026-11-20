# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests
from util.spider_util import SpiderUtil

# 原列表页 /blog 已 404，改读官方 RSS（2026-11-19）。RSS 只有一句摘要，正文仍从详情页取；
# 普通 requests 会被 403，必须用 curl_cffi 模拟浏览器指纹
feed_url = "https://talkmarkets.com/rss"
filename = "./news/data/talkmarkets/list.json"
util = SpiderUtil()

KEEP_POSTS = 40
MAX_NEW_PER_RUN = 3
LOCAL_TZ = timezone(timedelta(hours=8))
IMPERSONATE = "chrome"
NOISE_SELECTOR = "script, style, iframe, noscript, div"


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, impersonate=IMPERSONATE, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("detail error: {}, link: {}".format(response.status_code, link))
        return ""
    content = BeautifulSoup(response.text, "lxml").select_one("div.article-body")
    if content is None:
        util.log_action_error("article-body not found: {}".format(link))
        return ""
    for element in content.select(NOISE_SELECTOR):
        element.decompose()
    return str(content).replace("\n", "").replace("\r", "").strip()


def format_pub_date(raw):
    try:
        return parsedate_to_datetime(raw).astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return util.current_time_string()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    response = requests.get(feed_url, impersonate=IMPERSONATE, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("rss error: {}".format(response.status_code))
        return

    for item in ET.fromstring(response.content).findall(".//item"):
        if len(new_articles) >= MAX_NEW_PER_RUN or util.out_of_time():
            break
        link = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        if not link or not title or link in links:
            continue
        description = get_detail(link)
        if not description:
            continue
        links.add(link)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "author": (item.findtext("author") or "").strip(),
                "pub_date": format_pub_date(item.findtext("pubDate")),
                "source": "talkmarkets",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(new_articles)))
    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
