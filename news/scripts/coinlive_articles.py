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
    "Content-Type": "application/json",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US",
    "authorization": "null",
    "content-type": "application/json",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "x-device-id": "c8c2882a8dbcc714b202e0397e9e22ae",
    "x-platform": "PC",
    "x-project": "1",
    "x-zone": "8",
    "Referer": "https://www.coinlive.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.coinlive.com/"
filename = "./news/data/coinlive/articles.json"
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        detail = lxml.select_one("[class^=detail_html]")
        soup = detail.select_one("[class^=share__]")

        ad_elements = soup.select("[class^=share_container], [class^=ad_wrap]")
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

    body = {
        "symbols": [],
        "page": 1,
        "size": 10,
        "show_position": 2,
        "sort": "published_at",
    }

    # 使用 requests 发送请求
    response = requests.post(
        "https://api.coinlive.com/api/v1/news/list",
        headers=headers,
        data=bytes(json.dumps(data), encoding="utf8"),
    )
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["list"]
        for index, post in enumerate(posts):
            if index < 3:
                id = post["id"]
                title = post["title"].strip()
                link = "https://www.coinlive.com/news/{}".format(post["tid"])
                image = post["cover_img"]
                pub_date = util.convert_utc_to_local(post["published_at"])
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
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
                            "source": "coinlive_articles",
                            "kind": 1,
                            "language": "en",
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
