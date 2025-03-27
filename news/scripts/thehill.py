# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": '_pxhd=c029f7692718be4a29f42ba7a1f8ec6e01ee3099b2bf1fa2409dfc1e40937f06:f4346e89-ea9e-11ef-95c1-f6c22795b593; pxcts=f78983a9-ea9e-11ef-93a3-0168562e4a1d; _pxvid=f4346e89-ea9e-11ef-95c1-f6c22795b593; referralId=Nexstar Referral; last_visit_bc=1739515411692; _cb=DoKmEvC9SLNOBF2rQ7; _chartbeat2=.1739515411765.1739515411765.1.D58U_kDU9_pYDWy49ywtF76Dqtkji.1; _cb_svref=https%3A%2F%2Fthehill.com%2Fnews%2F; minUnifiedSessionToken10=%7B%22sessionId%22%3A%22056946017c-63517b3abf-111cc4de89-cfa94bedcd-1ae95bce38%22%2C%22uid%22%3A%22ad9134940e-ac83556b62-f4e19e6919-a7403776b5-629dca219e%22%2C%22__sidts__%22%3A1739515411859%2C%22__uidts__%22%3A1739515411859%7D; minVersion={"experiment":288997026,"minFlavor":"headlinesmi-1.17.1.140.js100"}; _px2=eyJ1IjoiMDEwZTlmZDAtZWE5Zi0xMWVmLTk4ZmEtMmJhM2VkODhlNTZhIiwidiI6ImY0MzQ2ZTg5LWVhOWUtMTFlZi05NWMxLWY2YzIyNzk1YjU5MyIsInQiOjE3Mzk1MTU3MTIyMjksImgiOiI3MjZmYjA0NjNlOTgyM2JjYWQ1NTFhYmQ5YTQ3ZWQ0MzBkZmQ4MjRhOWUwNDAxZTQzMmRkNmJmNGVjOWY2YWJjIn0=; usprivacy=1---; seg_sessionid=50819d92-6918-43a7-9758-efcf714ab5ba; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.755637220.1739515413; _gid=GA1.2.1049908157.1739515413; repeat_visitor=1739515413937-804410; bob_session_id=1739515413937-306104; BCSessionID=2ffec1be-f446-41d2-8cea-5de04e7e8678; permutive-id=ff3d491c-1956-42d3-acff-fc80d36d319e; sailthru_pageviews=1; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_cluster=sgp3; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_identity=CiY2OTM0MjExNzUyMTYzNjI0MjE0MDEyNzE2ODEwMDg2OTYwMzI0MlITCPe3y5nQMhABGAEqBFNHUDMwAPAB97fLmdAy; sailthru_content=e8b25caad75cd79293442f3d1a30c1fa; sailthru_visitor=999fae57-3397-4e44-a73c-03dae5ce23a6; OTGPPConsent=DBABBg~BUUAAAGA.QA; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Feb+14+2025+14%3A43%3A55+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7431f159-f7b3-4132-8b41-b19f16a37a93&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fthehill.com%2Fnews%2F&GPPCookiesCount=1&groups=C0001%3A1%2CSPD_BG%3A0%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0',
}
base_url = "https://thehill.com/news/"
filename = "./news/data/thehill/list.json"


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select(".article__text")[0]

            ad_elements = soup.select(".ad-unit,.hardwall, style, script")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error(f"Error fetching detail for {link}: {str(e)}")
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        response = requests.get(
            "https://thehill.com/wp-json/lakana/v1/template-variables/",
            headers=headers,
            proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            posts = response.json()["sidebar"]["just_in"]
            for index in range(len(posts)):
                if index < 3:
                    post = posts[index]
                    kind = post["post_type"]
                    id = post["id"]
                    title = post["title"]
                    link = post["link"]
                    if link in ",".join(links):
                        util.info("exists link: {}".format(link))
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
                                "pub_date": util.current_time_string(),
                                "source": "thehill",
                                "language": "en",
                            },
                        )
            if len(articles) > 0 and insert:
                if len(articles) > 10:
                    articles = articles[:10]
                util.write_json_to_file(articles, filename)
        else:
            util.log_action_error(f"request error: {response.status_code}")
    except Exception as e:
        util.log_action_error(f"request error: {str(e)}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
