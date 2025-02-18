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
    "sa-mpw-data": '{"url":"/article/4757748-in-defense-of-adaptive-asset-allocation","query":"","page_key":"2f35ca49-2ec7-491b-9235-3b389346e2e1","referrer":""}',
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "machine_cookie=4280005110950; _sasource=; _gcl_au=1.1.599881413.1739425315; _ga=GA1.1.682383326.1739425315; pxcts=3c9bc777-e9cd-11ef-aad6-41c06ffbc06b; _pxvid=3c9bb834-e9cd-11ef-aad3-ffb72c88b6c6; hubspotutk=2b77748c6e4ac29a66ffaab47e818e3c; __hssrc=1; sailthru_hid=39b04d7c8e25d63b5e45e1150895dd0066b463a8da7c1f8f4b0510de06f5a2bed999b02abf867b7ee4da86f9; __stripe_mid=018b8403-a705-4bd3-b4aa-cab69c1b2ab0a0c682; _sapi_session_id=kR9eMRLgw3wJgl8G1qStmNJKFC7uBurCJwaix3m7mr2pn%2B0pf8ek0a7ZBDPIDeiWJRSqlacL7ZECbgxZGUmBMCl%2BCUQRP79Vhh5eOCW5R8EMwF55sEkyZekREPlAggeSBwmgEzhEChIA%2Bo8MPqHyIx0x5fzgLdZc1mUsHm0%2Fhp2jJUr8MvWW%2FVhRUEWn08OF04%2BHzf%2Bb7hUchN1nyyFFiD32IBzaWaHrWQcaGcq02wh5GtfgxOFrBsDbG5QzlGm95Auww8bU9ySe9UTeKG7F6t2VaK3P%2BSLtcR4y3fuYxT8Ty%2Fv2jXbH6WNSa4GJ8Dl%2BbOtViAIK4J%2BlBujV9s56rcghrcOKgzf5kXzyOL0aGLseOd%2FgNYvWWyEcH%2Bs%3D--6TAMp2Qxo6MQeLm1--HjizK%2FLiHyXaVFjXtYwBPA%3D%3D; session_id=a6428e7e-e51f-40ac-b16b-053e552cb8df; __hstc=234155329.2b77748c6e4ac29a66ffaab47e818e3c.1739425357232.1739428732897.1739434105767.3; user_id=61876035; user_nick=Billysince1995; user_devices=1%2C2; user_cookie_key=113u32k; u_voc=; has_paid_subscription=true; ever_pro=1; sapu=12; user_remember_token=57084c07b4f55012bf15c490f2e262924c0a4821; gk_user_access=1*premium.archived*1739434136; gk_user_access_sign=5798315c264868c14ff9ebc0aab2cebf699e8e5d; _ig=61876035; sailthru_pageviews=5; _uetsid=3bf4b3d0e9cd11ef8f5797e039ea4cd2|5lva73|2|fte|0|1870; sailthru_content=864a3a924da7a30de0ebe319a3429a48433eea90254efab8fc12dd503670d192e000daf098443cb6e598403579b60d077a48c54f6be030f76d2203a1105287e6db4b63cd722394fd8b7c55797eb62a243c5f57e561d9315a8a9a86be8720511e231d398bb6e754b13332e22dba31551e912a0177cbf7e981e53da9957bf1d0ecca4e4f313bb70a5ce1e669fdb076c9facee9f6e97844b2d50c1a0176d4b403dc0aa7c86d573f665954f16c8c32f3fd6dc3a027d330391622fa2443218fcb2121e9d09602a27c89ca74b1e54c1fa1bee5; sailthru_visitor=2173ec22-20e3-40ac-8a40-62c2593cfd47; _uetvid=3bf4c4d0e9cd11ef9ce49515d1a870d7|1dlh7cm|1739434334968|5|0|bat.bing.com/p/insights/c/n; __hssc=234155329.5.1739434105767; _px3=fc11328702c5fdc152ada9316d3dfd114a4fd30439cb2849e85dd60c6cfb9438:yoGfpIqCzZIwD5B5ITtz5Mx2EPZuyyzhPYG0PCWsdGCJojKcEJIxsnsdHGW5CX/TiUe7pCBlwmcAPEZlCkw/Tg==:1000:p+PkHNKHCwoSaZsLqOdRM89E2UDVycvToOwskS74Km0eOo2MvQgpaBxR844yy3oSCEtKwMysFpEZVDViZeBh0ZBobxEjqMBxF+gmIinUcHlA10rGXNkV7RSz3jF8TGyQeSQ1q9RmCc8TxmPyQ1b/SglADFudXeYzG8ol2wpZ8xLuzHvSN4TkUT5VZKXoEp3/GAnf5CIlO5dr1foNB6/1gpf1mAdG6oM1+9CyvFE7hks=; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%224280005110950%22%2C%22machineCookieSessionId%22%3A%224280005110950%261739434102393%22%2C%22sessionStart%22%3A1739434102393%2C%22sessionEnd%22%3A1739436146779%2C%22firstSessionPageKey%22%3A%22de39f06b-819f-4fbc-9e23-fbde6593af82%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1739434346779%7D%7D; _pxde=77608e961fb6098f5e88d3138096f1871e56159015171399922df8eafc166d94:eyJ0aW1lc3RhbXAiOjE3Mzk0MzQzNDkxMTgsImZfa2IiOjB9; _ga_KGRFF2R2C5=GS1.1.1739428711.2.1.1739434349.44.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Farticle%2F4757748-in-defense-of-adaptive-asset-allocation%22%2C%22fromMpArticle%22%3Afalse%7D",
    "Referer": "https://seekingalpha.com/article/4757748-in-defense-of-adaptive-asset-allocation",
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
