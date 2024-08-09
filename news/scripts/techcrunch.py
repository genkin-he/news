# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import urllib.request  # 发送请求
import json
from util.util import history_posts
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'A1=d=AQABBOCtqWYCEBf3q_NUfFxL6uyQL9EUgpgFEgEBAQH_qmazZivg7L8A_eMAAA&S=AQAAAksQqYdWCIyyOhhHbywqFPY; A3=d=AQABBOCtqWYCEBf3q_NUfFxL6uyQL9EUgpgFEgEBAQH_qmazZivg7L8A_eMAAA&S=AQAAAksQqYdWCIyyOhhHbywqFPY; A1S=d=AQABBOCtqWYCEBf3q_NUfFxL6uyQL9EUgpgFEgEBAQH_qmazZivg7L8A_eMAAA&S=AQAAAksQqYdWCIyyOhhHbywqFPY; _ga=GA1.1.515206287.1722396153; cmp=t=1722396153&j=0&u=1---; gpp=DBAA; gpp_sid=-1; _gcl_au=1.1.1920270479.1722396153; axids=gam=y-l7sKBcxE2uIboQaGBwDaEPNiNyQ5esxG~A&dv360=eS1iNHl6bnFoRTJ1R0VHRmgwMkRoSk9FcXBHZzJOb1FRQ35B&ydsp=y-kIVd65dE2uJ1eErCpVziGcU0291kIlEQ~A&tbla=y-y82zLGtE2uLOoqAFAr_5lHI3zl4kgbxS~A; tbla_id=e34b6b67-19b7-4bc9-96ed-ececa769c2d1-tuctda3337b; _ga_KJR3C2ZQN6=GS1.1.1722396678.1.1.1722396727.11.0.0; ___nrbic=%7B%22isNewUser%22%3Atrue%2C%22previousVisit%22%3A1722396727%2C%22currentVisitStarted%22%3A1722396727%2C%22sessionId%22%3A%221741fe94-409c-40a9-9556-51a4f45ce66f%22%2C%22sessionVars%22%3A%5B%5D%2C%22visitedInThisSession%22%3Atrue%2C%22pagesViewed%22%3A1%2C%22landingPage%22%3A%22https%3A//techcrunch.com/%22%2C%22referrer%22%3A%22%22%7D; ___nrbi=%7B%22firstVisit%22%3A1722396727%2C%22userId%22%3A%22cc9f70ae-366a-4b1e-9183-a14fc57e0573%22%2C%22userVars%22%3A%5B%5D%2C%22futurePreviousVisit%22%3A1722396727%2C%22timesVisited%22%3A1%7D; compass_uid=cc9f70ae-366a-4b1e-9183-a14fc57e0573; __hstc=16024617.1b0a38119aa9fe799bc8e5b37c6a3373.1722396729481.1722396729481.1722396729481.1; hubspotutk=1b0a38119aa9fe799bc8e5b37c6a3373; __hssrc=1; __hssc=16024617.1.1722396729482',
}

base_url = "https://techcrunch.com/"
filename = "./news/data/techcrunch/list.json"
current_links = []
post_count = 0

def get_detail(link):
    if link in current_links or "/video/" in link:
        return ""
    print("techcrunch link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, 'lxml')
        soup = soup.select(".entry-content")[0]
        
        ad_elements = soup.select('.ad-unit, .marfeel-experience-inline-cta, .wp-block-tc23-podcast-player')
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup)
    else:
        print("techcrunch request: {} error: ".format(link), response)
        return ""
    
def run():
    post_count = 0
    current_links = []
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        base_url, None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, 'lxml')
        nodes = soup.select(".wp-block-tc23-post-picker")
        for node in nodes:
            if post_count >= 3:
                break
            link = str(node.select(".wp-block-post-title > a")[0]['href'])
            title = str(node.select(".wp-block-post-title")[0].text)
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
                        "author": "TechCrunch"
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("techcrunch request error: ", response)


try:
    run()
except Exception as e:
    print("techcrunch exec error: ", repr(e))
    logging.exception(e)
