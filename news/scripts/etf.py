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
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"130.0.6723.70"',
    "sec-ch-ua-full-version-list": '"Chromium";v="130.0.6723.70", "Google Chrome";v="130.0.6723.70", "Not?A_Brand";v="99.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "cf_clearance=y1fe6hdrDZQoIrpbR15IuGemCgxkx5T68hqZ5zZq1AI-1733108975-1.2.1.1-P2PBswtY12j2qKQj36EEVg1d4Bk2tTT26XBya4yQv5XHTOXZR0XGoSnrnXhv0c1pIcj6B61xvHSrNv7Zo22BIeriR3vn6mSsV22g54vwo.Dr7.f4QbG8_xZPCW8h2rAXWDAfMgpfN1vIzlMPCs1EDKw6JtolVafHTqpkgBN0dRsBRHsquYFXNgQ0BNpgCXyck3VWcX5oJlmRLI5IY6Uxu7vAL8WMSMzq_9mz5P4YNa.a4446Cu24olHEV028oEFb_GpQ9cZrfcbHLUbYyL._btWa1J5mYV5fpNYtGlD1tz21ZxV8FfOjgPZ6J9xrIH3B16QT2iIyeOoWjAsBCj1HE_ULO6GxHbX9KZBKZ7Tr7c0VLHADjTu4kJzZ1G61DDUPlupyTlNI4eedEd.1CbvHVQ; _gid=GA1.2.1069546951.1733108976; __qca=P0-528224901-1733108977006; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m46gc5me7v4wtvf6%22%7D; __pat=-18000000; cX_P=m46gc5me7v4wtvf6; cX_G=cx%3A1g8t3l5qvab522qup6k9oj9ay5%3A1n0exp5fx6zk0; __adblocker=false; _ga_NFBGF6073J=GS1.1.1733108976.1.1.1733108991.45.0.0; _ga=GA1.2.1317551932.1733108976; __pvi=eyJpZCI6InYtbTQ2Z2M1bWxlM3IxMnV2dSIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTczMzEwODk5MTgzN30%3D; __pnahc=0; FCNEC=%5B%5B%22AKsRol_7rRKYQCrTvOZRbNy0GdJW4dijX9NTCQKzfIhRJWl1o5TUuRYtdKcr31lq55DiCsklAqDIje5Z6JrqM5AaNvMZagD5i9UN-NNGXShS3JTBaxH7R8DRnODgNc55GdikAi20nMjgibZP1I6RgDxyfZNtJHRJIQ%3D%3D%22%5D%5D; __tbc=%7Bkpex%7D1pFOv8WiuE0RbZ9zyiuvQOg9J8SDvZEpbie-2zf4vU9TRRif_AqPojRPKKlo0Foa; xbc=%7Bkpex%7DR82PRxdVvn91IOKvhHFQYw_-iTexBy0K4O9DcGEtJb8",
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
                        "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "etf",
                        "kind": 1,
                        "language": "en",
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
