# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone

import requests
from util.spider_util import SpiderUtil

# 官网被 Cloudflare 人机验证拦截，Feedly 能正常订阅它的 RSS，经 Feedly 中转拿全文
feed_url = "https://cloud.feedly.com/v3/streams/contents?streamId=feed/https://www.thesmartinvestor.com.sg/feed/&count=20"
filename = "./news/data/thesmartinvestor/list.json"
util = SpiderUtil()

KEEP_POSTS = 30
LOCAL_TZ = timezone(timedelta(hours=8))
# 付费文章在 RSS 里只剩一句登录提示（约 35 个词），入库就是空壳
PAYWALL_MARK = "Please log in to access our premium content"
MIN_WORDS = 200
# WordPress RSS 自动追加的来源尾巴，不属于正文
FOOTER_RE = re.compile(r"<p>\s*The post .*?appeared first on .*?</p>\s*$", re.S)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "application/json",
}


def word_count(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


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
        util.log_action_error("list error: {}".format(response.status_code))
        return

    for item in response.json().get("items", []):
        title = item.get("title", "").strip()
        # 链接保持 Feedly 原样（带 utm 参数），与此前直连 Feedly 时入库的 uuid 一致，切换时不会重复入库
        link = first_href(item, "alternate")
        body = (item.get("content") or item.get("summary") or {}).get("content", "")
        if not title or not link or link in _links:
            continue
        if PAYWALL_MARK in body or word_count(body) < MIN_WORDS:
            util.info("skip paywall/short: {}".format(link))
            continue
        _links.add(link)
        _new_articles.append(
            {
                "title": title,
                "description": FOOTER_RE.sub("", body).strip(),
                "link": link,
                "cover": first_href(item, "enclosure"),
                "author": item.get("author", ""),
                "pub_date": datetime.fromtimestamp(item["published"] / 1000, LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "thesmartinvestor",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(_new_articles)))
    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
