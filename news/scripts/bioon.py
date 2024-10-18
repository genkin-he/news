# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts,current_time
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "msStatisUserId=1725256097192_d461b2e2; gr_user_id=f29e7278-8813-4ccd-80c1-a0636cc4338c; Hm_lvt_1e2aa76b9e893c2641e3129643165132=1725256097; HMACCOUNT=DE8779AB467443C3; _ga=GA1.1.625244564.1725256097; aea9aa242cc95dc5_gr_session_id=84207c88-8cb2-498d-a6d5-9dfe35700dff; aea9aa242cc95dc5_gr_session_id_sent_vst=84207c88-8cb2-498d-a6d5-9dfe35700dff; XSRF-TOKEN=eyJpdiI6IlhkMG5JR2lqVm1FXC91Uk5lcHY2NFpRPT0iLCJ2YWx1ZSI6IkZXOHloazVwdTJKdkZhSGswVUNheXFZZUhjTnpucm1Vak0yWm5BQ0JITnkxMUtIRW9Heng4SDVzbmlyMTEySWtRS0lqWDlTYjJ1eVk3K3BGWlpWUTJRPT0iLCJtYWMiOiJmMDhhZDk4ODJiN2MwNzg2N2I1YmJkNGNmYzczOTYwZGIzODcwZGNmN2VjNTJkN2NhN2RjNWY0NjliZDJhYzQyIn0%3D; bioon_session=eyJpdiI6IllwdWZaS0RnMDFIXC8rYU1CVUVTWExBPT0iLCJ2YWx1ZSI6IllJYjZEZnc5U3NWOXVyTlhZUVVQUEp3ZWFmMEhhNTFxRDZ1R1Fhb1wvMnBOVjlXVUhDS1wvcEdXVDNkaE1lZ3J5Mnl3NFllcXNvUDAxcVRyVXo3OHA2YlE9PSIsIm1hYyI6IjA5NTBhNGFlN2Y4ODljNTRmZWRjZWZjMjM2NmFjYzhhNTEzZDhlYjQyZTM3ZDdlMzMyZTI2ZDI5Njg5ZWMyOTgifQ%3D%3D; _ga_Q9WJ5CGWD2=GS1.1.1725259958.2.1.1725260039.0.0.0; Hm_lpvt_1e2aa76b9e893c2641e3129643165132=1725260040",
}

base_url = "https://www.bioon.com/"
filename = "./news/data/bioon/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    print("bioon link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select('.composs-main-content div[style="color: #303a4e;"]')[0]

        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("bioon request: {} error: ".format(link), response)
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
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".composs-blog-list > .item")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].select(".item-content> h2 > a")[0]["href"].strip()
            title = items[index].select(".item-content> h2 > a")[0].text.strip()
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
                        "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("bioon request error: ", response)


try:
    run(base_url)
except Exception as e:
    print("bioon exec error: ", repr(e))
    logging.exception(e)
