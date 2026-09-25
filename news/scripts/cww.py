# -*- coding: UTF-8 -*-
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Google Chrome";v="152", "Chromium";v="152", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}

base_url = "https://www.cww.net.cn"
# 原 /subjects/nav/rollList/{columnId} 列表页已被站方废弃：服务端渲染新闻列表时抛异常，
# 响应头已 flush 所以 GET 停在 200 但正文在 <div class="col-md-8 newslist"> 处截断（HEAD 可见 500）。
# 首页的「行业资讯」滚动块是同一份数据，改从这里取。
list_url = "https://www.cww.net.cn/index.jsp"
filename = "./news/data/cww/list.json"
util = SpiderUtil()

MAX_POSTS = 2
KEEP_POSTS = 10


def article_id(link):
    """历史数据里的链接是 http://，urljoin 产出的是 https://，按 id 去重才不会重复收录同一篇"""
    matched = re.search(r"[?&]id=(\d+)", link)
    return matched.group(1) if matched else link


def parse_pub_date(soup):
    """详情页的发布时间形如 2026.09.03 09:53，已是北京时间，不能再走 util.parse_time 的 +8"""
    for node in soup.select("span.introtit_fl"):
        text = node.get_text(strip=True)
        matched = re.search(r"\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}", text)
        if not matched:
            continue
        try:
            return datetime.strptime(matched.group(), "%Y.%m.%d %H:%M").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            break
    return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return "", ""

        response.encoding = "utf-8"
        lxml = BeautifulSoup(response.text, "lxml")
        soup = lxml.select_one("#divContentDiv")
        if soup is None:
            util.error("request: {} error: no #divContentDiv".format(link))
            return "", ""

        for element in soup.select("script,style"):
            element.decompose()

        return str(soup).strip(), parse_pub_date(lxml)
    except Exception as e:
        util.error("exception: {}".format(str(e)))
        return "", ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    seen_ids = {article_id(item) for item in data["links"]}
    insert = False

    try:
        response = requests.get(list_url, headers=headers, timeout=10)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(list_url, str(e)))
        return

    if response.status_code != 200:
        util.log_action_error("request error: {}".format(response.status_code))
        return

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "lxml")
    nodes = soup.select('.cwwsd a[href^="/article?id="]')
    if not nodes:
        util.log_action_error("request {}, no article node parsed".format(list_url))
        return

    for node in nodes[:MAX_POSTS]:
        link = urljoin(base_url, node["href"].strip())
        if article_id(link) in seen_ids:
            util.info("exists link: {}".format(link))
            continue
        title = node.get_text(strip=True)
        if not title:
            continue
        description, pub_date = get_detail(link)
        if description == "":
            continue
        insert = True
        seen_ids.add(article_id(link))
        articles.insert(
            0,
            {
                "title": title,
                "description": description,
                "pub_date": pub_date,
                "link": link,
                "source": "cww",
                "kind": 1,
                "language": "zh-CN",
            },
        )

    if insert and len(articles) > 0:
        util.write_json_to_file(articles[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
