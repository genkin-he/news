# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re

from bs4 import BeautifulSoup

from util.util import current_time, history_posts

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
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
    "cookie": '_pxhd=23824071f65c47d7e3b3e9fcd47b32be3b133b014174b80fbcff906d2cf2f1b4:6099ff30-b2db-11ef-bd64-4c1b55a676cd; referralId=Direct; _cb=BMOA9lCZoSnBaYVya; pxcts=6441bd31-b2db-11ef-8c0f-44da767a7d95; _pxvid=6099ff30-b2db-11ef-bd64-4c1b55a676cd; usprivacy=1---; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.730455360.1733384083; _gid=GA1.2.1183695747.1733384083; OTGPPConsent=DBABBg~BUUAAAGA.QA; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_cluster=sgp3; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_identity=CiY3NjYwMjEzMzY5NjYyNTU0ODAyMDk3OTAwNzYwMjE0NDQ2NTI2NlITCP2w%2DK25MhABGAEqBFNHUDMwAPAB%5FbD4rbky; repeat_visitor=1733384084503-748260; bob_session_id=1733384084503-583952; BCSessionID=b5d93d85-3585-406b-b8bd-42603c8e6973; minVersion={"experiment":288997026,"minFlavor":"headlinesmi-1.17.1.140.js100"}; permutive-id=bb48e214-c612-4beb-a6e5-67cf50e1bca3; trc_cookie_storage=taboola%2520global%253Auser-id%3D36de74de-057d-4e33-8d7e-1d84eb691b3c-tucte482fc3; minUnifiedSessionToken10=%7B%22sessionId%22%3A%227208373866-d5d47dfe58-f73fb8acd1-78058d2f1d-eb94b72af0%22%2C%22uid%22%3A%225d10bb9783-1f39a4130c-e7f275b5d7-c4311bd8e1-bab08b31d2%22%2C%22__sidts__%22%3A1733385793721%2C%22__uidts__%22%3A1733385793721%7D; last_visit_bc=1733385847239; seg_sessionid=4232f722-a5b4-4b2d-8fe2-f9ce0d6acf55; _chartbeat2=.1733384082036.1733385856955.1.Qr9enC4g0okBqkP3yDvwwNCrqk3l.1; _cb_svref=external; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Dec+05+2024+16%3A04%3A17+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=72ee242e-9894-4979-a0a8-71a9140d25c8&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=SPD_BG%3A0%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false; s_ips=1649; s_tp=6480; s_ppv=thehill%253Ademocratic-rep-pushes-biden-to-issue-blanket-pardon-to-those-patel-could-target%2C25%2C25%2C25%2C1649%2C15%2C4; sailthru_pageviews=7; s_plt=21.91%2Cthehill%3Ademocratic-rep-pushes-biden-to-issue-blanket-pardon-to-those-patel-could-target; sailthru_content=e8b25caad75cd79293442f3d1a30c1fa9412c6fb6e5ee467f03bbb54bd85de2c48b2cfed235d053fe88496a0f63adb03; sailthru_visitor=38f26e92-6252-40a1-8315-a0208c0d0c36; _px2=eyJ1IjoiMzRhZDc5ZDAtYjJkZi0xMWVmLTkyMTEtYjUxOGU1NThkZDRjIiwidiI6IjYwOTlmZjMwLWIyZGItMTFlZi1iZDY0LTRjMWI1NWE2NzZjZCIsInQiOjE3MzMzODYyNjQ0MzQsImgiOiJlNWI2YmVhNjJjN2Y2YzQzNzhlM2UxZjZhYzhmYmY5NWI1NjFjYjY4ZmQyMTQyZTVjZmRjYWNlNjRkYmRkZmQ4In0=',
}
base_url = "https://thehill.com/news/"
filename = "./news/data/thehill/list.json"


def get_detail(link):
    print("thehill link: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".article__text")[0]

        ad_elements = soup.select(".ad-unit,.hardwall")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("thehill request: {} error: ".format(link), response.status)
        return ""


def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://thehill.com/wp-json/lakana/v1/template-variables/",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["sidebar"]["just_in"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                kind = post["post_type"]
                id = post["id"]
                title = post["title"]
                link = post["link"]
                if link in ",".join(links):
                    print("thehill exists link: ", link)
                    break

                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "kind": kind,
                            "link": link,
                            "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "thehill",
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("thehill request error: ", response)


try:
    run()
except Exception as e:
    print("thehill exec error: ", repr(e))
    logging.exception(e)
