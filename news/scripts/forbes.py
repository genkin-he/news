# -*- coding: UTF-8 -*-
import time
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.forbes.com/money/",
    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
}

cookies_str = "client_id=5995fea6468c9f678f57363909b3634cc2c; blaize_session=fd76a0b0-1fab-465c-b25e-18d55df2432d; blaize_tracking_id=8206d515-debd-42fa-8fa3-bb94105799f6; _ga=GA1.1.425295379.1766571634; _gcl_au=1.1.1835932459.1766571634; rbzid=ObYWkr7EpgYnGLFBuFcdbw8AjQ2g9KI6bXuZRyMIfwBuBfoPA6OVH3lNQlj064Yo5fw+7Esgc+aevsDVattiwfFB40ZGeWiX4s8rki5JXTYDioaA1ro1Mp/bXFP/3AbUW6TOmcuOMRf4M6HDLUUfnD5SHwjUJet4I1+GZJoOTzB/2j/IGqrnQv2n/uhEWL9cWfSlSJsxtY6z/G8Cv0tIsZGKyh2w1IvyqQKmgu+zazg=; rbzsessionid=2fd9567d5155397a6ce0fa2834cd6846; _swb=7d6a1291-5c6b-4eb0-b3fc-9bf9c2cf32b0; datadome=cf3mer_JVtYIMceU81ug~uISux6Wf4j_tN0Ny2X1JK1kae99iEG7ijXPLi6UYXC9KJOss6CndgV4WBRGPSFJVxppOnhjp6cisXS5~~e1jk9Wd2iQQnL_0KxlixCgYTxm; AWSALB=XOrtjg0GzGYApmQkj6Xtdu7gjN6ghqFdsnjH2CjkmKo6wol0H8Z8Ny9GLAJeiVlf7ucgmTDTEzm1p5kOwEAWFG8fFIp0gZn3gOBZc8/NlhTn5hdciRqrJWEHoz/H; AWSALBCORS=XOrtjg0GzGYApmQkj6Xtdu7gjN6ghqFdsnjH2CjkmKo6wol0H8Z8Ny9GLAJeiVlf7ucgmTDTEzm1p5kOwEAWFG8fFIp0gZn3gOBZc8/NlhTn5hdciRqrJWEHoz/H"

base_url = "https://www.forbes.com"
filename = "./news/data/forbes/list.json"
current_links = []
util = SpiderUtil(notify=False)

session = requests.Session()
session.headers.update(headers)


def parse_cookies(cookie_string):
    cookies = {}
    for item in cookie_string.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


cookies_dict = parse_cookies(cookies_str)
for key, value in cookies_dict.items():
    session.cookies.set(key, value, domain=".forbes.com")


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    time.sleep(1)
    try:
        response = session.get(link, timeout=10, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one(".current-page .article-body")
            if not soup:
                return ""
            ad_elements = soup.select("figure, div")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.info("request: {} response: {}".format(link, response.text[:200]))
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
        all_items = []
        response = session.get(
            "https://www.forbes.com/money/?sh=68a28149c19a",
            timeout=10,
            proxies=util.get_random_proxy(),
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items1 = soup.select("a.zEzPL6aA")
            for item in items1:
                link = item["href"].strip()
                title = item.get_text().strip()
                if link and title:
                    all_items.append({"link": link, "title": title.strip()})
            items2 = soup.select("h3.HNChVRGc a")
            for item in items2:
                link = item["href"].strip()
                title = item.get_text().strip()
                if link and title:
                    all_items.append({"link": link, "title": title.strip()})
            data_index = 0
            for index, item in enumerate(all_items):
                if index > 4:
                    break
                if data_index > 4:
                    break
                link = item["link"].strip()
                title = item["title"].strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description != "":
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "forbes",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1
        else:
            util.error(
                "request url: {}, error: {}".format(
                    "https://www.forbes.com/money/?sh=68a28149c19a", response.status_code
                )
            )

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.info("403 Forbidden")
    #     util.execute_with_timeout(run)
