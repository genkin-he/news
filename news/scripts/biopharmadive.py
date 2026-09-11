# -*- coding: UTF-8 -*-
import logging
import traceback
from datetime import datetime, timezone, timedelta
import json
import re
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

# 使用 curl_cffi 模拟 Chrome 以绕过 403（TLS/JA3 指纹）
IMPERSONATE = "chrome120"

_curl_session = None


def _get_session():
    global _curl_session
    if _curl_session is None:
        _curl_session = curl_requests.Session(impersonate=IMPERSONATE)
    return _curl_session

base_url = "https://www.biopharmadive.com/"
filename = "./news/data/biopharmadive/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = _get_session().get(link, timeout=30)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        soup = body.select(".article-body")
        if not soup:
            soup = body.select(".body")
            if not soup:
                soup = body.select(".content__text")[0]
            else:
                soup = soup[0]
        else:
            soup = soup[0]
            
        ad_elements = soup.select(".hybrid-ad-wrapper")
        # 移除这些元素
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
        response = _get_session().get(link, timeout=30)
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".feed__item")
        for index in range(len(items)):
            if index > 2:
                break
            if not items[index].select(".feed__title > a"):
                continue
            link = "https://www.biopharmadive.com{}".format(items[index].select(".feed__title > a")[0]["href"].strip())
            title = items[index].select(".feed__title > a")[0].text.strip()
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
                        "source": "biopharmadive",
                        "kind": 1,
                        "language": "en"
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


link1 = "https://www.biopharmadive.com/"
link2 = "https://www.biopharmadive.com/press-release/"
if __name__ == "__main__":
    util.execute_with_timeout(run, link1)
    util.execute_with_timeout(run, link2)
