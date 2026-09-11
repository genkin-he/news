# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
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
    "cookie": "Hm_lvt_3d113c8324b108865d5f578fa799f678=1734919806; HMACCOUNT=6C8CECE5E323CD44; acw_tc=0a47314617349198059184624e004eae6896f2a34d92739480f1a086ab3d4f; ASPSESSIONIDSAADQTDB=MMMEDJJDNHCALCAAPILCJDMN; _ga=GA1.1.1062564735.1734919806; Hm_lpvt_3d113c8324b108865d5f578fa799f678=1734919821; _ga_YD8KXPNBE7=GS1.1.1734919806.1.1.1734919821.0.0.0",
}

base_url = "https://www.c114.com.cn"
filename = "./news/data/c114/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("gbk")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select(".text")[0]

        ad_elements = soup.select(".ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request("https://www.c114.com.cn/news/", None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("gbk")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".content_c_list > .new_list_c")
        for node in nodes:
            if post_count >= 2:
                break
            link = str(node.select("h6 > a")[0]["href"].strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = str(node.select("h6 > a")[0].text.strip())
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
                        "source": "c114",
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
    util.execute_with_timeout(run)
