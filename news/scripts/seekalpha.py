# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=3889491919864; _sasource=; _gcl_au=1.1.330905452.1741658889; _ga=GA1.1.1481409249.1741658889; pxcts=af343f6c-fe1d-11ef-98b6-19d86e425fed; _pxvid=af34300f-fe1d-11ef-98b5-7c1cf1718571; __hstc=234155329.c852213c4c1dae9c43cd88c18f11b205.1741658891819.1741658891819.1741658891819.1; hubspotutk=c852213c4c1dae9c43cd88c18f11b205; __hssrc=1; user_id=62054337; user_nick=; user_devices=1%2C2; user_cookie_key=krvvs0; u_voc=; marketplace_author_slugs=limelight-alpha-management-partners%2Ckirk-spano; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=1453e996f1f9d5413775a0c446ea9eeeedf6f2cc; gk_user_access=1*premium.archived.mp_46.chat.mpb_46.mpf_46.mp_1177.chat.mpb_1177.mpf_1177*1741658895; gk_user_access_sign=8f567488737105f4ad9a4de818144fb55bd9624a; sailthru_hid=61fb400149add9e37e73f81d1a622b8467ce92c82447c9629707ce36da7489bd931b67c3055d04c2b6c95cd9; _uetvid=ae0805f0fe1d11ef9aa64d659a9a4cfb|1p8n5x|1741658892533|1|1|bat.bing.com/p/insights/c/n; sailthru_visitor=dfbed0ae-0148-4b78-a45d-8c219786e0f4; sailthru_content=3c5f57e561d9315a8a9a86be8720511ef0251524d6c5bdfecb6f06af6381eace; _ga_KGRFF2R2C5=GS1.1.1741658889.1.1.1741659410.60.0.0; _px3=9fcf041faffe346301c76eecf892c769af16416ba3c4d75afb41c76eeb9e2b96:KraBK8z4gOC6pCNzxjlcBGRoWyit8U02zCn+8MzD21/vB2DGafBehYnwkOc+JNd5CI82B7qaxbwBHl3STBkRbw==:1000:BT43vcqr4+3i/Rd0fsZyYjrq7RGYvrlF/MjGoh7Qfw5k8UPSFNtSBX5wwTTy6sZH3uHf2TzOUHdV68keICjoE4yuEdGobiW0nnDyYKPOZacFGP34a6qV6MyOBeSaaIrBhRqKIoLmjlw9zuchHxkfttwE3yuEB36oHtXHYarawOZbTubUwmg7IcLvgOaMOMiZvCCOC9iLKrvy9Yh000IhX6QlVzFEu7hHjbrwAnwOWuk=; _pxde=65071718855d2eab6124830c6ae75e70f578038b252b7ac94024ea6427290df9:eyJ0aW1lc3RhbXAiOjE3NDE3NDU5MjcyMTcsImZfa2IiOjB9; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%223889491919864%22%2C%22machineCookieSessionId%22%3A%223889491919864%261741745932758%22%2C%22sessionStart%22%3A1741745932758%2C%22sessionEnd%22%3A1741747732758%2C%22firstSessionPageKey%22%3A%228be6544d-5bb2-4738-9606-51cf30513b4d%22%2C%22isSessionStart%22%3Atrue%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22init%22%2C%22timestamp%22%3A1741745932758%7D%7D; session_id=6993a784-7dc7-4709-a4b7-552c115c455e; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2F%22%7D",
    "Referer": "https://seekingalpha.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/list.json"

util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=6&page[number]=1"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        posts = response.json()["data"]
        for index in range(len(posts)):
            if index < 2:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["links"]["uriImage"]
                link = base_url + post["links"]["self"]
                publish_on = post["attributes"]["publishOn"]
                pub_date = util.current_time_string()
                if "-05:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-05:00")
                elif "-04:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-04:00")

                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                soup = BeautifulSoup(post["attributes"]["content"], "lxml")
                ad_elements = soup.select("#more-links")
                for element in ad_elements:
                    element.decompose()
                description = str(soup).strip()
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "seekalpha",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


util.execute_with_timeout(run)
