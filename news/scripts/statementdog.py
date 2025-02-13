# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

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
    "cookie": "statementdog_device_id=K1dkRjRXS05UMEh4OFl6ZXJ6WUhOVDRYSzhLWS93bEtwenJUSS9EUVFXbWNBdmI5YmQzQUdkbjRVK2NtcWtFYy0tbVBoaDRKelJVaElPTzF5b244Q0R5QT09--d2a38c6127f3e8134caa3c4a201a7f99b58dd3f9; easy_ab=f13b7707-7926-49a9-b65e-3df6110331cf; _ga=GA1.1.90004727.1737971169; upgrade_browser=1; aws_personalize_impression=[%2212248%22%2C%2212245%22%2C%2212243%22%2C%2212242%22%2C%2212241%22%2C%2212238%22%2C%2212239%22%2C%2212232%22%2C%2212237%22%2C%2212227%22%2C%2212233%22%2C%2212226%22%2C%2212217%22%2C%2212219%22%2C%2212214%22%2C%2212198%22%2C%2212212%22%2C%2212203%22%2C%2212218%22%2C%2212215%22%2C%2212205%22%2C%2212207%22%2C%2212211%22%2C%2212216%22]; _statementdog_session_v2=T7UCJzEnebLPZMqIR70wgvvV%2FWwJtdTXHcNwdQi1pbM8n9RhQAoBJyPBs7fFtiXPBTeLyf6kbcilvy5E6khQxQRv5Y8QDECAQxLfJkuWtmPjRJgKQnRqYeakrhWAxVd1jhw0qQHVURvmq4%2B0QO1dHUMyoYa7ntCjYMWDhKdoko0rWZsDdK3hQyvi0hEOdgd%2FkOhXIjHUmEl3nVlMkyx6c36FZbi3CsmgYxabk1DNYHZPUQG%2FQXYJwrxeA8JtCHcdz0%2Bw7fGxc6l8ateKrhUNgnHRl1qk4Ol0LYsnnKVd4qNf9Ri18EtgDDJTuKGAKa8q4HsqOG%2F9--DvMzFfSK5coXXuHw--Eha%2FueRdY5hZSYlGmw6htg%3D%3D; AMP_0ab77a441f=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJjYmI0OGE3OS1iMTU1LTQxYTMtYTA5OS1kYjg1Y2MwMzcyMGMlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzM3OTcxMTY5MDU0JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJwYWdlQ291bnRlciUyMiUzQTAlN0Q=; _ga_K9Y9Y589MM=GS1.1.1737971169.1.1.1737972385.60.0.0",
}

base_url = "https://www.statementdog.com/"
filename = "./news/data/statementdog/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    print("statementdog link: ", link)
    current_links.append(link)
    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one('.main-news-content')

            ad_elements = soup.select(".main-news-title, .main-news-time, .main-news-tag-section, script, picture, .main-news-editors")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            print("statementdog request: {} error: ".format(link), response.status_code)
            return ""
    except Exception as e:
        print("statementdog request exception:", str(e))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(
            "https://statementdog.com/news/latest", headers=headers, timeout=5
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select(".statementdog-news-list-item-link")
            for index in range(len(items)):
                if index > 1:
                    break
                link = items[index]["href"].strip()
                title = items[index]["data-title"].strip()
                if link in ",".join(_links):
                    print("statementdog exists link: ", link)
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
                            "source": "statementdog",
                            "kind": 1,
                            "language": "zh-HK",
                        },
                    )

            if len(_articles) > 0 and insert:
                if len(_articles) > 10:
                    _articles = _articles[:10]
                util.write_json_to_file(_articles, filename)
        else:
            util.log_action_error(
                "statementdog request error: {}".format(response.status_code)
            )
    except Exception as e:
        util.log_action_error("statementdog request exception: {}".format(str(e)))


util.execute_with_timeout(run, notify=False)
