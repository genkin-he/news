# -*- coding: UTF-8 -*-
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

# 原实现请求 https://api.investinglive.com/api/articles/get-all-news —— 该主机已是
# NXDOMAIN，CI 日志里表现为 URLError(gaierror(8, 'nodename nor servname provided'))，
# 并非 403。正文原本另取 S3 上的
# fmpedia-forexlive-prod.s3.amazonaws.com/investing-articles/{id}.json，
# 现在站点自己的 /api/public-articles 已在 expandedContent 里直接给出全文，
# 一个端点即可，S3 那一跳连同其 deviceid / CORS 请求头一并去掉。
headers = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://investinglive.com/live-feed/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}

base_url = "https://investinglive.com"
list_url = "https://investinglive.com/api/public-articles?first=12&skip=0&projection=forexlive-widget"
filename = "./news/data/investinglive/list.json"
util = SpiderUtil()

MAX_POSTS = 5
KEEP_POSTS = 20
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))
# publishedUtc 的小数秒是 7 位（如 2026-09-04T08:00:16.0233757Z），strptime 的 %f
# 最多只认 6 位，原实现的 "%Y-%m-%dT%H:%M:%S.%fZ" 在这种值上会直接失败，故只取到秒。
UTC_SECONDS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")


def parse_pub_date(value):
    matched = UTC_SECONDS.match(value or "")
    if not matched:
        return util.current_time_string()
    try:
        parsed = datetime.strptime(matched.group(1), "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return util.current_time_string()
    return (
        parsed.replace(tzinfo=timezone.utc)
        .astimezone(LOCAL_TZ)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def clean_content(html):
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "lxml")
    for element in soup.select("script,style,iframe,noscript,figure"):
        element.decompose()
    if not soup.get_text(strip=True):
        return ""
    # lxml 会为 HTML 片段补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}, body: {}".format(
                url, response.status_code, (response.text or "").strip()[:120]
            )
        )
        return

    try:
        posts = json.loads(response.text)["articles"]
    except (ValueError, KeyError) as e:
        util.log_action_error("request url: {}, bad payload: {}".format(url, str(e)))
        return

    if not posts:
        util.log_action_error("request url: {}, no article in payload".format(url))
        return

    for post in posts:
        if len(new_articles) >= MAX_POSTS:
            break

        path = (post.get("path") or "").strip()
        title = (post.get("displayText") or "").strip()
        if not path or not title:
            continue

        link = urljoin(base_url + "/", path)
        if link in links:
            util.info("exists link: {}".format(link))
            continue

        description = clean_content(post.get("expandedContent"))
        if description == "":
            util.error("empty content: {}".format(link))
            continue

        util.info("link: {}".format(link))
        links.add(link)
        new_articles.append(
            {
                "id": post.get("contentItemId", ""),
                "title": title,
                "description": description,
                "link": link,
                "pub_date": parse_pub_date(post.get("publishedUtc")),
                "source": "investinglive",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, list_url)
