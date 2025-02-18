# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "A1=d=AQABBKxRB2cCEK0LLZ4HjsQLVa7nwC4FPmgFEgEBAQGjCGcRZ2ChyyMA_eMAAA&S=AQAAAopGdwsv42vYOkNZtIXmckw; A3=d=AQABBKxRB2cCEK0LLZ4HjsQLVa7nwC4FPmgFEgEBAQGjCGcRZ2ChyyMA_eMAAA&S=AQAAAopGdwsv42vYOkNZtIXmckw; A1S=d=AQABBKxRB2cCEK0LLZ4HjsQLVa7nwC4FPmgFEgEBAQGjCGcRZ2ChyyMA_eMAAA&S=AQAAAopGdwsv42vYOkNZtIXmckw; cmp=t=1728532911&j=0&u=1---; gpp=DBAA; gpp_sid=-1; _gcl_au=1.1.1590016139.1728532913; ___nrbic=%7B%22isNewUser%22%3Atrue%2C%22previousVisit%22%3A1728532912%2C%22currentVisitStarted%22%3A1728532912%2C%22sessionId%22%3A%2259657671-59c6-4caf-bce5-bc32f17b6a6d%22%2C%22sessionVars%22%3A%5B%5D%2C%22visitedInThisSession%22%3Atrue%2C%22pagesViewed%22%3A1%2C%22landingPage%22%3A%22https%3A//techcrunch.com/%22%2C%22referrer%22%3A%22%22%2C%22lpti%22%3Anull%7D; ___nrbi=%7B%22firstVisit%22%3A1728532912%2C%22userId%22%3A%22eea26347-f731-4290-b836-ca3b9d59a096%22%2C%22userVars%22%3A%5B%5D%2C%22futurePreviousVisit%22%3A1728532912%2C%22timesVisited%22%3A1%7D; compass_uid=eea26347-f731-4290-b836-ca3b9d59a096; _ga_KJR3C2ZQN6=GS1.1.1728532912.1.0.1728532912.60.0.0; _ga=GA1.1.1794013525.1728532913; axids=gam=y-Q4W3JPdE2uLD2b422vADHQCBMd7sOOE9~A&dv360=eS1YOFQ4ZUJaRTJ1SDhfYnJQRHgyRzIzSWgxMzg2Rm10Yn5B&ydsp=y-P16xWCRE2uLzABWHXXaRTfCKg7qUsS9s~A&tbla=y-8s_vK9hE2uILE1770oFeYO0D04SxOZPC~A; tbla_id=4b3f5910-e65c-488c-bcdd-6a5b78146dd1-tuctdfe8300",
}

base_url = "https://techcrunch.com/"
filename = "./news/data/techcrunch/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(link):
    if link in current_links or "/video/" in link:
        return ""
    print("techcrunch link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        soup = soup.select(".entry-content")[0]

        ad_elements = soup.select(
            ".ad-unit, .marfeel-experience-inline-cta, .wp-block-tc23-podcast-player"
        )
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("techcrunch request: {} error: ".format(link), response)
        return ""


def run():
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(base_url, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".wp-block-post-template > .wp-block-post")
        for node in nodes:
            if post_count >= 3:
                break
            link = str(node.select(".loop-card__title > a")[0]["href"]).strip()
            title = str(node.select(".loop-card__title")[0].text).strip()
            if link in ",".join(links):
                print("techcrunch exists link: ", link)
                break
            description = get_detail(link)
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "TechCrunch",
                        "pub_date": util.current_time_string(),
                        "source": "techcrunch",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("techcrunch request error: {}".format(response))


util.execute_with_timeout(run)
