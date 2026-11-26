# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 原列表接口 apibs.business-standard.com 需要前端混淆过的 listData 参数，已返回 400；
# 改读官方 RSS（2026-11-19），详情页结构未变，仍取 #parent_top_div
feed_url = "https://www.business-standard.com/rss/latest.rss"
filename = "./news/data/businessstandard/list.json"
util = SpiderUtil()

KEEP_POSTS = 10
MAX_NEW_PER_RUN = 3
LOCAL_TZ = timezone(timedelta(hours=8))
NOISE_SELECTOR = ".storyadsprg, .recommendsection, .mb-20 > style, script"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
}


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("detail error: {}, link: {}".format(response.status_code, link))
        return ""
    content = BeautifulSoup(response.text, "lxml").select_one("#parent_top_div")
    if content is None:
        util.log_action_error("#parent_top_div not found: {}".format(link))
        return ""
    for element in content.select(NOISE_SELECTOR):
        element.decompose()
    return str(content).strip()


def format_pub_date(raw):
    try:
        return parsedate_to_datetime(raw).astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return util.current_time_string()


def first_image(item):
    for element in item:
        if element.tag.endswith("content") or element.tag.endswith("thumbnail"):
            if element.get("url"):
                return element.get("url")
    return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    response = requests.get(feed_url, headers=headers, timeout=util.request_timeout(5))
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
                "image": first_image(item),
                "pub_date": format_pub_date(item.findtext("pubDate")),
                "source": "business-standard",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(new_articles)))
    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
