# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib.request
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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

base_url = "https://www.cww.com"
filename = "./news/data/cww/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""

        lxml = BeautifulSoup(response.text, "lxml")
        soup = lxml.select_one("#divContentDiv")

        ad_elements = soup.select("script,style")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    except Exception as e:
        util.error("exception: {}".format(str(e)))
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    post_count = 0

    response = requests.get(
        "https://www.cww.net.cn/subjects/nav/rollList/3009", headers=headers
    )

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        nodes = soup.select("#newsList li")
        for index in range(len(nodes)):
            if index >= 2:
                break
            node = nodes[index]
            link = str(node.select("a")[0]["href"].strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            title = node.select(".slh")[0].text.strip()
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
                        "source": "cww",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run)
