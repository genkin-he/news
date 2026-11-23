# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

import requests  # 发送请求
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}

# business 频道 RSS 覆盖 economy / companies-markets / banking / invest 等全部子栏目，
# 但也混有 /singapore/jobs 等非财经内容，只保留 /business/ 下的链接
rss_url = "https://www.straitstimes.com/news/business/rss.xml"
link_prefix = "https://www.straitstimes.com/business/"
filename = "./news/data/straitstimes/list.json"
util = SpiderUtil()

MAX_POSTS = 5
KEEP_POSTS = 30
LOCAL_TZ = timezone(timedelta(hours=8))


def parse_pub_date(item):
    """RSS pubDate 为 RFC 822（如 Mon, 09 Nov 2026 16:58:42 +0800）"""
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


def get_detail(link):
    """RSS 的 description 只有一句摘要，正文仍需抓详情页"""
    util.info("link: {}".format(link))
    try:
        response = requests.get(
            link, headers=headers, timeout=util.request_timeout(5)
        )
        if response.status_code != 200:
            util.error("detail: {} error: {}".format(link, response.status_code))
            return ""
        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(".storyline-wrapper")
        if soup is None:
            util.error("detail: {} storyline-wrapper not found".format(link))
            return ""

        # 移除样式、脚本与广告等 div 包裹块
        for element in soup.select("style, script, div"):
            element.decompose()

        return str(soup).strip()
    except Exception as e:
        util.error("detail: {} exception: {}".format(link, str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    response = requests.get(
        rss_url, headers=headers, timeout=util.request_timeout(5)
    )
    if response.status_code != 200:
        util.log_action_error("list error: {}".format(response.status_code))
        return

    soup = BeautifulSoup(response.content, "xml")
    for item in soup.find_all("item"):
        if len(_new_articles) >= MAX_POSTS or util.out_of_time():
            break
        title_node = item.find("title")
        link_node = item.find("link")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = link_node.get_text(strip=True)
        if not title or not link.startswith(link_prefix):
            continue
        if link in _links:
            util.info("exists link: {}".format(link))
            continue

        description = get_detail(link)
        if description:
            _links.add(link)
            _new_articles.append(
                {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": parse_pub_date(item),
                    "source": "straitstimes",
                    "kind": 1,
                    "language": "en",
                }
            )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
