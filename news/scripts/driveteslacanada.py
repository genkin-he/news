# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
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
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "__wpdm_client=7ad49d58b7fd93f272b3fdfded7c748d; wp-dark-mode-device=light; _ga=GA1.1.49754206.1739412603; usprivacy=1N--; _sharedID=0c3c28e9-9598-4d96-9d6a-917290cce38d; wp-dark-mode-choice=light; _ga_P9220DJMHX=GS1.1.1739412602.1.1.1739416095.60.0.0; _sharedID_cst=kSylLAssaw%3D%3D; cto_bundle=8QqYj19MVUdwT2NDNW9TdlVOa2ltSERkJTJCNDZ2T0hKaSUyQmQ3Qkd5MmJoeUtRRTVyVmhuSDBvWFhSYW9hblZuSU41VGl6JTJGUDBHaGdHTUx2OUUyWWdCbVNmRCUyQldNNHc5NWhHVCUyQm9LSjlhSXV2cXFwVGcxM3FyZ2ZaMkltOHVWb1NVNlFxNkI1NmE3eWtCSmglMkJRYSUyRjA1SjBMNDJKTVM3V21MS2ZyaWFWcERJeVZwMHVGayUzRA; cto_bidid=zsBATF9GNTlETU8lMkJlWkFYYTVjR2clMkJtdCUyQkhXYiUyQmFXTHhFcWVHbWZ2ODhqYlJHaXZzQnRFa3FGbGY2d1BabW5wV2slMkIybiUyRjY4N01HSVQlMkZFT1hkanR1eUMlMkZjaFJiR3pOUWF6dlFGVGIlMkJ5R2U3UVJGTEFNMFdCblJGN2tEcW9UUmFHYmFkSA",
}

base_url = "https://driveteslacanada.ca/"
filename = "./news/data/driveteslacanada/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    
    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one('.entry-content')
            
            ad_elements = soup.select("style,script,.code-block,.twitter-tweet")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request failed: {}".format(str(e)))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    response = requests.get(link, headers=headers, timeout=5)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".entry-content article")
        for index in range(len(items)):
            if index > 5:
                break
            link = items[index].select_one(".entry-title > a")["href"].strip()
            
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            title = items[index].select_one(".entry-title > a").text.strip()
            image = items[index].select_one(".entry-thumb img")["src"].strip()
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "image": image,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "driveteslacanada",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
