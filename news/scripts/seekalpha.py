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
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=1600579007054; session_id=1262c729-5d64-4e85-9e08-5f5aed5d97da; _sasource=; sailthru_pageviews=1; _gcl_au=1.1.918264544.1742208108; _ga=GA1.1.1972693355.1742208108; sailthru_content=3c5f57e561d9315a8a9a86be8720511e; sailthru_visitor=119f1a1a-bd59-4aad-b0c2-77654c690154; _uetsid=6df2f180031c11f0a0a4c51b2d364524|12q7yfk|2|fua|0|1902; _uetvid=6df30c30031c11f0bd7d17fc0c2473c2|15wxwc9|1742208109684|1|1|bat.bing.com/p/insights/c/e; pxcts=6eb0051a-031c-11f0-9c9e-23da37be648a; _pxvid=6eaffa3b-031c-11f0-9c9d-1fab639b9a93; __hstc=234155329.d7dc8212116e7979bd200fc0ef39cc7b.1742208110651.1742208110651.1742208110651.1; hubspotutk=d7dc8212116e7979bd200fc0ef39cc7b; __hssrc=1; __hssc=234155329.1.1742208110651; _px3=15910e2ecab6ed1e66b2834537664474f9c40f642a386facb071b6f7a399573b:LKl4fZH0e7pu7M3GuK0QT1a1mhTx2cOpahvmH2HIB1qfOfGTpDeKvdIymfD2034E0wDFFDsw7G9azkgS7VMHfg==:1000:2fUG6gpVz7YLu9P6IYdBzKzqethYwMPR9IHnM4mShvHelB//tEuncBw9quORDzEGoMs4jNaT9x4jTd2URN0zoGBDSscvPZRIsmCkLbG6efLm/sA+aq0Kiigb/ug5s64FV5dmml9BjfS548Vbg8TB7mjhGBjf09ru9Peb20pZjYSlu7Pivd/satfpLbL0g6FMpHa/49j/+y56fnV7rvbgZaXke43X8PNxkQfwboQaY4U=; user_id=62083975; user_nick=; user_devices=1%2C2; user_cookie_key=xsbbt5; u_voc=; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=30011224c9eceebb2804de102c3ef69a129bd905; gk_user_access=1*premium.archived*1742208115; gk_user_access_sign=21e2aaf637337269d6373751736866e08a57fc08; sailthru_hid=a3d286c3d20855c4ce296d328028219b67d4cdeed08c0393710fed268a54e529a458058c6c82459d848b860d; _pxde=0b965c5d72e3968b1bdffb7c8c3e74da09a1f0100b759beff0059675fc6540b5:eyJ0aW1lc3RhbXAiOjE3NDIyMDgxMTcyMjQsImZfa2IiOjB9; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%221600579007054%22%2C%22machineCookieSessionId%22%3A%221600579007054%261742208106055%22%2C%22sessionStart%22%3A1742208106055%2C%22sessionEnd%22%3A1742209932033%2C%22firstSessionPageKey%22%3A%227b5f20ca-c3b2-4047-a7fe-2ad8c0c4b836%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1742208132033%7D%7D; _ga_KGRFF2R2C5=GS1.1.1742208108.1.1.1742208134.34.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2F%22%2C%22fromMpArticle%22%3Afalse%7D",
    "Referer": "https://seekingalpha.com/",
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
