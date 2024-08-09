# -*- coding: UTF-8 -*-

import logging
import urllib.request  # 发送请求
import json
import re
import time
from util.util import history_posts

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "_pcc": "D1TtWJUNJU2zHRBOUCpqzgub0GXBBrBQvwFw6loXP8SEGov261BGuCUnvV2OylZ3n1PM/4HlDxOTHcpA8kvSKuw+wlIkJ7Z/TX8nBSm9BpuVrl0Y/XaHXuj0LOfrFBjIf7hKDwTg2siVPrk+jDMsLS3nKcBSmEogUq++U9ksI4U=",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Dnt": 1,
    "Origin": "https://www.fx168news.com",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://www.fx168news.com/",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Site-Channel": "001",
    "T": "",
}
base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/info.json"


def get_detail(id):
    print("fx168 news: ", id)
    request = urllib.request.Request(
        "https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsDetail?newsId={}".format(id),
        None,
        headers,
    )
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        body = json.loads(body)["data"]["newsContent"]
        return body


def run():
    # 读取保存的文件
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://centerapi.fx168api.com/cms/api/cmsnews/news/getNewsByChannel?pageNo=1&pageSize=10&channelCodes=001001",
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
                id = result[index]["newsId"]
                url_code = result[index]["urlCode"]
                link = "hhttps://www.fx168news.com/article/{}".format(url_code)
                if link in ",".join(links):
                    print("fx168 news exists link: ", link)
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
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("fx168 news request error: ", response)


try:
    run()
except Exception as e:
    print("fx168 news exec error: ", repr(e))
    logging.exception(e)
