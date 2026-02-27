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
    "cookie": "_gid=GA1.2.340515276.1734940560; __cf_bm=_R5Y6LfHsRqg1sGHKkhu9i9SQ9xJXeYCNlru6SZ3YlE-1734942393-1.0.1.1-sydkzz.3lDlQjxy5spCwMP2pu1UrJkSwoaZUwbbQp9mT4ETnjfR6wxSWeovL1R3kGlhPd_JcnRRpnEcuynJUow; cf_clearance=AlysIBzrreLVf_4riHd9Fc6uGik9hi_CQA7ZaDML6y0-1734942393-1.2.1.1-8YCySKL4Qca28sUbTQRmBI4Rbj3ItrciaZf3knXYqaBTvTFZNKrWhC26h7kCZ1BX9Bjo6uHy6oJygjv4tK7yw6JWlA8dCdICcy7ANkF7ruJ8jvyrO0t2O8VC4dvy_ogJMju4xG5GuV4LbIWd1RNFu6O4PsU0Ivhzoqf_Ia5_0eTBQfmlFj0cLfsBmxHJGzFCF49Z0BXfOJrvuNiicvF0XkeHT1kzsp46WAsGPNY10U9lHjoi3iAZ0npYvZ4B.Yru5d3w7RedjFFj92vIa2ztNevoNu4vvq87BNgrGgTJbIcIh74dgBHQCrZ4lx5CoMBNC3_Yb9QHtFiha.na8sPmRxp9WaP9pPXbM1d60ZDzmF.jRVuYkNt8OFFXV9AHDyXbcqQHUSufV34XUo1HdJvQxg; _sws_ses.1740=*; plans_variant=control; _hjSessionUser_44113=eyJpZCI6ImZkZDFjM2ZhLTQ4OWQtNTY4OC1iNGIxLTU2YTQ4OTZlMTlkOSIsImNyZWF0ZWQiOjE3MzQ5NDA1NDQ4MjksImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_44113=eyJpZCI6ImJiYjZmZDYyLThhMjMtNDA0Yi05OWI4LTJjOWIyOTFlM2YzNCIsImMiOjE3MzQ5NDIzOTU0MDYsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; _sws_flagsessid=295943768; _sws_id.1740=8bb87ebb-492a-4664-bf92-7ed86c9fcf8b.1734940544.2.1734942474.1734940560.80fe427d-5479-438b-a2df-7fab2e739055; _ga_YXRWTP2MC7=GS1.1.1734940543.1.1.1734942474.41.0.0; _ga=GA1.1.869530380.1734940543; _ga_DQKZK4J4W2=GS1.2.1734942425.2.1.1734942474.11.0.0; _ga_VNZZ8E7MPM=GS1.2.1734942395.2.1.1734942474.42.0.0; _dd_s=rum=0&expire=1734943434298",
}

base_url = "https://simplywall.st/"
filename = "./news/data/simplywall/list.json"
post_count = 0
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one('div[data-cy-id="article-content"]')
        ad_elements = soup.select("figure, div")
        # 移除 soup 子标签中最后一个 p 标签和 最后一个 div 标签
        last_p = soup.find_all('p')[-1]
        if last_p:
            last_p.decompose()

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

    # request 中放入参数，请求头信息
    request = urllib.request.Request("https://simplywall.st/news", None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select('div[data-cy-id="list-article"] > article')
        for node in nodes:
            if post_count >= 5:
                break
            link_el = node.select_one("div:first-child > a")
            title_el = node.select_one("div:nth-of-type(2) h2")
            if not link_el or not link_el.get("href") or not title_el:
                continue
            link = str(link_el["href"]).strip()
            title = str(title_el.get_text()).strip()
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
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
                        "source": "simplywall",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
