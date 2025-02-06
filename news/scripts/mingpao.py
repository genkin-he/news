# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import requests  # Changed from urllib.request
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "mpLoginStatus=nologin; FPID=FPID2.2.CyL2wqjmCyTTXRzR49DVlSZOSIAKpu3I6mHkymTr2II%3D.1738828169; FPLC=20KHXi4Sx6c9vfgI4RIqXn83UjxtSayXXyINleBrV4ggf%2FbUSlZo%2Bda%2BiijltwP36UJe62SD0Ddq2Gm16Jd3dB3OXB08szOuWZ9EYAoUDxHAFyVF66caYFAkCtxEaA%3D%3D; _gid=GA1.2.1974149629.1738828221; cto_bundle=vfvsOF80Y0toa3Q4dGNDSTYlMkZGR1poR1dmTlB1Y08lMkZDYTA1WUpOUm1aY3piWFdkbEZ0JTJGSEdaT3djQTBPcXJPSiUyRms5eENnTW9HdmtGSWtNdEtIQ2F4SCUyRnNlMXBPYjc2WWRWa082YXpYc0lheUhidURON0gzanV4TDhKSCUyRllHJTJCejZhbEwlMkZpV0w2SFlsNVdRbUEwY2JhWmVWcTlBJTNEJTNE; _ga=GA1.1.1768069481.1738828169; _ga_2CX22RM6FV=GS1.1.1738828220.1.1.1738831175.60.0.0; _ga_26L1K95RQX=GS1.1.1738830951.2.1.1738831177.59.0.0; _ga_PJXF9C93DG=GS1.1.1738828170.1.1.1738831177.58.0.306486543; _ga_FWRHJGBF7Y=GS1.1.1738830951.2.1.1738831177.60.0.0; _ga_E35W61CKGY=GS1.1.1738828172.1.1.1738831177.0.0.1260562116; FPGSID=1.1738830193.1738831180.G-E35W61CKGY.v5qe0AJOcBEWURxWky1yuw; FCNEC=%5B%5B%22AKsRol_WiMwsi4VwyEfiPCVZmE4Z5JqMZKiQIwb-OxSZG8IZPaTnroCikvsYW5ZYA74AM04aIWG6_-0nTqryeWLhOaEpHGVM8ZhVlSyoT_pN73yb_c-z0cJy7Cd7sw76rbh8JBb3ydY3UeOuKD0Rt4GySdgYeAspiQ%3D%3D%22%5D%5D",
}

base_url = "https://news.mingpao.com"
filename = "./news/data/mingpao/list.json"
util = SpiderUtil()


def get_detail(link):
    print("mingpao link: ", link)
    try:
        response = requests.get(link, headers=headers)  # Changed to requests.get
        if response.status_code == 200:  # Changed from status to status_code
            body = BeautifulSoup(
                response.text, "lxml"
            )  # Changed from response.read().decode()
            soup = body.find(class_="article_content")

            # 移除 <p dir="ltr">
            for element in soup.select("p[dir='ltr']"):
                element.decompose()
            
            # 移除 <iframe src="https://www.facebook.com/plugins/page.php?
            for element in soup.select("iframe[src*='facebook.com']"):
                element.decompose()

            # 正则匹配多个 \n\n\n\n\n\n\n 只保留一个 \n
            description = re.sub(r"\n\n+", "\n", str(soup).strip())
            return description
        else:
            print("mingpao request: {} error: ".format(link), response.status_code)
            return ""
    except Exception as e:
        print(f"mingpao request error: {str(e)}")
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    link = "https://news.mingpao.com/ins/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/main#tabcontentnewslist2lat-tab"
    response = requests.get(link, headers=headers)  # Changed to requests.get
    if response.status_code == 200:  # Changed from status to status_code
        body = response.text  # Changed from response.read().decode()
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".contentwrapper")
        for index, node in enumerate(items):
            if index > 4:
                break
            kind = node.select_one(".title").text.strip()
            if kind not in ["地　產", "經　濟"]:
                continue
            print("mingpao kind: ", kind)
            item = node.select_one("figure a")
            link = item["href"].strip()
            if link in ",".join(_links):
                print("mingpao exists link: ", link)
                break
            title = item["title"].strip()
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "mingpao",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("mingpao request error: {}".format(response.status_code))


util.execute_with_timeout(run)
