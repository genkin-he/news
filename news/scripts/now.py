# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "_ga=GA1.1.1337123095.1733714167; _ga_PSJPX029ZD=GS1.1.1733714174.1.1.1733714184.50.0.0; __utma=262549139.1337123095.1733714167.1733714284.1733714284.1; __utmb=262549139.0.10.1733714284; __utmc=262549139; __utmz=262549139.1733714284.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=262549139.|1=deviceType=desktop=1; _ga_DGFECMB23C=GS1.1.1733714166.1.1.1733715785.60.0.1304140467; __utmt=1; __utma=262549139.1337123095.1733714167.1733714284.1733714284.1; __utmb=262549139.1.10.1733714284; __utmc=262549139; __utmz=262549139.1733714284.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=262549139.|1=deviceType=desktop=1",
    "Referer": "https://news.now.com/home/finance",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://news.now.com"
filename = "./news/data/now/list.json"
current_links = []
util = SpiderUtil(notify=False)

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers, timeout=8, proxies=util.get_random_proxy())
    if response.status_code == 200:
        body = response.text
        lxml = BeautifulSoup(body, "lxml")
        soup = lxml.select_one(".newsLeading")

        ad_elements = soup.select(".imagesCollection")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""

def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        # 使用 requests 替换 urllib
        response = requests.get(
            link, headers=headers, timeout=8, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            items = response.json()
            for index in range(len(items)):
                if index > 4:
                    break
                id = items[index]["newsId"]
                title = items[index]["title"]
                description = ""
                image = items[index]["imageUrl"]
                link = "https://news.now.com/home/technology/player?newsId={}".format(
                    id
                )
                description = get_detail(link)
                category = items[index]["categoryName"]
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    break
                if description != "":
                    insert = True
                    _articles.insert(
                        index,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "image": image,
                            "category": category,
                            "pub_date": util.current_time_string(),
                            "source": "now",
                            "kind": 1,
                            "language": "zh-HK",
                        },
                    )

            if len(_articles) > 0 and insert:
                if len(_articles) > 20:
                    _articles = _articles[:20]
                util.write_json_to_file(_articles, filename)
        else:
            util.log_action_error("now request error: {}".format(response.status_code))
    except requests.RequestException as e:
        util.log_action_error("request error: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(
        run, "https://newsapi1.now.com/pccw-news-api/api/getNewsListv2?category=121&pageSize=20&pageNo=1"
    )

    util.execute_with_timeout(
        run, "https://newsapi1.now.com/pccw-news-api/api/getNewsListv2?category=502&pageSize=20&pageNo=1"
    )
