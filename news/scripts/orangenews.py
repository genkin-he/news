# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "cookie": '_gid=GA1.2.1106022777.1757559020; _ga=GA1.1.216479998.1757559011; acw_tc=2ff6269617575889780922903ec8a3d8af24df7839cfa3b61fb2ee15c1; cdn_sec_tc=2ff6269617575889780922903ec8a3d8af24df7839cfa3b61fb2ee15c1; _ga_1T11XM47PP=GS2.1.s1757588567$o2$g1$t1757589046$j60$l0$h0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

base_url = "https://www.orangenews.hk"
filename = "./news/data/orangenews/list.json"
current_links = []
util = SpiderUtil()

def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    response = requests.get(
        link, headers=headers
    )
    if response.status_code == 200:
        body = response.text
        json_data = json.loads(body)
        items = json_data["data"]["records"]
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 4:
                break
            a = items[index]
            link = a["detailsUrl"].strip()
            title = a["title"].strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = a["txt"]
            # Remove content before and including【橙訊】
            if description:
                # Find the position of【橙訊】and remove everything before it (including【橙訊】)
                orange_news_pattern = r'.*?【橙訊】'
                description = re.sub(orange_news_pattern, '', description, flags=re.DOTALL)
                description = description.strip()

            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "orangenews",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://apps.orangenews.hk/app/bus/tag/news/common/pageList?handlerName=contentTagPageListHandler&page=1&limit=12&params=%7B%22tagId%22%3A%22126%22%2C%22requestType%22%3A%22IOS%22%7D")
