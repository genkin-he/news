# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
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
    "cookie": '_gcl_au=1.1.2112536696.1734940740; _gid=GA1.2.830825866.1734940740; bspPelcroStatus=loggedOut; pelcro.unique.id=Nm53a3FlZzc4YjNtNTBxeDdiZg==; _hjSession_3517483=eyJpZCI6IjNjNzBhZTVlLTAwOGMtNGRhNC04NDQyLTVkYzkxYjBjODFjMyIsImMiOjE3MzQ5NDA3NDEwNjQsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; pelcroStatus={"loggedInUser":false,"userEntitlement":[]}; messagesUtk=b606d77ad6344a61b3afc3100aacc8ad; __hstc=178906363.8cbc2e459f3ad6e97035686ed16f3c03.1734940744472.1734940744472.1734940744472.1; hubspotutk=8cbc2e459f3ad6e97035686ed16f3c03; __hssrc=1; _hjSessionUser_3517483=eyJpZCI6ImI5ZTRkOGRkLTlkMmUtNTE4Zi1iMDkyLTJmNDlkNDEwNDU2MCIsImNyZWF0ZWQiOjE3MzQ5NDA3NDEwNjMsImV4aXN0aW5nIjp0cnVlfQ==; _clck=15yxlfg%7C2%7Cfry%7C0%7C1818; _gat_gtag_UA_423078_9=1; _clsk=tvv772%7C1734941411528%7C6%7C1%7Cb.clarity.ms%2Fcollect; _uetsid=c49570a0c10311ef936c058b9653974c; _uetvid=c4958690c10311ef8e98e913b21190b1; _ga_H1KNGY0CX2=GS1.1.1734940739.1.1.1734941426.35.0.0; _ga=GA1.2.1148218751.1734940740; __hssc=178906363.11.1734940744472',
}

base_url = "https://www.cabotwealth.com"
filename = "./news/data/cabotwealth/list.json"
post_count = 0

util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = BeautifulSoup(str(lxml.select(".Page-articleBody")[0]).strip().replace("bsp-article-tables", "div"), "lxml").select(".RichTextBody")[0]
        ad_elements = soup.select(".InternalAd")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request("https://www.cabotwealth.com/daily", None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".PageList-items-item")
        for node in nodes:
            if post_count >= 2:
                break
            link = str(node.select(".PagePromo-title > a")[0]["href"].strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = str(node.select(".PagePromo-title > a")[0].text.strip())
            image = str(node.select(".PagePromo-media img")[0]["src"].strip())
            post_count = post_count + 1
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "image": image,
                        "source": "cabotwealth",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
