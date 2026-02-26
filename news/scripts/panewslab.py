# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "theme-mode=light; _ga=GA1.1.1591991107.1745806348; _ga_KHBYDL8DMV=GS1.1.1745806348.1.1.1745807260.0.0.0",
    "Referer": "https://www.panewslab.com/",
    "Referrer-Policy": "same-origin",
}
base_url = "https://www.panewslab.com/"
filename = "./news/data/panewslab/list.json"
util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = requests.get(
        "https://www.panewslab.com/webapi/flashnews?LId=1&LastTime=0&Rn=10",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["flashNews"][0]["list"]
        for index, post in enumerate(posts):
            if index < 4:
                id = post["id"]
                link = "https://www.panewslab.com/zh/sqarticledetails/{}.html".format(
                    id
                )
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                title = post["title"].strip()
                pub_date = util.convert_utc_to_local(post["publishTime"])
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
                            "source": "panewslab",
                            "kind": 2,
                            "language": "zh-CN",
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
