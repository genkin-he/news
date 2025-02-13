# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
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
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"131.0.6778.205"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "FCNEC=%5B%5B%22AKsRol95w-Wvep60KMALNAyFFz6mj0cyaGyfXJOmsCmmajTrp4jfw4EfjjTXl4Hht7aRdc4U94MFpM12vlXWJDw7PwT2dldwv8Xk6y1HEDjajYvkMccaZyxG4c-OocNYhtNPe-Ols8du_JpQx15pvXOuquW2hJFjGw%3D%3D%22%5D%5D; _ga_NFBGF6073J=GS1.1.1735810275.1.0.1735810275.60.0.1668651610; _ga=GA1.2.40528344.1735810275; _gid=GA1.2.476376437.1735810275; _gat_G-NFBGF6073J=1; __adblocker=false; cf_clearance=fvF_r1Ozat9qC9NLRg_KB2mcJkJUB0EU.eKtqL8Llrw-1735810276-1.2.1.1-MX03uPD5weuksWgTzCJV9aGX.YiLDbrMg8bcngHrEPQr89cwx1dNKfnMXHh8l2NRHUrtfOkk6GYheN.oOxulC_lgWbR1WR7op6ZuCysu5KCayaV8IexTLEv7mJI4yGLzcrjoYbV7FMZ.DHAoN1VcY3KVdouXH5.jLAatQ0spSj4z7_mjMyO.OtfywEY6ioZl6eb8LgnFA9wAu.Gjtv2zK2C3vg0WGrgmqBquQrUu9IpRHo_sRnvklo10sVsTg._RZxm1leK7cd2jELDWu602lYPl1.1uB_VxEwcuAekZsGC5ZfUlXs6.BQ6UEPmavPIX9UTyPAn3X6ZyYqaSuZzNwqogir80oFM1EEfWR6UPHA.4RA8P9k6.ncSKDlC7PWnZV4NWU9_QS1njCeEtEyuIjzXDqExYil37O47PqvNWaCOV52KA_jvMPa_Gura8cjC1; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m5f4mdda5uysuwif%22%7D; __pnahc=0; __tbc=%7Bkpex%7D5Emi2w1yQWK9W5RdgtfI5ix2g0upckZAn0zNMPeXK0xTRRif_AqPojRPKKlo0Foa; __pat=-18000000; __pvi=eyJpZCI6InYtbTVmNG1kZGR4aDhhYjN1bSIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTczNTgxMDI3NzMzN30%3D; xbc=%7Bkpex%7DVXZoI1PSquTiIXwvctpw9A_-iTexBy0K4O9DcGEtJb8; __qca=P0-1859494904-1735810276629; cX_P=m5f4mdda5uysuwif",
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
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".etf_articles__body")[2]
        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("etf request: {} error: ".format(link), response)
        return ""


def run(link):
    data = util.history_posts(filename)
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
        print("etf request error: ", response)

try:
    run(base_url)
except Exception as e:
    print("etf exec error: ", repr(e))
    traceback.print_exc()


