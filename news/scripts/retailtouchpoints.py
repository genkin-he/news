# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests
from util.spider_util import SpiderUtil

# 官网整站（含 /feed）被 Cloudflare 以 403 拦截，浏览器 cookie 也绑 IP 无法复用；
# Feedly 能正常订阅它的 RSS 且带全文，经 Feedly 中转（2026-11-19 起）
source_feed = "https://www.retailtouchpoints.com/feed"
feed_url = "https://cloud.feedly.com/v3/streams/contents?streamId={}&count=20".format(
    quote("feed/" + source_feed, safe="")
)
filename = "./news/data/retailtouchpoints/list.json"
util = SpiderUtil()

KEEP_POSTS = 10
LOCAL_TZ = timezone(timedelta(hours=8))
# 正文末尾固定附带「Related stories」推荐列表，不属于正文
RELATED_RE = re.compile(r"<h\d[^>]*>\s*<strong>\s*Related stories:?\s*</strong>.*$", re.S | re.I)
MIN_LENGTH = 500

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "application/json",
}


def first_href(item, key):
    values = item.get(key) or []
    return values[0].get("href", "") if values else ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    response = requests.get(feed_url, headers=headers, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("feedly list error: {}".format(response.status_code))
        return

    for item in response.json().get("items", []):
        title = item.get("title", "").strip()
        link = first_href(item, "alternate")
        body = (item.get("content") or item.get("summary") or {}).get("content", "")
        if not title or not link or link in _links:
            continue
        description = RELATED_RE.sub("", body).strip()
        if len(description) < MIN_LENGTH:
            util.info("skip short: {}".format(link))
            continue
        _links.add(link)
        _new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "author": item.get("author", ""),
                "pub_date": datetime.fromtimestamp(item["published"] / 1000, LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "retailtouchpoints",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(_new_articles)))
    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
