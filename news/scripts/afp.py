# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "origin": "https://www.msn.com",
    "priority": "u=1, i",
    "referer": "https://www.msn.com/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

list_url = "https://assets.msn.com/service/news/feed/pages/fullchannelpage?ProviderId=vid-3kv7h73mtcdhywg28d4f9ihgi4xcniq2ubb83iikdu3qwmbd73pa&activityId=690c608f-d29a-43bf-b4e1-222920da80b2&apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&cm=zh-hk&it=web&memory=8&scn=ANON&timeOut=2000&user=m-3FCB06CABFAB62603EFD10E6BEAA63E2"
detail_base_url = "https://assets.msn.com/content/view/v2/Detail/zh-hk/"
filename = "./news/data/afp/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(article_id):
    if article_id in current_links:
        return ""
    util.info("article_id: {}".format(article_id))
    current_links.append(article_id)
    try:
        detail_url = detail_base_url + article_id
        response = requests.get(detail_url, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            data = response.json()
            body = data.get("body", "")
            if body:
                soup = BeautifulSoup(body, "lxml")
                img_elements = soup.select("img")
                for element in img_elements:
                    element.decompose()
                if soup.body:
                    result = soup.body.decode_contents()
                elif soup.html and soup.html.body:
                    result = soup.html.body.decode_contents()
                else:
                    result = str(soup).strip()
                    result = result.replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "").strip()
                return result.strip()
        else:
            util.error("request: {} error: {}".format(detail_url, response.status_code))
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
        response = requests.get(list_url, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            json_data = response.json()
            sections = json_data.get("sections", [])
            for section in sections:
                cards = section.get("cards", [])
                for card in cards:
                    if card.get("type") == "ProviderFeed":
                        sub_cards = card.get("subCards", [])
                        for sub_card in sub_cards:
                            card_id = sub_card.get("id", "")
                            card_type = sub_card.get("type", "")
                            title = sub_card.get("title", "")
                            url = sub_card.get("url", "")
                            if card_id and title and url:
                                all_items.append({
                                    "id": card_id,
                                    "type": card_type,
                                    "title": title.strip(),
                                    "url": url.strip(),
                                })
            data_index = 0
            for index, item in enumerate(all_items):
                if data_index > 4:
                    break
                article_id = item["id"].strip()
                title = item["title"].strip()
                link = item["url"].strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(article_id)
                if description != "":
                    insert = True
                    _articles.insert(
                        index,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "afp",
                            "kind": 1,
                            "language": "zh-HK",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format(list_url, response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    # if util.should_run_by_minute(divisor=10):
        util.execute_with_timeout(run)

