# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "Accept-Language": 'zh-CN,zh;q=0.9',
    "Cache-Control": 'max-age=0',
    "Connection": 'keep-alive',
    "cookie": 'aliyungf_tc=67a0a0c837f573faf0f40dda9ef102de835568ebb3e306fb08a9868703e7b281; _ga=GA1.1.332743504.1757559008; open_app=true; _ga_DH8KJBSFD7=GS2.1.s1757559008$o1$g1$t1757559099$j60$l0$h0',
    "Sec-Fetch-Dest": 'document',
    "Sec-Fetch-Mode": 'navigate',
    "Sec-Fetch-Site": 'none',
    "Sec-Fetch-User": '?1',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"'
}

base_url = "https://www.dotdotnews.com"
filename = "./news/data/dotdotnews/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode(response.headers.get_content_charset())
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one("div.mainManuscripts div.post-content div.post-body")
        ad_elements = soup.select("input, figure")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select("div.flex-between div.item h4 a")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 2:
                break
            a = items[index]
            link = a["href"].strip()
            title = a.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
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
                        "pub_date": util.current_time_string(),
                        "source": "dotdotnews",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.dotdotnews.com/finance")
