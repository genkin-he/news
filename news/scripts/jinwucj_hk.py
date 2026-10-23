# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "token": "fenlibao&8ef4863071d5284486cd18cd4d479125&1725962285328",
    "cookie": "Hm_lvt_8ddfa1ee949bd6f1115678cd8e9ec3d8=1725934911; HMACCOUNT=9DDE48DEBE88D1EC; Hm_lpvt_8ddfa1ee949bd6f1115678cd8e9ec3d8=1725962264",
    "Referer": "https://ipo.jinwucj.com/info",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://ipo.jinwucj.com/info"
filename = "./news/data/jinwucj/list_hk.json"
util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    data = {"pageNum": 1, "pageSize": 10}

    # 使用requests发送POST请求
    response = requests.post(
        "https://pro-app-sky-api.szfiu.com/news/v1/list", json=data, headers=headers
    )

    if response.status_code == 200:
        posts = response.json()["body"]["list"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["id"]
                title = post["title"]
                link = "https://sky.szfiu.com/info/hk/details/{}".format(id)
                pub_date = post["pubDate"]

                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break

                description = post["content"]
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
                            "source": "jinwucj",
                            "kind": 1,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
