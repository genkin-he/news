# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import time
import traceback
import requests
import json

from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil
util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie": util.get_env_variable("tradingview_cookie", ''),
    "Referer": "https://www.tradingview.com/",
    "Referrer-Policy": "origin-when-cross-origin",
}

base_url = "https://www.tradingview.com/news-flow/?market=etf,forex,index,futures,bond,economic,crypto,stock&market_country=entire_world"
filename = "./news/data/tradingview/list.json"

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        soup = BeautifulSoup(resp, "lxml")
        soup = soup.select_one("article div[class*='body-']")

        symbol_links = soup.select("a[href*='/symbols/']")
        for link in symbol_links:
            link.decompose()

        return str(soup).encode("utf-8").decode("utf-8")
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 发送请求获取响应
    url = "https://news-mediator.tradingview.com/news-flow/v1/news?filter=lang%3Aen&streaming=true&time={}".format(int(time.time()))
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        body = response.text
        posts = json.loads(body)["items"]
        for index in range(len(posts)):
            post = posts[index]
            if index > 12:
                break
            storyPath = post["storyPath"]
            link = "https://www.tradingview.com{}".format(storyPath)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            id = post["id"]
            source = post["source"]
            title = post["title"]
            description = get_detail(link)
            pub_date = util.convert_utc_to_local(post["published"])
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "id": id,
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                        "source": source,
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 30:
                articles = articles[:30]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, timeout=15)
