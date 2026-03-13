# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://news.tvb.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://news.tvb.com"
filename = "./news/data/tvb/list.json"
util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = requests.get(
        "https://inews-api.tvb.com/news/entry/category?id=finance&mpmLimit=0&lang=sc&page=1&limit=10&country=HK",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.json()
        posts = body["content"]
        for index, post in enumerate(posts):
            if index < 4:
                id = post["id"]
                link = "https://news.tvb.com/sc/finance/{}".format(id)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                title = post["title"].strip()
                pub_date = util.current_time_string()
                description = post["desc"].strip()
                if description:
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "tvb",
                            "kind": 1,
                            "language": "zh-CN",
                        },
                    )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
