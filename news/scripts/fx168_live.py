# -*- coding: UTF-8 -*-

import logging
import urllib.request  # 发送请求
import json
import re
import time
from util.util import history_posts
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "_pcc": "dBoIC52Ioh64p7ckrGL8ryuwot1RPdSitM9BTNtaoNlVLhnLoFEaehJOn1SViYrf7lt303A4qjUUtDoSbcdlHdGioyU7N7igsoNKcge9yMAnxx+FzWsQQz5fcqsIAc/Yigj3leAEnYw/TGvC8v8C38tGRGFUQ9pGJ8BfWYQKDDo=",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "site-channel": "001",
    "t": "",
    "Referer": "https://www.fx168news.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/live.json"


def run():
    # 读取保存的文件
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://centerapi.fx168api.com/cms/api/cmsFastNews/fastNews/getList?fastChannelId=001&pageNo=1&pageSize=20&appCategory=web&direct=down",
        None,
        headers,
    )

    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        result = json.loads(body)["data"]["items"]
        for index in range(len(result)):
            if index < 3:
                id = result[index]["fastNewsId"]
                link = "https://www.fx168news.com/express/fastnews/{}".format(id)
                if link in ",".join(links):
                    print("fx168 live news exists link: ", link)
                    break
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
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))

    else:
        print("fx168 live news request error: ", response)


try:
    run()
except Exception as e:
    print("fx168 live news exec error: ", repr(e))
    logging.exception(e)
