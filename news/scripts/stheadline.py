# -*- coding: UTF-8 -*-
import logging
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.util import current_time, history_posts
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "AMCVS_E1E31A3C5BB4BED90A495E47%40AdobeOrg=1; s_cc=true; _gid=GA1.2.2097601869.1733396156; _cc_id=b7db9dd6384818769efb04257e82c421; panoramaId_expiry=1734000957218; panoramaId=0830c0c437cb7c5147da21002d20185ca02c2bf47c0a4afdad0d8e31932d2430; panoramaIdType=panoDevice; purecookieDismiss=1; s_sq=%5B%5BB%5D%5D; AMCV_E1E31A3C5BB4BED90A495E47%40AdobeOrg=-1303530583%7CMCIDTS%7C20063%7CMCMID%7C00302968270587971890180144851762103530%7CMCAAMLH-1734070869%7C3%7CMCAAMB-1734070869%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1733473269s%7CNONE%7CvVersion%7C3.3.0; s_pn=%E6%98%9F%E5%B3%B6%E6%97%A5%E5%A0%B1.%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E; cto_bundle=Q3R5N19WSU1rUmhVZnc5bHVmV1NvQWJYTGxBJTJCeEJsT0QzUWttJTJCZjhEdTg2SkpkSHAlMkZOeDNTRWplejBaRDVtdDhUc0x0b3FwSU9rSmNQY2s3ZzZ3bENIR29PRmZ2RGFZbGlNM2ZIRENieGo4d2x3YzhUdkJsQnp5OEJQZGxzTFBjR0lrOGdJTGFpWiUyQkFUZk50bXd3dUJqWFp5cXRkRnJRZ3hPUTlRWktBZHZtZzFrRSUzRA; s_getNewRepeat=1733466116150-Repeat; _ga=GA1.1.119576300.1733396156; _ga_T9RMKL3N37=GS1.1.1733466069.3.1.1733466116.13.0.0; FCNEC=%5B%5B%22AKsRol-HKoacevh4uOu0D4BM47UfAooZ6GK9sTXoOfmkOtSzmL7ApnUHAoWT3TdUoIXgdoMlA4aBokNV-t49Tq6AreaMArQvuOEd3KgHQUrORsn-VHlCIAQum-y1M6Ks3-8rz9bt4QvDW-fSh8N8itwGdeVmHecCIQ%3D%3D%22%5D%5D; tp=2733; s_ppv=%25u661F%25u5CF6%25u65E5%25u5831.%25u5373%25u6642%25u65B0%25u805E%2C53%2C53%2C1455",
}

base_url = "https://std.stheadline.com"
filename = "./news/data/stheadline/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    print("stheadline link: ", link)
    current_links.append(link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode(response.headers.get_content_charset())
        body = BeautifulSoup(resp, "lxml")
        soup = body.find(class_="paragraphs")

        ad_elements = soup.select(".ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("stheadline request: {} error: ".format(link), response)
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
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".latest-updates .media-body")
        for index in range(len(items)):
            if index > 2:
                break
            title_element = items[index].select_one(".title")

            link = title_element["href"].strip()
            title = title_element.text.strip()
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
                        "source": "stheadline",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("stheadline request error: ", response)


try:
    run("https://std.stheadline.com/realtime/%E5%8D%B3%E6%99%82")
except Exception as e:
    print("stheadline exec error: ", repr(e))
    logging.exception(e)
