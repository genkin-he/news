# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9,en;q=0.8',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}
base_url = "https://www.startuphub.ai"
filename = "./news/data/startuphub/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = requests.get(link, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one('div.infinity-article-content')

            if not soup:
                util.error("article content not found: {}".format(link))
                return ""

            ad_elements = soup.select("link, script, style, iframe, noscript, div")
            for element in ad_elements:
                element.decompose()

            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(
            "https://www.startuphub.ai/", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select("h2.post-title a")
            data_index = 0
            for index, item in enumerate(items):
                if data_index > 4:
                    break
                link = item["href"].strip()
                title = item.get_text().strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
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
                            "source": "startuphub",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format("https://www.startuphub.ai/", response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)

