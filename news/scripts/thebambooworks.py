# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests
from util.spider_util import SpiderUtil

# 官网整站（含中文快讯 RSS 与详情页）自 2026-01 起被 Cloudflare 403 拦截；
# 2026-11-19 改经 Feedly 中转订阅英文主站 RSS。Feedly 上没有中文快讯 feed，
# 且只有约 800 字摘要、没有全文，这是目前唯一能稳定拿到的数据
source_feed = "https://thebambooworks.com/feed/"
feed_url = "https://cloud.feedly.com/v3/streams/contents?streamId={}&count=20".format(
    quote("feed/" + source_feed, safe="")
)
filename = "./news/data/thebambooworks/list.json"
util = SpiderUtil()

KEEP_POSTS = 10
LOCAL_TZ = timezone(timedelta(hours=8))
MIN_LENGTH = 200
# WordPress RSS 自动追加的来源尾巴，不属于正文
FOOTER_RE = re.compile(r"<p>\s*The post .*?appeared first on .*?</p>\s*$", re.S)

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
        description = FOOTER_RE.sub("", body).strip()
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
                "source": "bambooworks",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(_new_articles)))
    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
