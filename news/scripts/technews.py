# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "Accept-Language": 'zh-CN,zh;q=0.9',
    "Cache-Control": 'max-age=0',
    "Connection": 'keep-alive',
    "Sec-Fetch-Dest": 'document',
    "Sec-Fetch-Mode": 'navigate',
    "Sec-Fetch-Site": 'none',
    "Sec-Fetch-User": '?1',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "cookie": 'tn_guest=1; _ga=GA1.1.1759613940.1762919340; _ss_pp_id=5095a21c8a3172757561762890743776; __htid=42efdbce-815f-4668-a71d-e178cd6058d4; _fbp=fb.2.1762919545634.1014785011; _ht_hi=1; _ht_f3244e=1; __gads=ID=f89ebc92fbc27026:T=1762919342:RT=1762933022:S=ALNI_Ma7JZ0ZYBgsI_ypvB5e8BA2ia4aAQ; __gpi=UID=000011b3e84117d2:T=1762919342:RT=1762933022:S=ALNI_MbqjFFCyTgkWM4yBv67bLp9hVv0qw; __eoi=ID=6a475d38d4fb4090:T=1762919342:RT=1762933022:S=AA-AfjYu8M-5JDyw1ec4zYWAeQJ3; _ga_6Z0DEQZ51Y=GS2.1.s1762933022$o3$g0$t1762933022$j60$l0$h0; _td=c5ddffa5-af0a-4bef-92a0-22b6cfb0b91d; truvid_protected={"val":"f","level":0,"geo":"HK","timestamp":1762933025}',
}

base_url = "https://technews.tw"
filename = "./news/data/technews/list.json"
current_links = []
util = SpiderUtil()

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。原实现两处 requests
# 都没设 timeout（默认无限等待），站点一慢就把整轮拖到被外层强杀且零产出。
REQUEST_TIMEOUT = (3, 5)  # (connect, read)；再由 request_timeout 按剩余预算收敛

MAX_POSTS = 5
KEEP_POSTS = 10


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = requests.get(
            link, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        body = BeautifulSoup(resp, "lxml",from_encoding=response.encoding)
        # 子站点模板不统一：ccc.technews.tw 的文章没有 div.indent（CI 日志里每轮都
        # 卡在同一篇 ccc 稿件上）。原实现直接对 select_one 的结果调 .select()，
        # 返回 None 就抛 AttributeError 并中断整轮，把同批次其余文章一并丢掉。
        soup = body.select_one("div.indent")
        if soup is None:
            util.info("content not found, skipped: {}".format(link))
            return ""

        ad_elements = soup.select("script,style,div")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # 使用 requests 发送请求
    try:
        response = requests.get(
            "https://technews.tw/",
            headers=headers,
            timeout=util.request_timeout(REQUEST_TIMEOUT),
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml", from_encoding=response.encoding)
        items = soup.select("article h1.entry-title a")
        # 原实现 data_index 先自增再 insert(data_index, ...)，最新一篇最早插到下标 1，
        # 下标 0 的那条永远轮不到被挤掉——列表首位一直挂着 2025-11-12 的旧稿。
        # 改为新文章整体拼在旧列表前面。
        new_articles = []
        for item in items:
            if len(new_articles) >= MAX_POSTS or util.out_of_time():
                break
            link = item["href"].strip()
            title = item.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                new_articles.append(
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "cmcmarkets",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if insert:
            util.write_json_to_file(
                (new_articles + _articles)[:KEEP_POSTS],
                filename,
                encoding=response.encoding,
            )
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
