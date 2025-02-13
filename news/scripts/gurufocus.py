# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
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
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"131.0.6778.205"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "strategy=password_grant_custom; password_grant_custom.token=false; password_grant_custom.expires=false; password_grant_custom.refresh_token=false; password_grant_custom.client=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImRkNjFlOGEzZjUxMTkwMGU3Y2UxMDIyNmUxY2ViZjE3MjQ4ZDRkMWIzOTU0MWRlMGI4YTFlNTQ4YjcxNjdiM2FiY2MxNTBjMzY3ZmIyMzc2In0.eyJhdWQiOiIyIiwianRpIjoiZGQ2MWU4YTNmNTExOTAwZTdjZTEwMjI2ZTFjZWJmMTcyNDhkNGQxYjM5NTQxZGUwYjhhMWU1NDhiNzE2N2IzYWJjYzE1MGMzNjdmYjIzNzYiLCJpYXQiOjE3MzQ3MTU5NjksIm5iZiI6MTczNDcxNTk2OSwiZXhwIjoxNzQ1MDgzOTY5LCJzdWIiOiIiLCJzY29wZXMiOltdfQ.zu53QaAg0TNZnYM5O-THQCJ5KE2pWWGzoCdqWsDZuv0MyXdZmUUYTapD47ne-sbmfgXD-aCJvKwTiFYXEXprrU10FvWXwz48iIO1OC-ay7JdE-vVRo_gs6_mjuf0bmOIxR_OjxBk4AMhdcrem1BYfbyzPmOeVLPZU_62Vqbf_B-ywX__PzRSNEZGvJ8LVgJf1yM6hL-05Kq0dk33l34pQ1zEqE6Pw_B1tcquf6nR8NwYWJ_9xlovIVA-ZpftgPk8JwkEOFTKAQr_8R8O-N0ZxF2QFpzuCvZ2mIpLZOvohUkZYBlueHuYFAP8AXnCSLTfMps-nabVxeTH3zh6yEMdg8-d9hawZctvjIUjUX3PmsMbtacgaNF8yWkWlv23mfVzBIozdhef_Y81mvbM0c9067AskN7zm1GesH2ZKxEXK-24JZg-csocUZOsNOGyTkZkL16sg2iCkytox-CkyO3CD9tC9jheKb7WbIsgNJni5Se3aWrWDqXde_H88MD46vTWUocybSmIYlIBtSfaVwqFrRVrnihEVwvXvkCOjwraLDgLLQoI5hgaigl8BCfIkJVlvbEmwC8f6W9ZP9g8FbMBj1zpa3IqCikRMlsdAtVk1zRRtIay2L6UyJkBVPSWyr1KNwVFrGYHsBphv-dU7I8QYOMsAw0H1Nu8fYVMBaZlwJY; password_grant_custom.client.expires=1745083969; phorum_session_v5=false; _gid=GA1.2.963244308.1734925673; _gcl_au=1.1.1688029102.1734925674; wooTracker=2K2GbSrXpddV; upgrade_counter=1; homepage_upgrade_counter_ads=1735012084; _gat=1; cf_clearance=uA7YfzbdR5rBLKEUOp3wmk8XgtEPrEGNYgFE7tVB6gw-1734950111-1.2.1.1-loPd6IF7S7rGZxhl8u.hTyBbsg1iwpWIayGb9Z1m3EPvS4BCr2Ayj7Vzn55GQPfGbVRVVWJTYJHCJW.NHTQCZrRuvKd5LUZraPDkDX2WaCFVxN6.mLlQn5pSyiV0yFX13cQ9kU8YvB3PU.KFSnBRZhf8qv4zxNtVrfeDZYQDfqzEI7HJbK5EJiedM9lxOEHPLU8pHglFhHwy_4t.vUKS92MqD2qvESjn_WWPPXixd1A.kOH1EcIhmZDRHStEUGFnNEMd9VCqLooFRmEvmP4GL4Y6E4H._7MEgVdZbSWxWF1wTDt2R_wLyGVLHQLCFeUBQeRSHvxBJUhi0qZp5tZF30kfrsaFW9CmgHWSWRs02EolTmc.b6NI5M6qvPY8mIW36_X5KnnqNrjhpYYgzhEpyA; _ga=GA1.1.411053262.1734925673; _ga_T14K4LKYZE=GS1.1.1734949354.3.1.1734950111.57.0.0",
}

base_url = "https://www.gurufocus.com"
filename = "./news/data/gurufocus/list.json"
util = SpiderUtil()


def get_detail(link):
    print("gurufocus link: ", link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode(response.headers.get_content_charset())
        body = BeautifulSoup(resp, "lxml")
        soup = body.find(class_="main-body")
        if soup is None:
            print(
                f"gurufocus Error: 'main-body' class not found in the response. Link: {link}"
            )
            return ""

        ad_elements = soup.select(".ad-container")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("gurufocus request: {} error: ".format(link), response)
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".article-item .link")
        for index in range(len(items)):
            if index > 1:
                break
            node = items[index]

            link = base_url + node["href"].strip()
            if link in ",".join(_links):
                print("gurufocus exists link: ", link)
                break
            if node.select_one(".title-section"):
                title = node.select_one(".title-section").text.strip()
            else:
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
                        "source": "gurufocus",
                        "kind": 2,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("gurufocus request error: {}".format(response))


util.execute_with_timeout(run, "https://www.gurufocus.com/latest-news/all/all")
