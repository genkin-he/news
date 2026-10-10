# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re

from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

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
    "cookie": "_ga=GA1.1.1337123095.1733714167; _ga_PSJPX029ZD=GS1.1.1733714174.1.1.1733714184.50.0.0; __utmc=249121560; __utmz=249121560.1733716728.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga_DGFECMB23C=GS1.1.1733727133.2.1.1733728036.60.0.1084214287; __utma=249121560.1337123095.1733714167.1733727133.1733729522.3; __gads=ID=efb162d568e6d6ef:T=1733729522:RT=1733729522:S=ALNI_MZjciaYrJHBG_HwG0QNsmJQmAQJvA; __gpi=UID=00000f88083c771a:T=1733729522:RT=1733729522:S=ALNI_MZ5ARL5oYNWyGcCV-QRnql_WrhFjQ; __eoi=ID=30eef4c424fb5f79:T=1733729522:RT=1733729522:S=AA-AfjaxFDCGxRwMnCLYx5M4ADdP; __utmt=1; __utmb=249121560.3.10.1733729522; _ga_W7LD8LPV2V=GS1.1.1733729510.2.1.1733730689.60.0.0",
}

base_url = "https://finance.now.com/"
filename = "./news/data/now/finance_list.json"
current_links = []

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。原实现两处 urlopen
# 均未设 timeout（默认无限等待），慢一次就把整轮拖死且零产出。
REQUEST_TIMEOUT = 3  # 1 次列表 + 最多 5 次详情，配合下方截止检查落在预算内


def get_detail(link):
    """详情页结构不符合预期时返回空串，由调用方跳过该条

    列表里混有视频等没有 .newsParagraphs 容器的稿件，原实现直接对 find() 的结果
    调 .select()，一旦返回 None 就抛 AttributeError 并中断整轮采集——日志里那条
    每轮必现的 "AttributeError: 'NoneType' object has no attribute 'select'" 即此。
    """
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status != 200:
        util.error("request: {} error: {}".format(link, response.status))
        return ""

    resp = response.read().decode(
        response.headers.get_content_charset() or "utf-8", errors="ignore"
    )
    body = BeautifulSoup(resp, "lxml")
    soup = body.find(class_="newsParagraphs")
    if soup is None:
        util.info("content not found, skipped: {}".format(link))
        return ""

    ad_elements = soup.select(".ad")
    # 移除这些元素
    for element in ad_elements:
        element.decompose()
    content = str(soup).strip()
    if not soup.get_text(strip=True):
        util.info("content empty, skipped: {}".format(link))
        return ""
    return content


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        # 返回体是 callback([...]) 形式的 JSONP；原实现用 eval 执行远端字符串，
        # 且只截到第一个 ")"，正文出现半角括号即会截断。改为按最后一个 ")" 取 JSON。
        items = json.loads(body[body.index("(") + 1 : body.rindex(")")])
        for index in range(len(items)):
            if index > 4 or util.out_of_time():
                break
            id = items[index]["id"]
            title = items[index]["title"]
            link = "https://finance.now.com/news/post.php?id={}".format(id)
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
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
                        "source": "now_finance",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://finance.now.com/news/newsList.php?type=world")
