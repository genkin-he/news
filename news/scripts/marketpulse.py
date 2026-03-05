# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": 'dctraffic=direct / none; csrftoken=k4973fbNGWwbGdihpc6kcqgUQLET16t8; _omappvp=YsbwYBQpJIuWlOv7IwRfHTQch2M4CeywG5ZGpg5iDJoMfx1Kxz8wQBisqMd6VsZcEuOYzp01JxanubPbqgQzTrH8Tbk5ooeG; _gcl_au=1.1.2012990157.1761901591; _ga=GA1.1.415933719.1761901591; OptanonAlertBoxClosed=2025-10-31T09:06:33.621Z; _svtri=095b9990-97d1-42a8-98bc-7899168cf001; optimizelyR42=095b9990-97d1-42a8-98bc-7899168cf001; _hjSessionUser_3390629=eyJpZCI6ImQ5ODM3MjU0LTI5ZjEtNTY1Yy04ZTA4LTdhMjI4ODA0OTIxMiIsImNyZWF0ZWQiOjE3NjE5MDE2MDM3MjQsImV4aXN0aW5nIjp0cnVlfQ==; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Nov+03+2025+14%3A15%3A19+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202501.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=1a91c4a7-7b8d-4191-bc91-c5df007fdea4&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1&intType=1&geolocation=CN%3BSC&AwaitingReconsent=false; _hjSession_3390629=eyJpZCI6IjE5ODk0YWZjLTU0M2ItNGYyYi05OTUwLTA1NzQyMTgxNjBkYSIsImMiOjE3NjIxNTA1MTk5OTEsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; _svlet=1762150522018; _svs=%7B%22c%22%3A%7B%221%22%3Atrue%7D%2C%22ct%22%3A1761901598951%2C%22p%22%3A%7B%220%22%3A1762150522019%2C%226%22%3A1762150522022%2C%227%22%3A1762150522021%2C%223002%22%3A1761901598953%2C%224242%22%3A1762150131161%7D%7D; _ga_Q2HXMSGECM=GS2.1.s1762150130$o2$g1$t1762150548$j30$l0$h0',
}
base_url = "https://www.marketpulse.com"
filename = "./news/data/marketpulse/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = requests.get(link, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one('.post-body')

            ad_elements = soup.select("link, script, style, .anchor-offset, .block-post_content_disclaimer")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        all_items = []
        urls = [
            "https://www.marketpulse.com/news/ai/",
            "https://www.marketpulse.com/markets/crypto/",
            "https://www.marketpulse.com/markets/stocks/",
            "https://www.marketpulse.com/markets/daily-market-wraps/",
        ]
        for url in urls:
            response = requests.get(
                url, headers=headers, timeout=5, proxies=util.get_random_proxy()
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                items = soup.select("a.item-title")
                for index in range(len(items)):
                    if index >= 3:
                        break
                    link = items[index]["href"].strip()
                    title = items[index].get_text().strip()
                    all_items.append({
                        "link": link,
                        "title": title.strip(),
                    })
            else:
                util.error("request url: {}, error: {}, response: {}".format(url, response.status_code, response))

        for index, item in enumerate(all_items):
            link = item["link"].strip()
            title = item["title"].strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
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
                        "source": "marketpulse",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)
