# -*- coding: UTF-8 -*-
import logging
import traceback
import json
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

# 使用 curl_cffi 模拟 Chrome 以绕过 403（TLS/JA3 指纹）
IMPERSONATE = "chrome124"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'advanced-frontend=342b31b2d0e2c8e6db61b5f6574efd47; _csrf-frontend=a1dca0d07d7ca7c888c6f82f022b8a53da115223f5613ff6c035d90269e84621a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22uY_VJmDvJwt738TowZunwrbPWSWxPjwS%22%3B%7D; Hm_lvt_e7e035075002bfbbfb97dd1986670572=1772415825; HMACCOUNT=3D0D96D90A2577B0; Hm_lpvt_e7e035075002bfbbfb97dd1986670572=1772415904',
}

base_url = "https://lieyunpro.com/"
filename = "./news/data/lieyun/list_live.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = curl_requests.get(
        "https://lieyunpro.com/news",
        headers=headers,
        impersonate=IMPERSONATE,
    )
    if response.status_code == 200:
        resp = response.text
        soup = BeautifulSoup(resp, 'lxml')
        nodes = soup.select(".news1-item")
        for node in nodes:
            share_url = str(node.select("img")[0]['src'])
            if "qrcode?url=" not in share_url:
                continue
            link = str(node.select("img")[0]['src']).split("qrcode?url=")[1]
            title = str(node.select(".news1-title")[0].text)
            description = str(node.select(".news1-content")[0].text)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "lieyun",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )

        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {} {}".format(response.status_code, response.reason))

if __name__ == "__main__":
    # util.execute_with_timeout(run)
    util.info("403 Forbidden")
