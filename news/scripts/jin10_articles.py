# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
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
    "withcredentials": "true",
    "x-app-id": "arU9WZF7TC9m7nWn",
    "x-token": "",
    "x-version": "1.0.1",
    "cookie": "x-token=; UM_distinctid=19491510b37d7e-0b203753ab54c2-1e525636-1fa400-19491510b38ece; Hm_lvt_522b01156bb16b471a7e2e6422d272ba=1737604795; HMACCOUNT=01CA30120E05D033; did=ca7fcb5e-6d28-4789-98a0-b35e1085a5aa; env=prod; Hm_lpvt_522b01156bb16b471a7e2e6422d272ba=1737610599",
    "Referer": "https://xnews.jin10.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://xnews.jin10.com/"
filename = "./news/data/jin10/articles.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one(".setWebViewConentHeight > div")

        ad_elements = soup.select("ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = requests.get(
        "https://reference-api.jin10.com/reference?page_size=10&nav_bar_id=28",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["list"]
        for post in posts:
            if post["vip"] != 0 or post["type"] != "news" or post["original_article"] != 1:
                continue
            id = post["id"]
            title = post["title"].strip()
            link = "https://xnews.jin10.com/details/{}".format(post["id"])
            if len(post["web_thumbs"]) > 0:
                image = post["web_thumbs"][0]
            else:
                image = ""
            pub_date = post["display_datetime"]
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            
            description = get_detail(link)
            if description:
                insert = True
                articles.insert(
                    0,
                    {
                        "id": id,
                        "title": title,
                        "description": description,
                        "image": image,
                        "link": link,
                        "pub_date": pub_date,
                        "source": "jin10_articles_articles",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(
            f"request error: {response.status_code}"
        )

if __name__ == "__main__":
    util.execute_with_timeout(run)
