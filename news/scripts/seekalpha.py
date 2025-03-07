# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=3791951084252; _sasource=; _gcl_au=1.1.1117180159.1741139439; _ga=GA1.1.1070425413.1741139439; pxcts=4464912a-f964-11ef-b42e-f146cef6739c; _pxvid=44648503-f964-11ef-b42d-183b217b8de4; hubspotutk=120a8019f12b614f72474ebab0944ffe; __hssrc=1; has_paid_subscription=true; ever_pro=1; sailthru_hid=31b96527a84257732f15927846a4385367c4f1e8793a62ba9f07b7c4ef6aa4bba69783843bf181cb0ea0a32b; session_id=e146c5c2-4af0-4f42-8937-065c599cd36a; user_id=62013422; user_nick=FelixZhou123; user_devices=1%2C2; user_cookie_key=2wehj6; u_voc=; marketplace_author_slugs=the-value-investor%2Cavi-gilburt%2Cmichael-wiggins-de-oliveira%2Cjussi-askola-cfa%2Ctariq-dennison%2Cr-paul-drake%2Cjohn-windelborn%2Caustin-rogers; sapu=12; user_remember_token=1bc472be749cdf9159f8214de153c976f07315a5; gk_user_access=1*premium.archived.mp_486.chat.mpb_486.mpf_486.mp_1182.chat.mpb_1182.mpf_1182.mp_1236.chat.mpb_1236.mpf_1236.mp_1268.chat.mpb_1268.mpf_1268.mp_1339.chat.mpb_1339.mpf_1339*1741312659; gk_user_access_sign=5ae43c93aef0e68e11835febeb032fe03de4a349; _px3=7c001a696610a0dba94deacde1e7e59f2a02b6bd13ad03b620c9341036b1d982:jlD02cze+uvWJdLs5U6FT1idI6qSwpL2iZx7mcT/7DhEx13+3S4zc/p1wWcn3lQg6R1VmvnE2B8eiMcyAfos2g==:1000:6YPwMnXehS4A5vlVVZuxbHcnYtlLTQmCi2MjacbTBCjdhjSVib4zPJLaPAMbyQfksxOW+rK4xe1HojqzsRY7ynZwm4EQODoQaBToljtPdOE/yLoOOEaO5LZT3iA6vONFEIjqV4AmdJ1Gok/Dzkl96vEQCOUveFUNXBzmb68CPD3gKvWoBY8vy6RqJ88+eBaoNyiBOw5zohRMJnO9MCd1kZEHtggmZOBstr9+UhVdy/Y=; sailthru_pageviews=2; _uetsid=06cdd3c0fa2f11efae793f6a84127b24|mrursh|2|fu0|0|1891; sailthru_visitor=ea787e7d-4976-480e-aa99-0eeca64ce551; __hstc=234155329.120a8019f12b614f72474ebab0944ffe.1741139451251.1741226547398.1741312854811.3; __hssc=234155329.1.1741312854811; sailthru_content=b6f09daf178879a54eed98528b6242aa9e9e3b505d20c25082b306eaffa45ce53c5f57e561d9315a8a9a86be8720511eb10936f2653b835f8464002e46ce6c65f0251524d6c5bdfecb6f06af6381eace; _uetvid=3d845890f96411ef9838c7b3c4ef61e9|15up6vp|1741312864263|9|1|bat.bing.com/p/insights/c/e; _ga_KGRFF2R2C5=GS1.1.1741312626.3.1.1741312864.16.0.0; _pxde=47a168a91e30730f61bd1ca9ee62ac445047db6cb61e9b5f4216839496ccd1f8:eyJ0aW1lc3RhbXAiOjE3NDEzMTI4NjQ4ODMsImZfa2IiOjB9; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%223791951084252%22%2C%22machineCookieSessionId%22%3A%223791951084252%261741312623354%22%2C%22sessionStart%22%3A1741312623354%2C%22sessionEnd%22%3A1741314682437%2C%22firstSessionPageKey%22%3A%22353977a6-3a90-4261-a6a5-5276a7e5e14d%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1741312882437%7D%7D; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fmarket-news%22%7D",
    "Referer": "https://seekingalpha.com/market-news",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/list.json"

util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=6&page[number]=1"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        posts = response.json()["data"]
        for index in range(len(posts)):
            if index < 2:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["links"]["uriImage"]
                link = base_url + post["links"]["self"]
                publish_on = post["attributes"]["publishOn"]
                pub_date = util.current_time_string()
                if "-05:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-05:00")
                elif "-04:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-04:00")

                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                soup = BeautifulSoup(post["attributes"]["content"], "lxml")
                ad_elements = soup.select("#more-links")
                for element in ad_elements:
                    element.decompose()
                description = str(soup).strip()
                if description != "":
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
                            "source": "seekalpha",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


util.execute_with_timeout(run)
