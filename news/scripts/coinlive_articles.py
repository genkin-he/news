# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US",
    "authorization": "null",
    "content-type": "application/json",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "x-device-id": "c8c2882a8dbcc714b202e0397e9e22ae",
    "x-platform": "PC",
    "x-project": "1",
    "x-zone": "8",
    "Referer": "https://www.coinlive.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.coinlive.com/"
filename = "./news/data/coinlive/articles.json"
util = SpiderUtil()

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。原实现两处请求都
# 没设 timeout（requests 默认无限等待），接口一卡就整轮被外层强杀且零产出
# （CI 日志里只有一行 "start executing..." 紧跟 "timeout: still running after 10s"）。
REQUEST_TIMEOUT = (3, 4)  # (connect, read)；1 次列表 + 最多 3 次详情
# 接口从 GitHub 的美国 runner 打过去经常读超时（本机 0.4 秒返回），但并非全天不可用。
# 预算够就换一条新连接再试一次，能把一部分偶发超时救回来。
ATTEMPTS = 2
list_url = "https://api.coinlive.com/api/v1/news/list"


def fetch_list(payload):
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        if attempt > 1 and util.out_of_time(reserve=5):
            break
        try:
            return requests.post(
                list_url,
                headers=headers,
                data=bytes(json.dumps(payload), encoding="utf8"),
                timeout=util.request_timeout(REQUEST_TIMEOUT),
            )
        except Exception as e:
            util.info(f"list attempt {attempt}/{ATTEMPTS}: {e!r}")
            last_error = e
    util.log_action_error(f"request error: {last_error!r}")
    return None


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(
            link, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        # 详情页改版或跳到风控页时这两个容器都可能取不到，原实现直接在 None 上
        # 继续 select_one 会抛 AttributeError 并中断整轮
        detail = lxml.select_one("[class^=detail_html]")
        soup = detail.select_one("[class^=share__]") if detail else None
        if soup is None:
            util.info("content not found, skipped: {}".format(link))
            return ""

        ad_elements = soup.select("[class^=share_container], [class^=ad_wrap]")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    body = {
        "symbols": [],
        "page": 1,
        "size": 10,
        "show_position": 2,
        "sort": "published_at",
    }

    # 使用 requests 发送请求。注意 body 才是请求体：原实现传的是 data，
    # 那是上面 history_posts 返回的历史文章字典，等于把本地存量当查询条件发了出去。
    response = fetch_list(body)
    if response is None:
        return
    if response.status_code == 200:
        body = response.json()
        posts = body["data"]["list"]
        for index, post in enumerate(posts):
            if util.out_of_time():
                break
            if index < 3:
                id = post["id"]
                title = post["title"].strip()
                link = "https://www.coinlive.com/news/{}".format(post["tid"])
                image = post["cover_img"]
                pub_date = util.convert_utc_to_local(post["published_at"])
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description:
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "coinlive_articles",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(
            f"request error: {response.status_code}"
        )

if __name__ == "__main__":
    util.execute_with_timeout(run)
