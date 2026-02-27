# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "Accept-Language": 'en-US',
    "Cache-Control": 'max-age=0',
    "Connection": 'keep-alive',
    "If-None-Match": 'i0LYUFs62LdYPOLwS_2U8mfW8Ns',
    "Sec-Fetch-Dest": 'document',
    "Sec-Fetch-Mode": 'navigate',
    "Sec-Fetch-Site": 'none',
    "Sec-Fetch-User": '?1',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": 'macOS',
    "cookie": 'jiyakeji_uuid=9cfddc10-8fc4-11f0-a9a8-f5c7047ebab3; __gads=ID=05f6f101c02795ca:T=1757673516:RT=1757673516:S=ALNI_Mbo5x1YQankuHcYBIbVTSj6LzuZGQ; __gpi=UID=00001195a5c8743a:T=1757673516:RT=1757673516:S=ALNI_MYl0i23TpOXSjeStBNqwMjv_zO9rg; __eoi=ID=c9976ee070a09fb3:T=1757673516:RT=1757673516:S=AA-Afja9-SjG_goMm8Rt0iXHbt_O; _gid=GA1.2.988872428.1758075534; .AspNetCore.Antiforgery.wWi1NWp-qSk=CfDJ8AcfkeD-pgtNpJNZLDjI3Y9otBkFPpo2cg3GXQCLvG_6bY6zoQ1ZQaTBrXbULbLzwBlr7T7gaCXnogJDmc4_jZNA1ggp_UEJRDcH-odjZxboEnoCSjODrFh-S2b6wEJUGhjTpgSq3JY11LMpFGGxAbQ; _ga_HSL1JCKFJ5=GS2.1.s1758076056$o3$g0$t1758076056$j60$l0$h0; _ga=GA1.2.2077495988.1757673502; FCNEC=%5B%5B%22AKsRol8HW_r4xMmGc2esiA7vuVmbHz7KY57q_kXL0zZqBOi5fsZ3cLPA-0uISrFzOAIqPvUHNmzBv6UwbmAEBhs43vYDrBFFn1fS0-ywfSGy7jwSGqNxNqrM09TtvjJG1WakkMvsMFAE3ubcmnVcB91NJvd1h5ABhA%3D%3D%22%5D%5D',
}

base_url = "https://vietnamnews.vn"
base_path = "./news/data/vietnamnews/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8", errors="ignore")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one("#abody")
        if not soup:
            return ""
        ad_elements = soup.select("div, table, .picture")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        result = str(soup).strip()
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    file_path = base_path
    data = util.history_posts(file_path)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".l-content article h2 a")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 3:
                break
            a = items[index]
            link = a["href"].strip()
            title = a.text.strip()
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
                        "source": "vietnamnews",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, file_path)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://vietnamnews.vn/economy-business-beat")
