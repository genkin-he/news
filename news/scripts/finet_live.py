# -*- coding: UTF-8 -*-

import logging
import traceback
import requests  # Changed from urllib.request
import json
import re
import time
from util.spider_util import SpiderUtil


headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "ci_session=15756046187f3017c4dedbed70628509f76c0390; _ga=GA1.1.1437542055.1741571248; Hm_lvt_f5cb0137b11ed6eb8cfe4c83298a2298=1741571248; HMACCOUNT=7E20D69DD237F3AF; Hm_lpvt_f5cb0137b11ed6eb8cfe4c83298a2298=1741571335; _ga_QV63PCW4FX=GS1.1.1741571247.1.1.1741571402.60.0.0",
    "Referer": "https://www.finet.hk/latest/latestnews",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.finet.hk/latest/latestnews"
filename = "./news/data/finet/live.json"
util = SpiderUtil()

def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # Using requests instead of urllib
    response = requests.get(
        "https://www.finet.hk/latest/geteslatest/1/{}".format(int(time.time())),
        headers=headers,
    )

    if response.status_code == 200:  # Changed from status to status_code
        if response.text == None or response.text == "":
            util.info("finet_live response is empty")
            return
        posts = response.json()["data"]
        for _, post in enumerate(posts):
            id = post["id"]
            link = "https://www.finet.hk/newscenter/news_content/{}".format(id)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = post["name_sc"]
            pub_date = post["create_time"]
            # 去掉开头的【财华社讯】
            description = post["description_sc"].replace("【财华社讯】", "")
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "id": id,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                        "source": "finet",
                        "kind": 2,
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
