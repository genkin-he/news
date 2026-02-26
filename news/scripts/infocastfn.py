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
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "pragma": "no-cache",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "JSESSIONID=B4DE08CF397666C735B9EF2C9B605FF8; GUEST_LANGUAGE_ID=en_US; COOKIE_SUPPORT=true; lang=en_US; _gid=GA1.2.1188327090.1736328583; _gat_gtag_UA_62880165_3=1; __utma=226899781.2113019888.1736328583.1736328583.1736328583.1; __utmc=226899781; __utmz=226899781.1736328583.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmv=226899781.Member; __utmt_~2=1; __utmb=226899781.6.10.1736328583; _ga_Z5M39XPJM0=GS1.1.1736328582.1.1.1736328585.0.0.0; _ga=GA1.1.2113019888.1736328583",
    "Referer": "https://www.infocastfn.com/web/guest/infocast-news",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://www.infocastfn.com"
filename = "./news/data/infocastfn/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select("#newsBody")[0]

        ad_elements = soup.select(".ad")
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
    data = b"sEcho=5&iColumns=3&sColumns=datetime%2Cheadline%2Cid&iDisplayStart=0&iDisplayLength=20&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&bSortable_0=true&bSortable_1=true&bSortable_2=true&jcomparatorName=com.infocast.iweb.comparator.news.NewsJComparator&locale=zh_CN&numProcessingRec=&searchCriteria=%7B%22type%22:%22%22,%22stockCode%22:%22%22,%22grpCode%22:%22NwsType%22%7D"
    request = urllib.request.Request(
        "https://www.infocastfn.com/fn/ajax/news/InfocastNewsJsonResult",
        data=data,
        headers=headers,
        method="POST",
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        nodes = json.loads(resp)["aaData"]
        for node in nodes:
            if post_count >= 4:
                break
            link = "https://www.infocastfn.com/fn/ajax/news/newsDetail?newsId={}&locale=zh_CN".format(
                node[2]
            )
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = node[1]
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
                        "source": "infocastfn",
                        "kind": 2,
                        "language": "zh-CN",
                        "id": node[2],
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        util.error("exec error: {}".format(repr(e)))
        traceback.print_exc()
