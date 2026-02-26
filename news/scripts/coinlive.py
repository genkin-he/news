# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "accept": "*/*",
    "accept-language": "en",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://www.coinlive.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.coinlive.com/"
filename = "./news/data/coinlive/list.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = requests.get(
        "https://api.coinlive.com/api/v1/news-letter/list?page=1&size=10", headers=headers
    )
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["list"]
        for index, post in enumerate(posts):
            if index < 4:
                id = post["id"]
                title = post["title"].strip()
                link = post["url"]
                description = post["brief"].strip()
                pub_date = util.convert_utc_to_local(post["published_at"])
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
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
                            "source": "coinlive",
                            "kind": 2,
                            "language": "en",
                        },
                    )
        if articles and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
