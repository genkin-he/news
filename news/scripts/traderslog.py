# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import time

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.traderslog.com/feed",
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

cookies_str = "_ga_Y8DRJ5Q9GN=GS2.1.s1766631260$o2$g0$t1766631260$j60$l0$h0; _ga_L86GZTPWNM=GS2.1.s1766631260$o2$g0$t1766631260$j60$l0$h0; _ga=GA1.2.708154639.1764732060; _gid=GA1.2.864128642.1766631261; _gat_gtag_UA_335312_1=1"

base_url = "https://www.traderslog.com"
filename = "./news/data/traderslog/list.json"
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
    session.cookies.set(key, value, domain=".traderslog.com")

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
            soup = body.select_one(".entry-content")
            if not soup:
                return ""
            ad_elements = soup.select("form, script, style, iframe, noscript")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run(url):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = session.get(
            url,
            timeout=10,
            proxies=util.get_random_proxy(),
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "xml")
            items = soup.select("item")
            for index, item in enumerate(items):
                if index > 3:
                    break
                title_tag = item.select_one("title")
                link_tag = item.select_one("link")
                if not title_tag or not link_tag:
                    continue
                title = title_tag.get_text().strip()
                link = link_tag.get_text().strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if title and link and description:
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "traderslog",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        else:
            util.error("request url: {}, error: {}".format(url, response.status_code))

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.traderslog.com/feed")
    time.sleep(1)
    util.execute_with_timeout(run, "https://www.traderslog.com/category/analysis/feed")
