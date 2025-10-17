# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from datetime import datetime
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "DNT": "1",
    "Host": "www.pharmexec.com",
    "upgrade-insecure-requests": "1",
}

base_url = "https://www.pharmexec.com/"
filename = "./news/data/pharmexec/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".blockText_blockContent__TbCXh")[0]

        ad_elements = soup.select(".bw-fsa")
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
    response = urllib.request.urlopen(request, timeout=3)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "xml")
        items = soup.find_all("item")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].link.string.strip().replace("onclive", "pharmexec")
            title = items[index].title.string.strip()
            pub_date = util.parse_time(
                items[index].pubDate.string.strip(), "%a, %d %b %Y %H:%M:%S %z"
            )
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
                        "pub_date": pub_date,
                        "source": "pharmexec",
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
    util.execute_with_timeout(run, "https://www.pharmexec.com/rss.xml")

