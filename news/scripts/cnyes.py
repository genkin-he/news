# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 改用requests库
import json
import re
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://news.cnyes.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "cookie": "_gid=GA1.2.1235959985.1740461742; _ga_YHSTW3NTRH=GS1.2.1740461741.1.0.1740461741.0.0.0; _ga_G733DLJ15Z=GS1.1.1740461741.1.0.1740461748.53.0.0; _ga_MHC8VFJ7Y6=GS1.1.1740461749.1.0.1740461749.60.0.0; _ga=GA1.1.1903781091.1740461702; _ga_Q14GZ4B1PW=GS1.1.1740461741.1.0.1740461749.0.0.0; _ss_pp_id=ad63f4720c1c78a1c521740432949954; tooltipLastShownDate=1; _td=74d5a339-70ed-477a-8d6c-5cb9ad8d6767; FCNEC=%5B%5B%22AKsRol9qaSeVP5YOqtnDFtzCoWoBfYichR1sI5Q0USenTh6IOlwf1D0ntIqQXmgX6RAkLVeBaT7l9wRqdGnEvgEQ_3UlRse1TBlAPNXcgsIkgOufFTJvqJ1WjFPmmFTSY_NElv3kQVDt1FlLB2KiT0CiE-Sp7Ygx9A%3D%3D%22%5D%5D; _ga_102K295BQ2=GS1.1.1740461701.1.1.1740462398.31.0.0; _ga_W8YSQ71T94=GS1.1.1740461701.1.1.1740462398.31.0.0",
}

base_url = "https://www.cnyes.cn/"
filename = "./news/data/cnyes/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one("#article-container")

        ad_elements = soup.select("script,style,[id*=-ad-]")
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    except Exception as e:
        util.error("request: {} error: {}".format(link, str(e)))
        return ""

def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False
    response = requests.get(
        "https://api.cnyes.com/media/api/v1/newslist/all?page=1&limit=30",
        headers=headers,
    )
    response.raise_for_status()
    response_data = response.json()

    items = response_data["items"]["data"]
    for index in range(len(items)):
        if index > 5:
            break
        id = items[index]["newsId"]
        link = "https://news.cnyes.com/news/id/{}".format(id)
        if link in ",".join(_links):
            util.info("exists link: {}".format(link))
            continue
        title = items[index]["title"]
        pub_date = util.convert_utc_to_local(items[index]["publishAt"])
        description = get_detail(link)
        if description != "":
            insert = True
            _articles.insert(
                0,
                {
                    "id": id,
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": pub_date,
                    "source": "cnyes",
                    "kind": 1,
                    "language": "zh-HK",
                },
            )

    if len(_articles) > 0 and insert:
        if len(_articles) > 10:
            _articles = _articles[:10]
        util.write_json_to_file(_articles, filename)


util.execute_with_timeout(run)
