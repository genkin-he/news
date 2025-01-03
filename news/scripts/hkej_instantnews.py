# -*- coding: UTF-8 -*-

import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.util import current_time, history_posts, log_action_error

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}
base_url = "https://www2.hkej.com"
filename = "./news/data/hkej/list.json"


def get_detail(link):
    print("hkej: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split("<div id='article-content'>")[1]
        .split('<div id="hkej_sub_ex_article_nonsubscriber_ad_2014">')[0]
    )
    body = re.sub(r"(\t)\1+", "", body)
    body = re.sub(r"(\n)\1+", "\n", body)
    body = body.lstrip()
    return body


def run():
    # 读取保存的文件
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request("https://www2.hkej.com/instantnews", None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        result = re.findall('.*<h3><a href="(.*)</a></h3>*', body)
        for index in range(len(result)):
            if index < 3:
                item = result[index].split('">')
                link = base_url + item[0]
                if link in ",".join(links):
                    print("hkej instantnews exists link: ", link)
                    break
                title = item[1]
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "hkej",
                            "kind": 1,
                            "language": "zh-HK",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("hkej instantnews request error: ", response)


try:
    run()
except Exception as e:
    print("hkej instantnews exec error: ", repr(e))
    traceback.print_exc()
    log_action_error(f"hkej instantnews exec error: {repr(e)}\n")
