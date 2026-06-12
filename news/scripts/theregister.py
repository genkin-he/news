# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from urllib.parse import urljoin
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
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
    "cookie": 'bucket=188; _ga=GA1.1.1366897814.1762757593; cmp=g0.c0.l0; __gads=ID=9d6446c480f58a47:T=1762757593:RT=1762765130:S=ALNI_MYn6_RA9RsQ27Mcy65sY2uKPDr9jw; __gpi=UID=000011b273163e39:T=1762757593:RT=1762765130:S=ALNI_MYl1EjvMpkR758lPn9et_6sma_p8w; __eoi=ID=9549f8f79d80d058:T=1762757593:RT=1762765130:S=AA-AfjZ5F48cuSxNv5VUTEPs-tlV; vs=242926; sc=6; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%220788693f-7610-41f1-8d52-f765861ffa79%5C%22%2C%5B1762757593%2C68000000%5D%5D%22%5D%5D%5D; _ga_JXW44Y23NM=GS2.1.s1762764021$o2$g1$t1762765302$j8$l0$h0; FCNEC=%5B%5B%22AKsRol8ibhu0AqrIApU8O_EcXkiT8WUacREApo988xBBcAOlu3gx4hZ84TvTHXbdsvVrhLOmYFYCCavJwvof0ZKcfhvlbuhenSBHFAV85Rpf0PrUFTpkYJkeOVdGWO07NjSj-ca34FRHpP7Xas5TymgYBk8gvl09YA%3D%3D%22%5D%5D'
}
base_url = "https://www.theregister.com"
filename = "./news/data/theregister/list.json"
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
            soup = body.select_one('#body')
            if not soup:
                util.error("article content not found: {}".format(link))
                return ""
            ad_elements = soup.select("script, style, iframe, noscript, div")
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
            "https://www.theregister.com/", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select("a.story_link")
            data_index = 0
            for index, item in enumerate(items):
                if data_index > 4:
                    break
                href = item.get("href", "").strip()
                if not href:
                    continue
                link = urljoin(base_url, href)
                title = item.select_one('h4').get_text().strip()
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
                            "source": "theregister",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format("https://www.theregister.com/", response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)

