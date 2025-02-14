# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib.request
import json
import re
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"133.0.6943.54"',
    "sec-ch-ua-full-version-list": '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.54", "Chromium";v="133.0.6943.54"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "FCNEC=%5B%5B%22AKsRol_eDpEA_V1zODZ5cP8foqFxv5v32VEpXtLs3S0J7QfXIWAuhRJnKWjeBM-sGRIRGSW8hu0SpIUQFHwTU1SHkKjqjK_f06nIuPtWXWxmJKeEGao1oJZXkfNwAng3q0_i3HsDfbFG8-xMdNked2Gh3wOESLpaTQ%3D%3D%22%5D%5D; _ga_NFBGF6073J=GS1.1.1739524966.1.0.1739524966.60.0.1990201687; _ga=GA1.2.1379057177.1739524966; _gid=GA1.2.1661605128.1739524966; _gat_G-NFBGF6073J=1; __adblocker=false; cf_clearance=pM8ccQ6BkfJCJpyL4GoVqrRLqBv5RGTwgSkMPtPOAvk-1739524968-1.2.1.1-LUwErw5bUBPA91E8jOf56E59HI6s61r.wNcdZIj87qaWYldWhEndwYHgQFyOomJeAjFb8XfqlGCOQxWfSygHQgCfRAanlQmR34bCZZocZWwhAvu4JB0B_Waq7zoTZhoR8Vr7p_BvQjJq7w3RLs93HNJ0KBL3ZPlqvPwD68vh1ZOtD1L_xrYd_nvOp.OPNcg2E9_fDowWIQ6h9msKr6LJekSiLlzPk8xionCGvWH9uIc0Obuwg5zmfpc5br8zuUPn9iBNmXKdqwIuse70ERhHqf5BAB8XYjEIzhvJC78x2t480I7baH0Plu.GidcGbc4kiex3.BwYBEXYwTZKlZDV5w; __qca=P0-2106094176-1739524967455; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m74k991785pdz69y%22%7D; __pnahc=0; __tbc=%7Bkpex%7Df-HxklQEqGvBn92XlUqpss2WUqZJRxQOYHla99OU-45TRRif_AqPojRPKKlo0Foa; __pat=-18000000; __pvi=eyJpZCI6InYtbTc0azk5MWRpdHV6aGRhMiIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTczOTUyNDk3ODc5MH0%3D; xbc=%7Bkpex%7D0XPQ6JvKr8t1-cfaESUdGA_-iTexBy0K4O9DcGEtJb8; cX_P=m74k991785pdz69y",
}

base_url = "https://www.etf.com/news"
filename = "./news/data/etf/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    print("etf link: ", link)
    current_links.append(link)

    try:
        response = requests.get(
            link, headers=headers, proxies=util.get_random_proxy(), timeout=10
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select(".etf_articles__body")[2]
            ad_elements = soup.select(".caas-da")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            print("etf request: {} error: ".format(link), response.status_code)
            return ""
    except Exception as e:
        print(f"Error fetching detail for {link}: {str(e)}")
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(
            link, headers=headers, proxies=util.get_random_proxy(), timeout=10
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select(".image-card")
            for index in range(len(items)):
                if index > 0:
                    break
                link = items[index].select(".image-card__title > a")[0]["href"].strip()
                if link != "":
                    link = "https://www.etf.com{}".format(link)
                title = items[index].select(".image-card__title > a")[0].text.strip()
                if link in ",".join(_links):
                    print("etf link exist: ", link)
                    break
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
                            "source": "etf",
                            "kind": 1,
                            "language": "en",
                        },
                    )

            if len(_articles) > 0 and insert:
                if len(_articles) > 10:
                    _articles = _articles[:10]
                util.write_json_to_file(_articles, filename)
        else:
            print("etf request error: ", response.status_code)
    except Exception as e:
        print(f"Error in run function: {str(e)}")


try:
    run(base_url)
except Exception as e:
    print("etf exec error: ", repr(e))
    traceback.print_exc()
