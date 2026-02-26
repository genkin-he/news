# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import json
import re
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 使用 curl_cffi 模拟 Chrome 以绕过 403（TLS/JA3 指纹）
IMPERSONATE = "chrome120"

_curl_session = None


def _get_session():
    global _curl_session
    if _curl_session is None:
        _curl_session = curl_requests.Session(impersonate=IMPERSONATE)
    return _curl_session

base_url = "https://www.bastillepost.com"
filename = "./news/data/bastillepost/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = _get_session().get(quote(link, safe="/:"), timeout=30)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        soup = body.find(class_="article-body")
        if not soup:
            return ""
        ad_elements = soup.select(".ad-container")
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = _get_session().get(quote(link, safe="/:"), timeout=30)
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".bppost-list > .bppost-item")
        for index in range(len(items)):
            if index > 2:
                break
            node = items[index]
            href = node.get("href")
            title_el = node.select_one(".bppost-title")
            img_el = node.select_one(".bppost-item-cover-container > img")
            if not href or not title_el or not img_el:
                continue
            link = base_url + href.strip()
            title = title_el.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
            image = img_el.get("src") or ""
            image = image.strip()
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "image": image,
                        "pub_date": util.current_time_string(),
                        "source": "bastillepost",
                        "kind": 2,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


link1 = "https://www.bastillepost.com/hongkong/category/5-%e9%8c%a2%e8%b2%a1%e4%ba%8b"
link2 = "https://www.bastillepost.com/hongkong/category/138491-%e5%9c%b0%e7%94%a2"
if __name__ == "__main__":
    util.execute_with_timeout(run, link1)
    util.execute_with_timeout(run, link2)
