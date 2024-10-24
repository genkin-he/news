# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import current_time, history_posts
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"129.0.6668.103"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="129.0.6668.103", "Not=A?Brand";v="8.0.0.0", "Chromium";v="129.0.6668.103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "cf_clearance=bn3ZNX7YuOCrB0pVWlqH972Vup7xE8vwbUeI2RoutqI-1729750906-1.2.1.1-xXHYeJSAIqGYwHq_IKhlBJpCnkV62pgKYyt1oYgP918M0SeoZcRmV0j2WN4Tb6_u5YYZY8vP7wMCLRx0CiwnSaFFVfJvwe_ZnsLBbwkIWbc4iz9dGaY6X3sAvPaPIztWbHHW58DwCyA9OAagarcU9pukw2pezug0CVkADANBgcgI7OkNRahiZe8BP_BXsax5.VTp_a9dRkveGZWT3Rm4FYhOJtyttzm8s9ydKlVq6CGM6MvHZ4ZVa4qrRasT3umXv7i9GR8wPMsXaokd7Zs0g8xQwO5js_wdi2NSi5krWgL_kiEZI_OGoeE9Vunv3DyOXl3zSptsPGIiyQiVwynaxr2w6Y.N_20X6emIzRssAjFG8aKSF1JcoxeOSeHddwqgKFuSL5cVmwm51F.Ey2CQAg; __adblocker=false; _ga_NFBGF6073J=GS1.1.1729750906.1.0.1729750906.60.0.0; _ga=GA1.2.714329511.1729750907; _gid=GA1.2.206263124.1729750907; _gat_G-NFBGF6073J=1; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m2mx11ufcklv3hbz%22%7D; __pnahc=0; __tbc=%7Bkpex%7Da1vSLn4D15zkb57e8-s1fF9ABhtwFnW1oEcv8vVfyXxTRRif_AqPojRPKKlo0Foa; __pat=-14400000; __pvi=eyJpZCI6InYtbTJteDExdWx4MHpzaTZjYiIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTcyOTc1MDkwNzc4Nn0%3D; xbc=%7Bkpex%7DRKnfCRF533vcTP8QeRKI1Q_-iTexBy0K4O9DcGEtJb8; cX_P=m2mx11ufcklv3hbz; FCNEC=%5B%5B%22AKsRol-EirP7pCqxRTV7IPmMxhrhj_YvKgCW3_3Yd3EtifutMVylE3cxK5equXckr_1hzkHVLw0u66G55vZ1k7Yf2KyqjS--GQ8FiZJGnTeW_7eB_9C5wov1VtyltjT85PWDcaB1F_nJBSF7n0pCR-bSIRqS2c2FsQ%3D%3D%22%5D%5D; __qca=P0-1663847813-1729750907210; cX_G=cx%3A1iyu0v5olso5116s1q5p1yd6t0%3A21bfik1fsces5",
}

base_url = "https://www.etf.com/news"
filename = "./news/data/etf/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    print("etf link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".etf_articles__body")[1]
        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("etf request: {} error: ".format(link), response)
        return ""


def run(link):
    data = history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".image-card")
        for index in range(len(items)):
            if index > 0:
                break
            link = items[index].select(".image-card__title > a")[0]["href"].strip()
            if link != "":
                link = "https://www.etf.com{}".format(link)
            title = items[index].select(".image-card__title > a")[0].text.strip()
            if link in ",".join(_links):
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
                        "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("etf request error: ", response)


try:
    run(base_url)
except Exception as e:
    print("etf exec error: ", repr(e))
    logging.exception(e)
