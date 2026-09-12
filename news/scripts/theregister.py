# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

base_url = "https://www.theregister.com"
filename = "./news/data/theregister/list.json"
util = SpiderUtil(notify=False)

MAX_POSTS = 5
KEEP_POSTS = 10
LOCAL_TZ = timezone(timedelta(hours=8))
# 页面上「4 hours ago」这类相对时间也占着 <time datetime>，只认 ISO 格式的那个
ISO_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T")


def parse_pub_date(soup):
    for node in soup.select("time[datetime]"):
        value = (node.get("datetime") or "").strip()
        if not ISO_TIME.match(value):
            continue
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            continue
        return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
    return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(
            link, headers=headers, timeout=10, proxies=util.get_random_proxy()
        )
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return "", ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one("div.bodytext")
        if not soup:
            util.error("article content not found: {}".format(link))
            return "", ""

        # bodytext 内的 div 全是相关文章框与广告位，正文实体是 p / h2
        for element in soup.select("script, style, iframe, noscript, div"):
            element.decompose()
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
        response = requests.get(
            base_url + "/", headers=headers, timeout=10, proxies=util.get_random_proxy()
        )
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))
        return

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(base_url, response.status_code)
        )
        return

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select("article")
    if not items:
        util.log_action_error("request url: {}, no article node parsed".format(base_url))
        return

    for item in items:
        if len(_new_articles) >= MAX_POSTS:
            break

        url_node = item.select_one('div.content a[itemprop="url"]')
        title_node = item.select_one("div.content a h2.headline")
        if url_node is None or title_node is None:
            continue
        href = (url_node.get("href") or "").strip()
        if not href:
            continue

        link = urljoin(base_url, href)
        if link in _links:
            util.info("exists link: {}".format(link))
            continue

        description, pub_date = get_detail(link)
        if description == "":
            continue

        _links.add(link)
        _new_articles.append(
            {
                "title": title_node.get_text().strip(),
                "description": description,
                "link": link,
                "pub_date": pub_date,
                "source": "theregister",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
