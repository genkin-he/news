# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
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
    "sa-mpw-data": '{"url":"/article/4757740-beyond-bank-runs-bank-liquidity-risks-shape-financial-stability","query":"","page_key":"9733f8d7-e426-46d7-942a-fe6423576ee6","referrer":""}',
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=4280005110950; _sasource=; _gcl_au=1.1.599881413.1739425315; _ga=GA1.1.682383326.1739425315; pxcts=3c9bc777-e9cd-11ef-aad6-41c06ffbc06b; _pxvid=3c9bb834-e9cd-11ef-aad3-ffb72c88b6c6; hubspotutk=2b77748c6e4ac29a66ffaab47e818e3c; __hssrc=1; sailthru_hid=39b04d7c8e25d63b5e45e1150895dd0066b463a8da7c1f8f4b0510de06f5a2bed999b02abf867b7ee4da86f9; session_id=7adfe7ff-7ebe-4225-83c2-a21943e664fd; __hstc=234155329.2b77748c6e4ac29a66ffaab47e818e3c.1739425357232.1739425357232.1739428732897.2; __stripe_mid=018b8403-a705-4bd3-b4aa-cab69c1b2ab0a0c682; __stripe_sid=d1aaf014-7f63-4d19-bab5-7b6009236dc7685306; user_id=61876035; user_nick=Billysince1995; user_devices=1%2C2; u_voc=; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=ba2879fba71323fd40ee90893669065dfc3ee758; user_cookie_key=f3b37s; gk_user_access=1*premium.archived*1739430072; gk_user_access_sign=dc333ff5a8ecb2cba693d8df4c059a6f81cdb813; _ig=61876035; _px3=db93b1e73321e6f4c15f75ec50acf675868a1892870c9ae32ec7bcde2accf0c5:p2+SSylySFMX6HTsJRFExqikCveeud2fiVqEyEp6As7xsvUXFn48wzZD4myLuwlo27K78IVQqFhQSNgrJOPZYQ==:1000:LdBPLkSy98c4FsLaW2e5uNQIWAjySl6XkQeJA6huwSI5oM79oO4D9yabfYuXDimMeQDeERA5rXmEZC3krHTtvTzgsdcyaHL0jg251ahpmitjhEdFybIm6QiY6EGc+lAT81JIKjQikpJsNKcC1wY5RQoCyATfCW8OByju1duZL4GBue6AjIqPQf2ejqhtZHk92NauYLOo9B7TGgneEY+FnJnKzO8mW2zpya/Q5YXhWj0=; __hssc=234155329.8.1739428732897; sailthru_content=864a3a924da7a30de0ebe319a3429a48433eea90254efab8fc12dd503670d1923c5f57e561d9315a8a9a86be8720511ecee9f6e97844b2d50c1a0176d4b403dc912a0177cbf7e981e53da9957bf1d0ece000daf098443cb6e598403579b60d077a48c54f6be030f76d2203a1105287e6db4b63cd722394fd8b7c55797eb62a24; sailthru_visitor=2173ec22-20e3-40ac-8a40-62c2593cfd47; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%224280005110950%22%2C%22machineCookieSessionId%22%3A%224280005110950%261739428710376%22%2C%22sessionStart%22%3A1739428710376%2C%22sessionEnd%22%3A1739432399172%2C%22firstSessionPageKey%22%3A%22e10fbe9a-996c-4a3e-b822-8e6070ffdb1b%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22scroll%22%2C%22timestamp%22%3A1739430599172%7D%7D; _pxde=f82870907165e2c5b1247a1e9435dd3d58daaf569d578d4fb7c3e2ac7019d2ad:eyJ0aW1lc3RhbXAiOjE3Mzk0MzA1OTkzNzgsImZfa2IiOjB9; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Farticle%2F4757740-beyond-bank-runs-bank-liquidity-risks-shape-financial-stability%22%2C%22fromMpArticle%22%3Afalse%7D; _ga_KGRFF2R2C5=GS1.1.1739428711.2.1.1739430616.60.0.0; _uetsid=3bf4b3d0e9cd11ef8f5797e039ea4cd2|5lva73|2|fte|0|1870; _uetvid=3bf4c4d0e9cd11ef9ce49515d1a870d7|1wmrw70|1739430590710|19|0|bat.bing.com/p/insights/c/o; sailthru_pageviews=12",
    "Referer": "https://seekingalpha.com/article/4757740-beyond-bank-runs-bank-liquidity-risks-shape-financial-stability",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"


def get_detail(id):
    link = "https://seekingalpha.com/api/v3/articles/{}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cauthor.userBioTags%2Cco_authors%2CpromotedService%2Csentiments".format(
        id
    )
    request = urllib.request.Request(
        link,
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        content = json.loads(body)["data"]["attributes"]["content"]
        return content


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=5&page[number]=1",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
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
                    print("seekalpha_articles exists link: ", link)
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
        util.log_action_error("seekalpha_articles request error: {}".format(response))


util.execute_with_timeout(run)
