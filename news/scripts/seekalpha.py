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
    "sa-mpw-data": '{"url":"/news/4407431-nabors-misses-q4-top-line-and-bottom-line-estimates-initiates-q1-and-fy25-outlook","query":"","page_key":"359cdd4b-55f3-421d-9697-377a231dbccf","referrer":""}',
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=4280005110950; _sasource=; _gcl_au=1.1.599881413.1739425315; _ga=GA1.1.682383326.1739425315; pxcts=3c9bc777-e9cd-11ef-aad6-41c06ffbc06b; _pxvid=3c9bb834-e9cd-11ef-aad3-ffb72c88b6c6; hubspotutk=2b77748c6e4ac29a66ffaab47e818e3c; __hssrc=1; sailthru_hid=39b04d7c8e25d63b5e45e1150895dd0066b463a8da7c1f8f4b0510de06f5a2bed999b02abf867b7ee4da86f9; session_id=7adfe7ff-7ebe-4225-83c2-a21943e664fd; __hstc=234155329.2b77748c6e4ac29a66ffaab47e818e3c.1739425357232.1739425357232.1739428732897.2; __stripe_mid=018b8403-a705-4bd3-b4aa-cab69c1b2ab0a0c682; __stripe_sid=d1aaf014-7f63-4d19-bab5-7b6009236dc7685306; sailthru_pageviews=5; _uetsid=3bf4b3d0e9cd11ef8f5797e039ea4cd2|5lva73|2|fte|0|1870; _uetvid=3bf4c4d0e9cd11ef9ce49515d1a870d7|1wmrw70|1739428949347|10|0|bat.bing.com/p/insights/c/o; sailthru_content=864a3a924da7a30de0ebe319a3429a48433eea90254efab8fc12dd503670d1923c5f57e561d9315a8a9a86be8720511ecee9f6e97844b2d50c1a0176d4b403dc912a0177cbf7e981e53da9957bf1d0ec; sailthru_visitor=2173ec22-20e3-40ac-8a40-62c2593cfd47; __hssc=234155329.5.1739428732897; _px3=c83e0a2b297f0289ef540c7e7aebe02ce0b4856486ba47d43564381b46ceb29a:L6pHvPlU/mfeyLl6fgHruZhqMFoe06hnEz/rXstnN9oLsRC82J0QzErJrN4pLwwsHA9/FheW5WcZS47sAFRFlQ==:1000:Mf6EVZR/NPG6U4SpPRgScLiKrBpHRYWSW6XnUa6jCFTGC1nd2+NHPI4JXiZAgCrLxPnC25FviYNL2Fr9IxT4vv1/0oGxbygwRZnwxSvU/NalK9ORnR+avt3xOHzGuwo3pvFJJlAKfHX+fPggKVy4evsJpFWPCL2XmbhVHVOqavTxIfav0SRgzIqTCNQ883z4G9MuXzpAttAfwuCs13VweT1RrdI0+Ik3v+XYFV22hQs=; _pxde=38265d7d4be9573ece7056e424e820e7db841028bb3264b084d2bf4c9ac2f858:eyJ0aW1lc3RhbXAiOjE3Mzk0MjkyMTIyMDQsImZfa2IiOjB9; user_id=61876035; user_nick=Billysince1995; user_devices=1%2C2; user_cookie_key=s7d8v9; u_voc=; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=ba2879fba71323fd40ee90893669065dfc3ee758; gk_user_access=1*premium.archived*1739429226; gk_user_access_sign=58fb45507a89b49bce6b5e3610f727c58103e802; _ig=61876035; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%224280005110950%22%2C%22machineCookieSessionId%22%3A%224280005110950%261739428710376%22%2C%22sessionStart%22%3A1739428710376%2C%22sessionEnd%22%3A1739431055799%2C%22firstSessionPageKey%22%3A%22e10fbe9a-996c-4a3e-b822-8e6070ffdb1b%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1739429255799%7D%7D; _ga_KGRFF2R2C5=GS1.1.1739428711.2.1.1739429262.12.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fnews%2F4407431-nabors-misses-q4-top-line-and-bottom-line-estimates-initiates-q1-and-fy25-outlook%22%2C%22fromMpArticle%22%3Afalse%7D",
    "Referer": "https://seekingalpha.com/news/4407431-nabors-misses-q4-top-line-and-bottom-line-estimates-initiates-q1-and-fy25-outlook",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://seekingalpha.com/"
filename = "./news/data/seekalpha/list.json"

util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=5&page[number]=1"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        posts = response.json()["data"]
        for index in range(len(posts)):
            if index < 2:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = post["links"]["canonical"]
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
        util.log_action_error(
            "request error: {}".format(response.status_code)
        )


util.execute_with_timeout(run)
