# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests
from util.spider_util import SpiderUtil

# 时代财经（time-weekly）与时代周报（time-weekly-app），同属时代传媒，均提供带全文的 RSS。
# 原先由 news-crawler（prod-hk-ack-1）直连采集，2026-10-30 起两个 RSS 在该集群都拿不到
# 响应（news-crawler 会把带 "Not Found" 的错误静默吞掉，日志里只有 Visiting），故迁到这里。
# 源 -> 该源的全部 RSS（与 CMS 里原来的种子一一对应），合并写进同一份 JSON
FEEDS = (
    ("time-weekly", ("https://www.tfcaijing.com/rss.xml?cid=original",)),
    (
        "time-weekly-app",
        (
            "https://app-rss.time-weekly.com/rss.xml",
            # timetank：「影响有影响力的人」栏目
            "https://app-rss.time-weekly.com/timetank.xml",
        ),
    ),
)
# 两个源出稿不算密，不需要每轮（CI 约 2~4 分钟一轮）都抓
RUN_INTERVAL_SECONDS = 15 * 60
REQUEST_TIMEOUT = (3, 4)
# 主 RSS 一天就有约 50 条，按时间截断时要给 timetank 这类出稿慢的栏目留位置
KEEP_POSTS = 60
util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def parse_items(xml_text, source):
    """RSS 的 description 即全文 HTML；pubDate 带时区（+0800），转成秒级时间戳"""
    articles = []
    root = ET.fromstring(xml_text)
    for item in root.findall("./channel/item"):
        link = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or "").strip()
        if not link or not title or not description:
            continue
        pub_time = 0
        try:
            pub_time = int(parsedate_to_datetime(item.findtext("pubDate")).timestamp())
        except Exception:
            pass
        articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "author": (item.findtext("author") or "").strip(),
                "pub_time": pub_time,
                "pub_date": util.convert_utc_to_local(pub_time)
                if pub_time
                else util.current_time_string(),
                "source": source,
                "kind": 1,
                "language": "zh-CN",
            }
        )
    return articles


def fetch_feed(url, source):
    try:
        response = requests.get(
            url, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return []
    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(url, response.status_code)
        )
        return []
    try:
        articles = parse_items(response.content, source)
    except Exception as e:
        util.log_action_error("parse {} error: {}".format(url, str(e)))
        return []
    if not articles:
        util.log_action_error("request url: {}, no item parsed".format(url))
    return articles


def run():
    if not util.should_run_every(RUN_INTERVAL_SECONDS):
        return
    for source, urls in FEEDS:
        filename = "./news/data/{}/list.json".format(source)
        articles = []
        for url in urls:
            articles.extend(fetch_feed(url, source))
        if not articles:
            continue

        history = util.history_posts(filename)
        links = set(history["links"])
        new_articles = []
        for article in articles:
            if article["link"] in links:
                continue
            links.add(article["link"])
            new_articles.append(article)
        if not new_articles:
            util.info("{}: no new item".format(source))
            continue
        merged = sorted(
            new_articles + history["articles"],
            key=lambda x: int(x.get("pub_time") or 0),
            reverse=True,
        )
        util.write_json_to_file(merged[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
