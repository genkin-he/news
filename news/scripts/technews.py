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


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        body = BeautifulSoup(resp, "lxml",from_encoding=response.encoding)
        soup = body.select_one("div.indent")

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
    response = requests.get(
        "https://technews.tw/", headers=headers
    )
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml", from_encoding=response.encoding)
        items = soup.select("article h1.entry-title a")
        data_index = 0
        for item in items:
            if data_index > 4:
                break
            link = item["href"].strip()
            title = item.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                data_index += 1
                _articles.insert(
                    data_index,
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

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename, encoding=response.encoding)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
