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
    "cookie": '_ga=GA1.1.1899341607.1768637761; __gads=ID=7681e3e175e71070:T=1768637762:RT=1768637762:S=ALNI_MY_yDgLCz_GGQW-oC-nOAbkl0k0Qw; __gpi=UID=000011e5eb119e36:T=1768637762:RT=1768637762:S=ALNI_Mawn8yFgJyt0P4SWQfJgVxeUEmVEg; __eoi=ID=f829c3b5801e556b:T=1768637762:RT=1768637762:S=AA-AfjYEhCtlhCnc9GSF4KfLVJyD; __cf_bm=eQiycMTaVW9SrAKTCJYFQO8vcYhYi.89m9xOVh6rfbc-1768894195-1.0.1.1-YxZTiTtIfSXy_QRa.9dXEBxmGIaMGdPK22S6bMZJsNRdB4cf7GqqqkuyoIwarSfnZQn_FyviK94oyTvq6yW4iL5YL39.YOuntHxOchUbUNE; _ga_ZJ42QPY9K7=GS2.1.s1768894196$o3$g1$t1768894215$j41$l0$h0',
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
