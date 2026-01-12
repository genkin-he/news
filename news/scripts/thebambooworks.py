# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "if-modified-since": 'Thu, 25 Sep 2025 08:31:25 GMT',
    "if-none-match": 'W/"b08d374784c8e6a6364a0000e7ac0dad"',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": '_ga=GA1.1.1675534351.1757674723; __cf_bm=TWw2ReMy31iujYiftPXRT.83nlg6k8oXcMH.dJcru40-1758792792-1.0.1.1-9DaWaOByJnhPhXlLaskpmi_aA.h1she3VPT250cts3LZV_tYncvlYzi3ogfzBUDYtfL5bkuypLnCW5AFiohLXXgN5jXQ4HPraba.E5WLhk8; _ga_ZJ42QPY9K7=GS2.1.s1758792794$o5$g1$t1758793101$j54$l0$h0; __gads=ID=6e5b4fb4f7087090:T=1757674723:RT=1758793101:S=ALNI_MZOFJBCJgP6cgAR7RWJHpo-iZGCkg; __gpi=UID=000011216e1b0e71:T=1757674723:RT=1758793101:S=ALNI_MZXeNwhzcyu6oiq-Y8Y6vCIIo7Ydg; __eoi=ID=c62c1c55b5e12ab2:T=1757674723:RT=1758793101:S=AA-Afjb59th_7h8m8O6vSpG4H_65',
}

base_url = "https://thebambooworks.com"
filename = "./news/data/thebambooworks/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select("#entry-content-container")[0]

        ad_elements = soup.select("div")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        # 删除最后两个 p 标签
        p_elements = soup.select("p")
        if len(p_elements) >= 2:
            # 删除最后两个 p 标签
            p_elements[-1].decompose()
            p_elements[-2].decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(url, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select("article h3 a")
        for node in nodes:
            if post_count >= 2:
                break
            a = node
            link = str(a["href"].strip())
            util.info("link: {}".format(link))
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            title = str(a.text.strip())
            util.info("title: {}".format(title))
            if title == "":
                continue
            post_count = post_count + 1
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "bambooworks",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run, "https://thebambooworks.com/cn/category/%E5%BF%AB%E8%AE%AF/")
