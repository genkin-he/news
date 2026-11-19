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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "cmp=t=1745305074&j=0&u=1---; gpp=DBAA; gpp_sid=-1; axids=gam=y-Bne2OohE2uLUtF7vEIxPBUUYDDoYegyx~A&dv360=eS1QekJpbFlCRTJ1SGZwekxubk5IbFpCUFgySjROUVBuen5B&ydsp=y-xLnd72xE2uJ6ECxmciEQNWJLi.yzhe9l~A&tbla=y-ZHaOk89E2uIZ.nayfCy40Dyl031iozNI~A; A1=d=AQABBPA9B2gCEFeXJcdQDJ3gowuF6QUAXuoFEgEBAQGPCGgRaFgAAAAA_eMCAA&S=AQAAAgRdy6FS0on6Yu1jJB-y43E; A3=d=AQABBPA9B2gCEFeXJcdQDJ3gowuF6QUAXuoFEgEBAQGPCGgRaFgAAAAA_eMCAA&S=AQAAAgRdy6FS0on6Yu1jJB-y43E; A1S=d=AQABBPA9B2gCEFeXJcdQDJ3gowuF6QUAXuoFEgEBAQGPCGgRaFgAAAAA_eMCAA&S=AQAAAgRdy6FS0on6Yu1jJB-y43E; tbla_id=88b300a5-c84a-4752-97a1-db511395ecbe-tuctf00c372; thamba=2",
}
base_url = "https://hk.news.yahoo.com/business/"
filename = "./news/data/yahoo/list_finance_asia.json"
current_links = []

util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    open_link = link
    if "%" not in link:
        open_link = quote(link, safe="/:")
    request = urllib.request.Request(open_link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        try:
            resp = response.read().decode("utf-8")
        except UnicodeDecodeError:
            return ""
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one(".caas-body")
        if soup is None:
            soup = body.select_one(".atoms")
        # 过滤 <div data-testid="view-comments"></div> 的 div
        ad_elements = soup.select('div[data-testid="inarticle-ad"]')
        view_comment = soup.select_one('div[data-testid="view-comments"]')
        if view_comment:
            view_comment.decompose()
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup)
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(base_url, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".js-stream-content")
        for index in range(len(items)):
            title = ""
            link = ""
            if index > 3:
                break

            a_tag = items[index].select_one("h3 > a")
            if a_tag:
                link = a_tag["href"]
                title = a_tag.text
            else:
                continue
            if link == "":
                continue
            elif "https://" in link:
                continue
            else:
                link = "https://hk.news.yahoo.com" + link
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
            description = get_detail(link)
            if description == "":
                continue
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "yahoo_finance_asia",
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
    util.execute_with_timeout(run)
