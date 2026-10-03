# -*- coding: UTF-8 -*-
import logging
import traceback
from datetime import datetime, timezone, timedelta
import json
import re
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

# 使用 curl_cffi 模拟浏览器以绕过 403（TLS/JA3 指纹）。原实现固定 chrome120 一档，
# 被拒就整轮失败；改为整条降级链，命中的档位缓存复用。
IMPERSONATE_PROFILES = ("chrome120", "safari18_0", "firefox133")

# execute_with_timeout 的预算为 10 秒，且本脚本在 __main__ 里连跑两轮，
# 而 CI 的 gtimeout 只给整个进程 15 秒——原实现两处 timeout=30 都超出预算。
TIMEOUT = 5
RUN_TIMEOUT = 6

_curl_session = None


def _get_session(profile=None):
    global _curl_session
    if _curl_session is None:
        _curl_session = curl_requests.Session(
            impersonate=profile or IMPERSONATE_PROFILES[0]
        )
    return _curl_session


def _request(url):
    """被拒时逐档降级重试；全链失败返回最后一个响应"""
    global _curl_session

    response = _get_session().get(url, timeout=util.request_timeout(TIMEOUT))
    if response.status_code == 200:
        return response

    for profile in IMPERSONATE_PROFILES[1:]:
        if util.out_of_time():
            break
        util.info("request url: {}, impersonate: {} rejected with: {}".format(
            url, profile, response.status_code))
        session = curl_requests.Session(impersonate=profile)
        response = session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            _curl_session = session
            return response
    return response

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
        response = _request(link)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        # 三个候选容器都取不到时跳过该条，原实现直接对空列表取 [0] 会抛 IndexError
        # 并中断整轮
        soup = None
        for selector in (".article-body", ".body", ".content__text"):
            found = body.select(selector)
            if found:
                soup = found[0]
                break
        if soup is None:
            util.info("content not found, skipped: {}".format(link))
            return ""

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
        response = _request(link)
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".feed__item")
        for index in range(len(items)):
            if index > 2 or util.out_of_time():
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
    util.execute_with_timeout(run, link1, timeout=RUN_TIMEOUT)
    util.execute_with_timeout(run, link2, timeout=RUN_TIMEOUT)
