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
    "cookie": "A3=d=AQABBHfeaGcCEF4gTjikEllEt8WpdanSRKIFEgEBAQEvamdyZwAAAAAA_eMAAA&S=AQAAAjWaOYhAC2U04wHVAgZIpD4; A1=d=AQABBHfeaGcCEF4gTjikEllEt8WpdanSRKIFEgEBAQEvamdyZwAAAAAA_eMAAA&S=AQAAAjWaOYhAC2U04wHVAgZIpD4; A1S=d=AQABBHfeaGcCEF4gTjikEllEt8WpdanSRKIFEgEBAQEvamdyZwAAAAAA_eMAAA&S=AQAAAjWaOYhAC2U04wHVAgZIpD4; cmp=t=1734944046&j=0&u=1---; gpp=DBAA; gpp_sid=-1; tbla_id=d0d8c5b4-a278-4cfe-9229-fc75784da290-tucte626409; axids=gam=y-9IZismxE2uIhFz6YNlN0XnYOTqIOBDjH~A&dv360=eS1BYXdkRWQ5RTJ1R25GdndlZFJ4akZrVFNhRFpoQ21nb35B&ydsp=y-TA55xQZE2uIhmmIFfNPkAGJo7ORDBsFv~A&tbla=y-UDssoBxE2uLAPPqahDTpLQlLBO1Tak38~A",
}
base_url = "https://finance.yahoo.com/topic/latest-news/"
filename = "./news/data/yahoo/list_finance_us.json"
current_links = []

util = SpiderUtil()
def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        try:
            resp = response.read().decode(response.headers.get_content_charset())
        except UnicodeDecodeError:
            return ["", ""]
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one(".article .body")

        # 过滤 <div data-testid="view-comments"></div> 的 div
        ad_elements = soup.select('div[data-testid="inarticle-ad"]')
        view_comment = soup.select_one('div[data-testid="view-comments"]')
        if view_comment:
            view_comment.decompose()
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return [
            str(soup),
            body.select_one(".byline-attr-time-style > time")["datetime"].replace(
                "Z", "+08:00"
            ),
        ]
    else:
        util.error("request: {} error: {}".format(link, response))
        return ["", ""]

def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(base_url, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode(response.headers.get_content_charset())
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".content > .titles-link")
        for index in range(len(items)):
            title = ""
            link = ""
            if index > 1:
                break
            a_tag = items[index]
            if "https://finance.yahoo.com/news/" not in a_tag["href"]:
                util.info("not in href: {}".format(a_tag["href"]))
                continue
            else:
                link = a_tag["href"]
                if a_tag.select_one("h2"):
                    title = a_tag.select_one("h2").text
                else:
                    title = a_tag.select_one("h3").text
            if link == "":
                continue
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
            detail = get_detail(link)
            description = detail[0]
            if description == "":
                continue
            pub_date = util.parse_time(detail[1], "%Y-%m-%dT%H:%M:%S.%f%z")
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                        "source": "yahoo_finance_us",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)

