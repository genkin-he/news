# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}

base_url = "https://www.marketpulse.com"
filename = "./news/data/marketpulse/list.json"
util = SpiderUtil(notify=False)

# 原实现只抓 /news/ai/、/markets/crypto/、/markets/stocks/、
# /markets/daily-market-wraps/ 四个子栏目，且每页只取前 3 条，因此漏掉了不属于这些栏目的
# 文章——例如外汇类（/markets/forex/ 本身已是 404）与商品类。
# 改抓两个聚合页：/markets/ 与 /news/。实测二者去重后共 24 条，且已覆盖原
# /news/ai/、/markets/crypto/、/markets/stocks/、/markets/commodities/ 的前 3 条。
# 未纳入 /markets/daily-market-wraps/：它不被聚合页覆盖，但内容已停更在 5 月
# （首条为 Memorial Day 相关），收进来只会用数月前的旧文挤掉新文。
LIST_URLS = (
    "https://www.marketpulse.com/markets/",
    "https://www.marketpulse.com/news/",
)
LIST_SELECTOR = "a.item-title"

CONTENT_SELECTOR = ".post-body"
# 沿用原实现的剥离范围。注意 .post-body 内有 44 个 div 承载版式，不能剥 div
STRIP_SELECTOR = (
    "link,script,style,.anchor-offset,.block-post_content_disclaimer"
)
# 详情页没有 article:published_time，发布时间在 JSON-LD 里
DATE_PATTERN = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))


def request(url):
    return requests.get(url, headers=headers, timeout=TIMEOUT)


def parse_pub_date(html):
    matched = DATE_PATTERN.search(html or "")
    if not matched:
        return util.current_time_string()
    try:
        return (
            datetime.fromisoformat(matched.group(1).replace("Z", "+00:00"))
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except ValueError:
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return "", ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""

        # 记录剥离前后的文本量：.post-body 里的 div 是版式容器，剥离范围一旦扩到 div
        # 就会伤到正文，日志可及时暴露
        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return "", ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip(), parse_pub_date(response.text)
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return "", ""


def collect_candidates():
    """两个聚合页合并，按出现顺序去重（页内也有重复，如 most-read 区块）"""
    candidates = []
    seen = set()
    for list_url in LIST_URLS:
        try:
            response = request(list_url)
        except Exception as e:
            util.error("request {} exception: {}".format(list_url, str(e)))
            continue

        if response.status_code != 200:
            util.error(
                "request url: {}, error: {}".format(list_url, response.status_code)
            )
            continue

        soup = BeautifulSoup(response.text, "lxml")
        nodes = soup.select(LIST_SELECTOR)
        added = 0
        for node in nodes:
            link = (node.get("href") or "").strip()
            title = node.get_text().strip()
            if not link or not title or link in seen:
                continue
            seen.add(link)
            candidates.append({"link": link, "title": title})
            added += 1
        util.info("{}: {} nodes, {} new".format(list_url, len(nodes), added))
    return candidates


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    candidates = collect_candidates()
    if not candidates:
        util.log_action_error("no article candidate on any list url")
        return

    for item in candidates:
        if len(_new_articles) >= MAX_POSTS:
            break
        if item["link"] in _links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description, pub_date = get_detail(item["link"])
        if description == "":
            continue

        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": pub_date,
                "source": "marketpulse",
                "kind": 1,
                "language": "en",
            }
        )

    if not _new_articles:
        return

    # 列表页顺序含 most-read 等非时间序区块，按解析出的发布时间倒序，保证最新的排最前
    _new_articles.sort(key=lambda item: item["pub_date"], reverse=True)
    util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
