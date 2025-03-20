# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
from util.spider_util import SpiderUtil

util = SpiderUtil()

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
    "cookie": "machine_cookie=1600579007054; session_id=1262c729-5d64-4e85-9e08-5f5aed5d97da; _sasource=; _gcl_au=1.1.918264544.1742208108; _ga=GA1.1.1972693355.1742208108; pxcts=6eb0051a-031c-11f0-9c9e-23da37be648a; _pxvid=6eaffa3b-031c-11f0-9c9d-1fab639b9a93; __hstc=234155329.d7dc8212116e7979bd200fc0ef39cc7b.1742208110651.1742208110651.1742208110651.1; hubspotutk=d7dc8212116e7979bd200fc0ef39cc7b; __hssrc=1; user_id=62083975; user_nick=; user_devices=1%2C2; user_cookie_key=xsbbt5; u_voc=; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=30011224c9eceebb2804de102c3ef69a129bd905; gk_user_access=1*premium.archived*1742208115; gk_user_access_sign=21e2aaf637337269d6373751736866e08a57fc08; sailthru_hid=a3d286c3d20855c4ce296d328028219b67d4cdeed08c0393710fed268a54e529a458058c6c82459d848b860d; sailthru_pageviews=3; _uetsid=6df2f180031c11f0a0a4c51b2d364524|12q7yfk|2|fua|0|1902; sailthru_visitor=119f1a1a-bd59-4aad-b0c2-77654c690154; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%221600579007054%22%2C%22machineCookieSessionId%22%3A%221600579007054%261742208106055%22%2C%22sessionStart%22%3A1742208106055%2C%22sessionEnd%22%3A1742209978895%2C%22firstSessionPageKey%22%3A%227b5f20ca-c3b2-4047-a7fe-2ad8c0c4b836%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1742208178895%7D%7D; __hssc=234155329.3.1742208110651; sailthru_content=3c5f57e561d9315a8a9a86be8720511eb10936f2653b835f8464002e46ce6c6584a044f7651eb9c7d9ea0f75ede6955b; _uetvid=6df30c30031c11f0bd7d17fc0c2473c2|15wxwc9|1742208181720|5|1|bat.bing.com/p/insights/c/e; _ga_KGRFF2R2C5=GS1.1.1742208108.1.1.1742208182.52.0.0; _px3=1b41a01039e134e802c3f001e2769f2777c71258e5a372bdb71b65cd816de9c5:6vBlGGpcUmnYwRSbueraBo0TyKvz8KTYRyT0j9SsbLD7DDTj1KuwB4wfO2jaSpi7k8QiM3fHaOVvR5r0PPxkog==:1000:2Ua7zYpD/zSZPUVqCQXuldaC5bx6RzRrLhnH0Jcc5Sh0AV3fhYrndfnOKycnRb1xp0y7HQkhlW5eSOvqmjOKWMDMmMdizkIBae9LmjvyhmMxSRvtkG3fvWAhASsV6zJNiyhphj2A5Uk4laVdKdKfd433wg7pjPSI7VShrtO/omVv3Hhr2wj/Xc1lEOxPmTZWSh8WIdHcbYsRiwW36f+Xyn4gV893koI181+fYLDLjWo=; _pxde=f731a071ce659189f73f25cfe16668534c32115d05b5196842ace74f95531876:eyJ0aW1lc3RhbXAiOjE3NDIyMDgxODIzNTIsImZfa2IiOjB9; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Flatest-articles%22%7D",
    "Referer": "https://seekingalpha.com/latest-articles",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"


def get_detail(id):
    link = "https://seekingalpha.com/api/v3/articles/{}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cauthor.userBioTags%2Cco_authors%2CpromotedService%2Csentiments".format(
        id
    )
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        content = response.json()["data"]["attributes"]["content"]
        return content
    return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=20&page[number]=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        posts = response.json()["data"]
        for index in range(len(posts)):
            if index < 1:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
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
                description = get_detail(id)
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
                            "source": "seekalpha_articles",
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
