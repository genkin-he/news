# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "x-client-type": "pc",
    "x-device-id": "19385157-2697-0257-13e9-03e5e1c96f2b",
    "x-ivanka-app": "wscn|web|0.40.11|0.0|0",
    "x-ivanka-platform": "wscn-platform",
    "x-taotie-device-id": "19385157-2697-0257-13e9-03e5e1c96f2b",
    "x-track-info": '{"appId":"com.wallstreetcn.web","appVersion":"0.40.11"}',
    "Referer": "https://wallstreetcn.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://wallstreetcn.com/news/global"
filename = "./news/data/wallstreetcn/list.json"

util = SpiderUtil()
def get_detail(id, kind):
    print("wallstreetcn id: ", id, kind)
    if kind == "article":
        link = "https://api-one-wscn.awtmt.com/apiv1/content/articles/{}?extract=0&accept_theme=theme%2Cpremium-theme".format(id)
    elif kind == "live":
        link = "https://api-one-wscn.awtmt.com/apiv1/content/charts/{}".format(id)
    else:
        return ""
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        data = json.loads(resp)["data"]
        if "is_need_pay" in data and data["is_need_pay"]:
            return ""
        content = data["content"]
        if "None" in content:
            soup = BeautifulSoup(content, "lxml")
            for img in soup.find_all("img", src=lambda x: x and "None" in x):
                img.decompose()
            content = str(soup)
        
        return str(content).strip()
    else:
        print("wallstreetcn request: {} error: ".format(link), response)
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global&accept=article&cursor=&limit=10&action=upglide",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]["items"]
        for index in range(len(posts)):
            if index < 3:
                kind = posts[index]["resource_type"]
                post = posts[index]["resource"]
                id = post["id"]
                title = post["title"]
                image = ""
                
                if kind == "live":
                    image = "images" in post and post["images"] and len(post["images"]) > 0 and post["images"][0]["uri"]
                elif "image" in post and post["image"]:
                    image = post["image"]["uri"]
                author = ""
                if "author" in post and post["author"]:
                    author = post["author"]["display_name"]

                link = post["uri"]
                if link in ",".join(links):
                    print("wallstreetcn exists link: ", link)
                    break
                description = get_detail(id, kind)
                if description != "":
                    if kind == "live":
                        description = "{} <p><img src='{}' /></p>".format(description, image)
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "author": author,
                            "pub_date": util.current_time_string(),
                            "source": "wallstreetcn",
                            "kind": 1,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("wallstreetcn request error: {}".format(response))


util.execute_with_timeout(run)
