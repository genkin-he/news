# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
import time
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'en-US,en;q=0.9',
    "cache-control": 'no-cache',
    "pragma": 'no-cache',
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}

base_url = "https://talkmarkets.com"
filename = "./news/data/talkmarkets/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        if "Access Restricted" in resp:
            raise Exception("Connection reset by peer") 
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select_one("#blog-content")
        if content_wrappers is None:
            return ""
        else:
            soup = content_wrappers
            ad_elements = soup.select("div")
            for element in ad_elements:
                element.decompose()

        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run(url):
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml")
        nodes = soup.select("h5.card-title a")
        util.info("nodes: {}".format(len(nodes)))
        for node in nodes:
            if post_count >= 3:
                break
            link = str(node["href"])
            title = str(node.text)
            title = title.replace('\n', '')
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = ""
            try:
                description = get_detail(link)
            except Exception as e:
                util.error("request: {} error: {}".format(link, str(e)))
                if "Access Restricted" in str(e):
                    break
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "apnews",
                        "pub_date": util.current_time_string(),
                        "source": "apnews",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 40:
                articles = articles[:40]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    # util.execute_with_timeout(run, "https://talkmarkets.com/blog?page=1")
    # 有人要验证，且 链接已变更
    util.info("403 Forbidden")