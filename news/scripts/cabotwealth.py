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

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。原实现两处 urlopen
# 都没设 timeout（默认无限等待），站点一慢就把整轮拖到被外层强杀且零产出
# （日志里的 "timeout: still running after 10s, aborted"）。
REQUEST_TIMEOUT = 3  # 1 次列表 + 最多 2 次详情


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        # 正文容器缺失时跳过该条，原实现直接取 [0] 会抛 IndexError 并中断整轮
        article_body = lxml.select(".Page-articleBody")
        if not article_body:
            util.info("content not found, skipped: {}".format(link))
            return ""
        rich_text = BeautifulSoup(
            str(article_body[0]).strip().replace("bsp-article-tables", "div"), "lxml"
        ).select(".RichTextBody")
        if not rich_text:
            util.info("content not found, skipped: {}".format(link))
            return ""
        soup = rich_text[0]
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
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".PageList-items-item")
        for node in nodes:
            if post_count >= 2 or util.out_of_time():
                break
            title_node = node.select(".PagePromo-title > a")
            if not title_node:
                continue
            link = str(title_node[0]["href"].strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = str(title_node[0].text.strip())
            image_node = node.select(".PagePromo-media img")
            image = str(image_node[0]["src"].strip()) if image_node else ""
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
