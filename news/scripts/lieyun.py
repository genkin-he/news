# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'advanced-frontend=2ceddaa63b9959f86a9f043376312796; _csrf-frontend=d5acdf8ebfc74d7efcb6e2647d00fca383be706ae79dc90c1ec15e392f1b4db2a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22mXtTM0vQZ8LuCgcNSDFTsCWb4fvdd7ic%22%3B%7D; Hm_lvt_e7e035075002bfbbfb97dd1986670572=1721976448; HMACCOUNT=8FD891EC62D343DC; 206efde5-6c70-4bb4-aeaa-66ae6d9b05ed=38e645d02a937c761022703766c0c83e; Hm_lpvt_e7e035075002bfbbfb97dd1986670572=1721979054',
}

base_url = "https://lieyunpro.com/"
filename = "./news/data/lieyun/list_live.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://lieyunpro.com/news", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
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
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
