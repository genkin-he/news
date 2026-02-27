# -*- coding: UTF-8 -*-

import logging
import traceback
import requests  # 发送请求
import json
import re
import time
from util.spider_util import SpiderUtil
from fx168_news_api import FX168NewsAPI
base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/live.json"
util = SpiderUtil()


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    api = FX168NewsAPI()
    response = api.get_json_by_url(
        url="https://centerapi.fx168api.com/cms/api/cmsFastNews/fastNews/getList", 
        params={
            "fastChannelId": "001",
            "pageNo": 1,
            "pageSize": 20,
            "appCategory": "web",
            "direct": "down"
        }, 
        pcc_value=None
    )
    
    if response:
        result = response["data"]["items"]
        for index in range(len(result)):
            if result[index]["isTop"] != 0:
                continue
            id = result[index]["fastNewsId"]
            link = "https://www.fx168news.com/express/fastnews/{}".format(id)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            pub_date = result[index]["publishTime"]
            description = result[index]["textContent"]
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": description,
                        "id": id,
                        "description": "",
                        "link": link,
                        "pub_date": pub_date,
                        "source": "fx168",
                        "kind": 2,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run)
