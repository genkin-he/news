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
    "cookie": "machine_cookie=1600579007054; _sasource=; _gcl_au=1.1.918264544.1742208108; _ga=GA1.1.1972693355.1742208108; pxcts=6eb0051a-031c-11f0-9c9e-23da37be648a; _pxvid=6eaffa3b-031c-11f0-9c9d-1fab639b9a93; hubspotutk=d7dc8212116e7979bd200fc0ef39cc7b; __hssrc=1; has_paid_subscription=true; ever_pro=1; sailthru_hid=a3d286c3d20855c4ce296d328028219b67d4cdeed08c0393710fed268a54e529a458058c6c82459d848b860d; session_id=d41a9a4c-533c-4881-b12b-12ec131d233b; sa-user-id=s%253A0-117e9369-5086-55db-5a2d-e5f552bae0b0.wVmBxVZN9D98HkR%252BkM%252Bs3bBQ8TQMYmq4CCE9%252BUJlrIo; sa-user-id-v2=s%253AEX6TaVCGVdtaLeX1UrrgsCWA_wg.Z1cXywGEzhWFyn6x1BJekw3Yw3KzWcHsVs8FmnGqtvM; sa-user-id-v3=s%253AAQAKICrO1qoQl-eTKLbp3qyhF7SrkAb6epSejUJyvDprsRy4EAMYAyC7lN--BjABOgSTr2ZEQgQwRJqO.jPiaKGs9XCO0ykKN2IZdp1NLHWRVEjM0qTLWC3ms%252BkY; __hstc=234155329.d7dc8212116e7979bd200fc0ef39cc7b.1742208110651.1742208110651.1742435396845.2; user_id=62083975; user_nick=Fakwr; user_devices=1%2C2; user_cookie_key=2tk8zq; u_voc=; marketplace_author_slugs=kirk-spano%2Ccash-builder-opportunities; sapu=12; user_remember_token=9bdd4732979d72c50d10e98fe92be438b7e96fcf; gk_user_access=1*premium.archived.mp_1177.chat.mpb_1177.mpf_1177.mp_1386.chat.mpb_1386.mpf_1386*1742435449; gk_user_access_sign=4a3751e5975273971f4217633a3e1ee526daa64a; sailthru_pageviews=2; _uetsid=9e8b1480052d11f0a4c6b30e70839a0c|17g1tcn|2|fud|0|1905; sailthru_content=b10936f2653b835f8464002e46ce6c6584a044f7651eb9c7d9ea0f75ede6955bf0251524d6c5bdfecb6f06af6381eace3c5f57e561d9315a8a9a86be8720511e; sailthru_visitor=119f1a1a-bd59-4aad-b0c2-77654c690154; __hssc=234155329.2.1742435396845; _px3=6f34680e4ddb8086b77e8efaa2b36908966130adf44b79ea25868b65c9bf0812:6+A0goA1hX3nSBLQiSdXNxNhQDisQDu1fL5uPnEcFA2dFm3d6Gdg5grhoBg+oN84Zj4MC3LLGypCdVgs3psoPQ==:1000:CV85ZN9VBMi+FcnQ/s9Fu4xAQr9R8AQEF6rOjg7cIu1gIPASLYhVD9QblFevgJMo1VoJdYpodY6WwfeGVyfTT+O5Qk+obm1V35eeJVOctU50o4P2sdcTBsbQ9DdqKxj23JuCZNi01flRQLWuiaYMPqrJueY0AcTgs7fSPDZNIrOuXT+EQr3P9ugOaA+wCAMLVDLa+01fycYZHPUze4iGYGYsWiWewDQeyfPaRp20/7k=; _pxde=657aad1b6164548972a3178f36961003f68b2048dfa80a86f4d67f906ec2fa44:eyJ0aW1lc3RhbXAiOjE3NDI0MzYwMDY2NjcsImZfa2IiOjB9; _uetvid=6df30c30031c11f0bd7d17fc0c2473c2|1u06t6|1742436238921|3|1|bat.bing.com/p/insights/c/l; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%221600579007054%22%2C%22machineCookieSessionId%22%3A%221600579007054%261742435391343%22%2C%22sessionStart%22%3A1742435391343%2C%22sessionEnd%22%3A1742438056196%2C%22firstSessionPageKey%22%3A%224d77b029-9600-49be-ba7d-dfc5c632c354%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1742436256196%7D%7D; _ga_KGRFF2R2C5=GS1.1.1742435393.2.1.1742436258.60.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2F%22%2C%22fromMpArticle%22%3Afalse%7D",
    "Referer": "https://seekingalpha.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/list.json"

util = SpiderUtil(notify=False)

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
