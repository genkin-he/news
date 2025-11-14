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
filename = "./news/data/fx168/info.json"
util = SpiderUtil()


def get_detail(id):
    util.info("link: {}".format(id))
    url = "https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsDetail"
    api = FX168NewsAPI()
    response = api.get_json_by_url(url, params={"newsId": id}, pcc_value=None)
    if response:
        body = response["data"]["newsContent"]
        return body


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    api = FX168NewsAPI()
    response = api.get_json_by_url(url="https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsByChannel", params={"pageNo": 1, "pageSize": 10, "channelCodes": "001001"}, pcc_value=None)
    if response:
        result = response["data"]["items"]
        for index in range(len(result)):
            id = result[index]["newsId"]
            url_code = result[index]["urlCode"]
            link = "https://www.fx168news.com/article/{}".format(url_code)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            title = result[index]["newsTitle"]
            image = result[index]["displayImage"]
            pub_date = result[index]["firstPublishTime"]
            description = get_detail(id)
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
                        "source": "fx168",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run)
