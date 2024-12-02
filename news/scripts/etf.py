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
    "cookie": "cf_chl_rc_ni=1; cf_clearance=ZgZVU7C01MKrIdQHu3EpB9R.MdySjJo72YwfsiYpFq8-1730281799-1.2.1.1-Mna8rB7Pq8ppyEkIk0_LjoRKMlC9DkYSoveXegMKhJrVJJohRFiBMweLkLb7JUozPi2JHj0xUIFs0zONYPqc2EGv.froQ9NgNXvugrdJ3Rj0PzSvX1mlJsjAqPCKWxmUoYBivrkUYeO6L992yOeOZMf3VvtZoRS9Qrak8wT6Z5LOvCfNk_6BZXtxau57sdt.GR7z9otuVGvruWTgiThbEyfWw96R36aFmBpvN5u3rKaHWt9btQoy0GuO13BYnxtIf5o6e5dNb1yG1aqwmLuEtCrco9qEjRJzmUb1PjAfU8ofsLqPqhDP5o_N0DK0kyItpmp8EId.fBmhx910Ay93i2tKJZdz7fRqPdIVVWhAuDzS6GJBD26uZlv2m12fyT3oNBJsaU8eLLyArvIWhEqS7Q; _gid=GA1.2.684941037.1730281801; __qca=P0-1979653068-1730281799275; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m2vp4276uwcs563y%22%7D; __pnahc=0; __pat=-14400000; cX_P=m2vp4276uwcs563y; cX_G=cx%3A1iyu0v5olso5116s1q5p1yd6t0%3A21bfik1fsces5; _ga_NFBGF6073J=GS1.1.1730281799.1.1.1730282163.60.0.0; _ga=GA1.2.2143324818.1730281799; _gat_G-NFBGF6073J=1; __adblocker=false; FCNEC=%5B%5B%22AKsRol_8460L2Mg1MmFmkPTWwuQpQH-6j5PK9OeJERjyOqZoYhM8inD2KE7sUOYHyQYTjOTVOdZxRwl0L8LYHPuujiuubsglN3QVhWDc4rRMFf31brHHe5rENXVZWaYNxLGVhMRTexXsheBq9lw2yKfEoUhSJomr5A%3D%3D%22%5D%5D; __pvi=eyJpZCI6InYtbTJ2cDQyN2Q2cjRnbWgybiIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTczMDI4MjE2NTkyNH0%3D; __tbc=%7Bkpex%7DW_VX3UsmV5EddnixgTUbZl4CNkbL-V7C-X2vwvsJ4MRTRRif_AqPojRPKKlo0Foa; xbc=%7Bkpex%7DC9o1I6PyeQKAwzEu1PmgItKDHNo6Gs1tuGi-IY5jMxBJ6nlQCI0n9Zqui79mrSXWJTPIvmQF92gRi2lwO-CYZw_-iTexBy0K4O9DcGEtJb8",
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
