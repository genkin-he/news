# -*- coding: UTF-8 -*-
from datetime import datetime, timezone, timedelta
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.util import history_posts,current_time, log_action_error
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'UOR=feed.mix.sina.com.cn,finance.sina.com.cn,; ULV=1721897778732:1:1:1::; SINAGLOBAL=118.122.97.227_1721897778.919302; Apache=118.122.97.227_1721897778.919303; SFA_version7.22.0=2024-07-25%2016%3A54; SFA_version7.22.0_click=1',
}

base_url = "https://sina.com.cn/"
filename = "./news/data/sina/list_us_stock.json"

def get_detail(link):
    print("sina us link: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, 'lxml')
        return str(soup.select(".article")[0])
    else:
        print("sina us request: {} error: ".format(link), response)
        return ""
    

def fetch_posts():
    request = urllib.request.Request(
        "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2518&k=&num=10&page=1", None, headers
    )
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        return json.loads(body)["result"]["data"]
    else:
        print("sina us request error: ", response)
        return []

def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    posts = fetch_posts()
    for post in posts:
        link = post["url"]
        title = post["title"]
        id = post["oid"]
        summary = post["intro"]
        author = post["author"]
        if link in ",".join(links):
            print("sina us exists link: ", link)
            break
        description = get_detail(link)
        if description:
            insert = True
            articles.insert(
                0,
                {
                    "id": id,
                    "title": title,
                    "description": description,
                    "link": link,
                    "summary": summary,
                    "author": author,
                    "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "sina_us_stock",
                    "kind": 1,
                    "language": "zh-CN",
                },
            )

    if articles and insert:
        articles = articles[:20]
        with open(filename, "w") as f:
            f.write(json.dumps({"data": articles}))

try:
    run()
except Exception as e:
    print("sina us exec error: ", repr(e))
    traceback.print_exc()
    log_action_error(f"sina us exec error: {repr(e)}\n")
