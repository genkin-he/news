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
    "_pcc": "AADasurSp4vqPth+GkI9ag6ZR4d/6dejiH/1xPmehwRpOso4cEJncyludfZXhaKi2L1pKNUfjv3jF1NMavxp08bHLtA8nGxwKYd1WCCxxLvnQfcLEQAHt0hsGyNIJJYQlNi4OutOHXLS5A0KGWecHUBc+mtGpS9oZmt0NbrFxUY=",
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
    "Referer": "https://www.fx168news.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/live.json"
util = SpiderUtil()


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    url = "https://centerapi.fx168api.com/cms/api/cmsFastNews/fastNews/getList?fastChannelId=001&pageNo=1&pageSize=20&appCategory=web&direct=down"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()["data"]["items"]
        for index in range(len(result)):
            if index < 5:
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
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)

    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
