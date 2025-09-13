# -*- coding: UTF-8 -*-

import logging
import traceback
import requests  # 发送请求
import json
import re
import time
from util.spider_util import SpiderUtil


headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "_pcc": "guV94wJgrAT+YgsDlvoI2JE/o6harvDGJ09NSk6LK1HQ+UZ7/32FW/JMEhM8KIYEh8CUN7Yjrq2/zVgvx0RZWB5899VzMqQ2fMDdO2goZsRFnAv3zJPlNA1BBNNAMZYOizGspbzOx12lZvd1eSsn620OANRHWnFfkcfuy2ToMVg=",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-fetch-storage-access": "active",
    "site-channel": "001",
    "t": "",
    "Referer": "https://www.fx168news.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/info.json"
util = SpiderUtil()


def get_detail(id):
    util.info("link: {}".format(id))
    url = "https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsDetail?newsId={}".format(
        id
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        body = response.json()["data"]["newsContent"]
        return body


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    url = "https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsByChannel?pageNo=1&pageSize=10&channelCodes=001001"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()["data"]["items"]
        for index in range(len(result)):
            if index < 1:
                id = result[index]["newsId"]
                url_code = result[index]["urlCode"]
                link = "https://www.fx168news.com/article/{}".format(url_code)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
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
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
