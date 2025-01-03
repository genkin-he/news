# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.util import current_time, history_posts, log_action_error
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
    "cookie": "_gcl_au=1.1.762604258.1734926649; _ga=GA1.1.1396770216.1734926650; AIMPID=b96317f1-252f-ad88-e9ff-73781e8dc092; _ga_BWZVK26SQF=GS1.1.1734934323.3.0.1734934323.0.0.0",
}

base_url = "https://www.bastillepost.com"
filename = "./news/data/bastillepost/list.json"


def get_detail(link):
    print("bastillepost link: ", link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode(response.headers.get_content_charset())
        body = BeautifulSoup(resp, "lxml")
        soup = body.find(class_="article-body")

        ad_elements = soup.select(".ad-container")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("bastillepost request: {} error: ".format(link), response)
        return ""


def run(link):
    data = history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".bppost-list > .bppost-item")
        for index in range(len(items)):
            if index > 2:
                break
            node = items[index]

            link = base_url + node["href"].strip()
            title = node.select_one(".bppost-title").text.strip()
            if link in ",".join(_links):
                print("bastillepost exists link: ", link)
                break
            image = node.select_one(".bppost-item-cover-container > img")["src"].strip()
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "image": image,
                        "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "bastillepost",
                        "kind": 2,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("bastillepost request error: ", response)


try:
    run("https://www.bastillepost.com/hongkong/category/5-%e9%8c%a2%e8%b2%a1%e4%ba%8b")
    run("https://www.bastillepost.com/hongkong/category/138491-%e5%9c%b0%e7%94%a2")
except Exception as e:
    print("bastillepost exec error: ", repr(e))
    traceback.print_exc()
    log_action_error(f"bastillepost exec error: {repr(e)}\n")
