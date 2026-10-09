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
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "A1=d=AQABBOXW42cCEIGX6k8t5AKfNqmL--2p_GMFEgEBAQEo5WftZ1gAAAAA_eMAAA&S=AQAAAgYpqfGfyvtsHdEWmSh1woY; A3=d=AQABBOXW42cCEIGX6k8t5AKfNqmL--2p_GMFEgEBAQEo5WftZ1gAAAAA_eMAAA&S=AQAAAgYpqfGfyvtsHdEWmSh1woY; A1S=d=AQABBOXW42cCEIGX6k8t5AKfNqmL--2p_GMFEgEBAQEo5WftZ1gAAAAA_eMAAA&S=AQAAAgYpqfGfyvtsHdEWmSh1woY; cmp=t=1742984938&j=0&u=1---; gpp=DBAA; gpp_sid=-1; _gcl_au=1.1.461531081.1742984938; ___nrbic=%7B%22isNewUser%22%3Atrue%2C%22previousVisit%22%3A1742984937%2C%22currentVisitStarted%22%3A1742984937%2C%22sessionId%22%3A%220c5337e7-e18b-4504-a205-4abd05e4295c%22%2C%22sessionVars%22%3A%5B%5D%2C%22visitedInThisSession%22%3Atrue%2C%22pagesViewed%22%3A1%2C%22landingPage%22%3A%22https%3A//techcrunch.com/%22%2C%22referrer%22%3A%22%22%2C%22lpti%22%3Anull%7D; ___nrbi=%7B%22firstVisit%22%3A1742984937%2C%22userId%22%3A%22b1c9fef8-9391-4806-834c-9fce61668217%22%2C%22userVars%22%3A%5B%5D%2C%22futurePreviousVisit%22%3A1742984937%2C%22timesVisited%22%3A1%7D; compass_uid=b1c9fef8-9391-4806-834c-9fce61668217; _ga_KJR3C2ZQN6=GS1.1.1742984938.1.0.1742984938.60.0.0; _ga=GA1.1.2084318813.1742984938; axids=gam=y-Cj7ra8FE2uKlnVCIeCVMAlyx6UIxbJNK~A&dv360=eS01eDdoMm5WRTJ1RXIyVl9fNzRXRnlXdEZaYno3czZIUn5B&ydsp=y-dQYKS4lE2uLUsGuXTNe_6Rk1cXql9MEJ~A&tbla=y-_p0coHtE2uIYrKo5BQUb6kaWiwlsmTCA~A; tbla_id=de970043-9d2b-4736-abba-0a5d848c4b85-tuctedcefee",
}

base_url = "https://techcrunch.com/"
filename = "./news/data/techcrunch/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    if link in current_links or "/video/" in link:
        return ""
    util.info("link: {}".format(link))
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
        util.error("request: {} error: {}".format(link, response))
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
                util.info("exists link: {}".format(link))
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
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
