# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "accept": "*/*",
    "accept-language": "en",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://www.coinlive.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.coinlive.com/"
filename = "./news/data/coinlive/list.json"
util = SpiderUtil()

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。原实现这次请求
# 没设 timeout（requests 默认无限等待），接口一卡就整轮被外层强杀且零产出
# （CI 日志里只有一行 "start executing..." 紧跟 "timeout: still running after 10s"）。
REQUEST_TIMEOUT = (3, 4)  # (connect, read)；再由 request_timeout 按剩余预算收敛
# 接口从 GitHub 的美国 runner 打过去经常读超时（本机 0.4 秒返回），但并非全天不可用，
# 当天仍有正常出稿。预算够就换一条新连接再试一次，能把一部分偶发超时救回来。
ATTEMPTS = 2

list_url = "https://api.coinlive.com/api/v1/news-letter/list?page=1&size=10"


def fetch_list():
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        if attempt > 1 and util.out_of_time(reserve=5):
            break
        try:
            return requests.get(
                list_url,
                headers=headers,
                timeout=util.request_timeout(REQUEST_TIMEOUT),
            )
        except Exception as e:
            util.info(f"list attempt {attempt}/{ATTEMPTS}: {e!r}")
            last_error = e
    util.log_action_error(f"request error: {last_error!r}")
    return None


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = fetch_list()
    if response is None:
        return
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["list"]
        for index, post in enumerate(posts):
            if index < 4:
                id = post["id"]
                title = post["title"].strip()
                link = post["url"]
                description = post["brief"].strip()
                pub_date = util.convert_utc_to_local(post["published_at"])
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                if description:
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "coinlive",
                            "kind": 2,
                            "language": "en",
                        },
                    )
        if articles and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
