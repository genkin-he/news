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
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=3791951084252; _sasource=; _gcl_au=1.1.1117180159.1741139439; _ga=GA1.1.1070425413.1741139439; pxcts=4464912a-f964-11ef-b42e-f146cef6739c; _pxvid=44648503-f964-11ef-b42d-183b217b8de4; hubspotutk=120a8019f12b614f72474ebab0944ffe; __hssrc=1; has_paid_subscription=true; ever_pro=1; sailthru_hid=31b96527a84257732f15927846a4385367c4f1e8793a62ba9f07b7c4ef6aa4bba69783843bf181cb0ea0a32b; _px3=e90a0216485817d1d39efd5fabe44dec36e4579e105a15cb2e08ef7b800c28aa:+x668kf2kCHuFIgLvGjnnlSzZZ/P8K6AVq9QKl4XZ6BZLEKngAMhqsky3ezmhB3AK0ajKiDrMzw8yUvsfXymaA==:1000:2mWCNNxcT6uM2jR36qxfa5z15P+371uNaATqlWuw4LDQ9kjXYhkmQ+gT0u/kV7wpT0G8plgzZtA1Yw6SQ5++ncK6744Jai6VdoGQt0fPjfuSvOokp78Dlbn9AboTn029/mX6xiE2X5zRY6/wNYDH2/Rf+cJgi0cB85SisJhCRPxh3lr3DmkuOfN72h8yaozymH22hzxLDyJMWyNfCKCNDutCVGrjq8RFqCTPMcXKy4A=; session_id=9aa19962-ae14-40ae-87c0-87ddf857c9dd; sailthru_pageviews=1; sailthru_visitor=ea787e7d-4976-480e-aa99-0eeca64ce551; _uetsid=48b0c660fd5211efa86f3383adef0d95|e8zx85|2|fu3|0|1895; __hstc=234155329.120a8019f12b614f72474ebab0944ffe.1741139451251.1741312854811.1741571534924.4; __hssc=234155329.1.1741571534924; user_id=62038920; user_nick=Ssdytcvhjuu; user_devices=1%2C2; user_cookie_key=bowoei; u_voc=; marketplace_author_slugs=victor-dergunov; sapu=12; user_remember_token=63ceafef20fa41ba0c7481eac4922b3558a600ed; gk_user_access=1*premium.archived.mp_1129.chat.mpb_1129.mpf_1129*1741571547; gk_user_access_sign=e09183a4abe0109e86372962bd7f5952a32f445e; sailthru_content=9e9e3b505d20c25082b306eaffa45ce5b10936f2653b835f8464002e46ce6c65b6f09daf178879a54eed98528b6242aa84a044f7651eb9c7d9ea0f75ede6955b3c5f57e561d9315a8a9a86be8720511ef0251524d6c5bdfecb6f06af6381eace; _uetvid=3d845890f96411ef9838c7b3c4ef61e9|jje63o|1741571619855|7|1|bat.bing.com/p/insights/c/l; _pxde=f300275eb582849ef463ce770446cf3a744be936bb83b8ad2ec90a52f9a3dfb2:eyJ0aW1lc3RhbXAiOjE3NDE1NzE2MjAxMzUsImZfa2IiOjB9; _ga_KGRFF2R2C5=GS1.1.1741571531.4.1.1741571625.50.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Flatest-articles%22%2C%22fromMpArticle%22%3Afalse%7D; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%223791951084252%22%2C%22machineCookieSessionId%22%3A%223791951084252%261741571527992%22%2C%22sessionStart%22%3A1741571527992%2C%22sessionEnd%22%3A1741573426105%2C%22firstSessionPageKey%22%3A%22093d954d-3de8-4ff7-8563-980f6ad782e4%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1741571626105%7D%7D",
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
