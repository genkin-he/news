# -*- coding: UTF-8 -*-

import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_ga=GA1.1.124143173.1735808742; _ga_L1F1234X85=GS1.1.1735808741.1.1.1735808749.0.0.0; cookies=true",
}
base_url = "https://www.capitoltrades.com/"
filename = "./news/data/capitoltrades/P000197.json"
util = SpiderUtil()
def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    resp = response.read().decode("utf-8")
    soup = BeautifulSoup(resp, "lxml")
    if "buzz" in link:
        title = soup.select("header h1")[0].string
        description = str(soup.select(".tweet-body_root__RNPsG")[0])
    else:
        title = soup.select("header h1")[0].string
        description = str(soup.select(".prose")[0])
    return [title, description]


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.capitoltrades.com/politicians/P000197", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        items = body.split("Related Reading")
        if len(items) == 0:
            return
        body = items[1]
        result = re.findall(r'.*?\\"href\\":\\"/(.*?)\\"*', body)
        for index in range(len(result)):
            if index < 3:
                link = base_url + result[index]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                detail = get_detail(link)
                title = detail[0]
                description = detail[1]
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "capitoltrades",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


try:
    # run()
    util.info("屏蔽 stop capitoltrades P000197")
except Exception as e:
    traceback.print_exc()
    util.log_action_error(f"exec error: {repr(e)}\n")
