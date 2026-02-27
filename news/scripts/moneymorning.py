# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "if-modified-since": 'Mon, 27 Oct 2025 09:59:04 GMT',
    "priority": 'u=0, i',
    "referer": 'https://moneymorning.com/',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"141.0.7390.108"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.108", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": 'logglytrackingsession=f5cb4e37-567a-40fa-8d8e-fdbe2f04ee24; _ga=GA1.1.1162612782.1761553047; _iiq_fdata=%7B%22pcid%22%3A%22cbdd112b-53ef-95ff-5d41-486c46989e0e%22%2C%22pcidDate%22%3A1761553047668%7D; OptanonAlertBoxClosed=2025-10-27T08:35:37.294Z; _li_dcdm_c=.moneymorning.com; _lc2_fpi=c5815cc71d3a--01k8jcy155c87rtv2zc6jc8zag; _lc2_fpi_js=c5815cc71d3a--01k8jcy155c87rtv2zc6jc8zag; _li_ss=CgA; cf_clearance=STVdZ_KG3GhmSbWoWlhirv7YPAkyWPPwyhU4fMmNJ_I-1761561474-1.2.1.1-APqfFHy7pzDXpPXiXMUcEco7nUjOQhDYl_V70KoBkd7zw_OJdMUN63hgaA3W55tAif3_2.2a9it9alySIg4Rhkev1DETk44svqgvAacdJy9UUzGBP81zhX9vnljmUC_o0VW_Kr1oLeqgzA7oYj2dIF.RvZIG2DU1KBclh6bUQaVvWUVhxHC4L7TvawLdzP5Jj9nueJ7sE0oJcuw2iJJ1Jrvn6CkY4xXFrhNizFD3laB58BUzsSOt9OD9c8QpTscn; __gads=ID=266f7b5581ba499d:T=1761554138:RT=1761562458:S=ALNI_MbLn8w_fotzmBx-aVPNmUqP8CTwcA; __gpi=UID=000012b8e6741794:T=1761554138:RT=1761562458:S=ALNI_MaAtONhkcp9-bEcfGOTffq5Zn2rOw; __eoi=ID=cfdbb039c6e39ef6:T=1761554138:RT=1761562458:S=AA-AfjZfhdPsEqUIpXbCKXcGvokr; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Oct+27+2025+18%3A54%3A20+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202509.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=9c7aa91a-4d7f-4e7f-a1b7-504105e12dd8&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0001%3A1%2CC0005%3A1&intType=1&geolocation=US%3BCA&AwaitingReconsent=false; _ga_JY6FFQTW4L=GS2.1.s1761561458$o2$g1$t1761562461$j60$l0$h1937097498'
}

base_url = "https://moneymorning.com"
filename = "./news/data/moneymorning/list.json"
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
        content_wrappers = body.select(".single-content")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            ad_elements = soup.select("div script style")
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
        nodes = soup.select("h4.entry-title a")
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
                        "author": "moneymorning",
                        "pub_date": util.current_time_string(),
                        "source": "moneymorning",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    # 403 Forbidden
    # util.execute_with_timeout(run, "https://moneymorning.com/all-posts/")
