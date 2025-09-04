# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import requests  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers_2 = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "expires": "0",
    "origin": "https://www.business-standard.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.business-standard.com/",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-access-token": "",
}

base_url = "https://www.business-standard.com"
filename = "./news/data/businessstandard/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers_2)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select("#parent_top_div")[0]

        ad_elements = soup.select(".storyadsprg,.recommendsection, .mb-20 > style")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    url = "https://apibs.business-standard.com/article/latest-news?limit=21&page=0&offset=0"
    response = requests.get(url, headers=headers_2)

    if response.status_code == 200:
        result = response.json()["data"]
        for index in range(len(result)):
            if index < 1:
                id = result[index]["article_id"]
                article_url = result[index]["article_url"]
                link = "https://www.business-standard.com{}".format(article_url)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                title = result[index]["heading1"]
                image = ""
                pub_date = result[index]["published_date"]
                # 将时间戳转换为日期格式
                if isinstance(pub_date, (int, str)):
                    try:
                        pub_date = int(pub_date)
                        from datetime import datetime
                        pub_date = datetime.fromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pub_date = str(pub_date)
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "id": id,
                            "description": description,
                            "link": link,
                            "image": image,
                            "pub_date": pub_date,
                            "source": "business-standard",
                            "kind": 1,
                            "language": "en",
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
