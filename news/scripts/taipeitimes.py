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
    "accept-language": 'zh-CN,zh;q=0.9',
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
    "cookie": 'tt_guid=5b30000056445; _ga=GA1.1.1772509010.1762152097; ltnSessionLast=1762154238324; ltnSession=1762154238324; _ga_9B3XE39JST=GS2.1.s1762156834$o3$g0$t1762156834$j60$l0$h0',
}
base_url = "https://www.taipeitimes.com"
filename = "./news/data/taipeitimes/list.json"
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
            soup = body.select_one('#left_blake .archives')

            ad_elements = soup.select("link, script, style, div, ul.as")
            for element in ad_elements:
                element.decompose()

            for child in soup.children:
                if hasattr(child, 'name') and child.name == 'h1':
                    child.decompose()
                    break

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
        all_items = []
        response = requests.get(
            "https://www.taipeitimes.com/News/biz", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items1 = soup.select("#left_blake li h1.bf")
            for item in items1:
                if not item.parent or not item.parent.parent:
                    continue
                a_tag = item.parent.parent
                if not a_tag or not a_tag.get("href"):
                    continue
                link = a_tag["href"].strip()
                title = item.get_text().strip()
                if link and title:
                    all_items.append({
                        "link": link,
                        "title": title.strip(),
                    })
            items2 = soup.select("#left_blake li h1.bf2")
            for item in items2:
                if not item.parent or not item.parent.parent:
                    continue
                a_tag = item.parent.parent
                if not a_tag or not a_tag.get("href"):
                    continue
                link = a_tag["href"].strip()
                title = item.get_text().strip()
                if link and title:
                    all_items.append({
                        "link": link,
                        "title": title.strip(),
                    })
            items3 = soup.select("#left_blake li a.tit")
            for item in items3:
                link = item["href"].strip()
                title = item.select_one("h2").text.strip()
                all_items.append({
                    "link": link,
                    "title": title.strip(),
                })
            util.info("all_items length: {}, all_items: {}".format(len(all_items), all_items))
            data_index = 0
            for index, item in enumerate(all_items):
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
                        index,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "taipeitimes",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format("https://www.taipeitimes.com/News/biz", response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)
