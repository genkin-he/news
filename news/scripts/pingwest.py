# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "_pk_id.2.7fe8=1806dcbee4b2d7d8.1725356118.; _pk_ses.2.7fe8=1",
    "Referer": "https://www.pingwest.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://www.pingwest.cn/"
filename = "./news/data/pingwest/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    print("pingwest link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".article-style")[0]

        ad_elements = soup.select(".ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("pingwest request: {} error: ".format(link), response)
        return ""


def run(link):
    data = history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        response = json.loads(body)
        if response["data"]["list"] == "":
            return
        
        soup = BeautifulSoup(response["data"]["list"], "lxml")
        items = soup.select("article")
        for index in range(len(items)):
            if index > 1:
                break
            link = "https:{}".format(items[index].select(".title > a")[0]["href"].strip())
            title = items[index].select(".title > a")[0].text.strip()
            if link in ",".join(_links):
                break
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("pingwest request error: ", response)


try:
    run("https://www.pingwest.com/api/index_news_list?last_id=")
except Exception as e:
    print("pingwest exec error: ", repr(e))
    logging.exception(e)
