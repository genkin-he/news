# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"809c58081575ba6851f3e11365bca706"',
    'priority': 'u=0, i',
    'referer': 'https://statementdog.com/news',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'statementdog_device_id=S2lrNHB1YnVnTTh0aGcyZFJTUk1idko2aWxpVHVwVXVla0taelRITHdIbkFjVFd0b0xwT1F4RUpDYTJrK0ZUUC0tc05yanVZYzc3dEk3VDFRMVRNRXYyZz09--70223dcbb8258ed7870f735b8375fee5dbe00a3e; easy_ab=da74befb-e996-48aa-b43f-f4fa29b8c555; _ga=GA1.1.1162741084.1761903112; aws_news_and_reports_impression={%22news%22:[%2214889%22%2C%2214895%22]}; AMP_0ab77a441f=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI1M2M0ZjI0Ny0xMmNiLTRmYTktOGYwOC04YzAzNDAxMWNlMzMlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzYxOTAzMTEyMjI3JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJwYWdlQ291bnRlciUyMiUzQTAlN0Q=; g_state={"i_l":0,"i_ll":1761903155667,"i_b":"kPoPB9X9G83Lv2DUNR/m/hGcAX2IKd4X/48g4F9SKBI"}; _statementdog_session_v2=akihw9gs8S0IKfGTqxAfuoRpQUC%2FU6AhX5JM6%2Fw732eZXl08YobxXoPd9s1hho%2FuBrMit0tgKDohz4wm6n3te35MoGIKW3EjT4IeKMwRLZQDPaAZSULvs3F5wiKkM3GlA4INkRgE9njYog1xrQWVZ7kG%2B7CTdIFpwUMnRoMgiZwBCdD6lgQjtFui3Xt6NUfCf30jjQglB%2FLE8JI3Dc09bS5TUTJy7WGhgf9WtP%2FLDzpikow0O8PYXgURdvpTQwuUdotY%2BXbQD88KrpQtpFEd5MN4CUQAOH3JfP4N4U02rcKbPH59LUR8bDSmXin6tTOZedEQmD2J--mLiShGX2EErFQmW%2B--KPRGfez2zuhjVJKMx3FexQ%3D%3D; _ga_K9Y9Y589MM=GS2.1.s1761903111$o1$g1$t1761903156$j15$l0$h0',
}

base_url = "https://www.statementdog.com/"
filename = "./news/data/statementdog/list.json"
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
            soup = body.select_one('.main-news-content')

            ad_elements = soup.select(".main-news-title, .main-news-time, .main-news-tag-section, script, picture, .main-news-editors")
            # 移除这些元素
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
            "https://statementdog.com/news/latest", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select(".statementdog-news-list-item-link")
            for index in range(len(items)):
                if index > 4:
                    break
                link = items[index]["href"].strip()
                title = items[index]["data-title"].strip()
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
                "request error: {}".format(response.status_code)
            )
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)
