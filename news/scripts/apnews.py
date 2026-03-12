# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": '__cf_bm=N6MgP0fipldYpkkrDXRuyiXGJvtXK2G8ofwfnWA7XXg-1759050101-1.0.1.1-sX8CaE2cLDpU.x5T4gYIyXDWVmS3DB_2htPrWaCI6MF1PAr1tVjZo0ae4iYzKnegtBUNfAREcTMCXwk_0DUZZ13Owm0TOELzQizDHC5S51C5KVdD3iVktwAYllYxU1tF; _ga=GA1.1.1182272407.1759050105; _pubcid=127c1114-6e31-45fb-bc20-9fedcc3e46e3; _pubcid_cst=zix7LPQsHA%3D%3D; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://apnews.com/hub/financial-markets%22%2C%22sref%22:%22%22%2C%22sts%22:1759050105431%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=6d81d5b5-40bf-4771-9419-e23fdf4db2a5%22%2C%22session_count%22:1%2C%22last_session_ts%22:1759050105431}; _vfa=apnews%2Ecom.00000000-0000-4000-8000-3caf4df03307.36bf2f4a-f9ce-4519-8cb6-e996dc8ee9e0.1759050103.1759050103.1759050103.1; panoramaId_expiry=1759654905910; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId=402f0af4245c8e0545148e12714a185ca02c0cca88f705323a0d8919a07befaa; blaize_session=43aca17f-b62c-406e-aeed-49507b91770a; blaize_tracking_id=47800fb2-71fc-459c-95e1-62f2e80ab659; BCSessionID=7ed5273e-5ebc-443d-9211-a93644b5d09b; permutive-id=47d27347-c745-4af3-a24e-b8b9cd1618d4; optimizelyEndUserId=oeu1759050112537r0.24380882105953583; OptanonAlertBoxClosed=2025-09-28T09:02:11.997Z; cto_bidid=M9IbMl91JTJGMTBKbXFOS2lvTGVVUEIxbzRXTFpCb0p4REFlMzhHV2xrOFRocG9NUTVjcnduc1lKejJmZnlndmtiektKa0VCWHN3Nmt2cGl1T0hYOHg2YURqVGNjbHFndHFKU3pRMUVoS3huU1U0amRDMmEzbEZDZ3U2YXdGUm8lMkZXWWl6VlBNTXBzS1BhSjFXbmYxUEwlMkZaUGUxQXclM0QlM0Q; _lr_retry_request=true; _lr_env_src_ats=false; _vfz=apnews%2Ecom.00000000-0000-4000-8000-3caf4df03307.1759051359.1.medium=direct|source=|sharer_uuid=|terms=; _vfz=apnews%2Ecom.00000000-0000-4000-8000-3caf4df03307.1759051359.1.medium=direct|source=|sharer_uuid=|terms=; optimizelySession=1759051383223; _awl=2.1759051383.5-9ebe76e08908c7404d071a010df534f9-6763652d75732d7765737431-0; _vfb=apnews%2Ecom.00000000-0000-4000-8000-3caf4df03307.18.10.1759050103.true...; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-08-28T09%3A04%3A37%22%7D; pbjs-unifiedid_cst=YiwPLDosoA%3D%3D; pbjs-unifiedid_last=Sun%2C%2028%20Sep%202025%2009%3A23%3A05%20GMT; sailthru_pageviews=4; cto_bundle=0z_qjF9JQk8zMGh6ckRLTGc2UnFsQ1M5d2t1MFRUZ2xQU2ZJYWFOaVpWS1U3UUIwdFVDV1hMdm1jQ3ZYVVY3d3UxQktyNjRGM3hSVVFQY2RKMm85VEJNNWEzTjZycjJ0Ym1iWnV1SjJTdnhLRGpSOHlhV01RRGlZZGhwYSUyQmZGblhaVTB5S0c0RHJScVJUanBVUzY3bEZtN1p2QSUzRCUzRA; sailthru_content=157c93ad7d6b1b4227a455d07bece3a14e65ce8aa0508a61fae5e4d88934adccda9bc1325db79b01b8f279c8f9e7b765; sailthru_visitor=c6a3842e-f09d-4898-86d1-151092eb234f; AWSALB=h3eqM6Mimm5neGh79nkr7VPxhDudjs0MqMyQG6E7IOmRly86ZxYnH8MaLDoc8J2IbuGB94EIEM5mFv+Ag+6SLRLEv6AgkC2/LFEPPN6hqNyI2V0/m/2hiVtgT2kO; AWSALBCORS=h3eqM6Mimm5neGh79nkr7VPxhDudjs0MqMyQG6E7IOmRly86ZxYnH8MaLDoc8J2IbuGB94EIEM5mFv+Ag+6SLRLEv6AgkC2/LFEPPN6hqNyI2V0/m/2hiVtgT2kO; _ga_CW1LS0SXPK=GS2.1.s1759050104$o1$g1$t1759051639$j60$l0$h1460001729; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Sep+28+2025+17%3A27%3A19+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a5964a15-321d-42d8-99b6-b3345fd56e13&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&intType=3&geolocation=CN%3BSC&AwaitingReconsent=false'
}

base_url = "https://apnews.com"
filename = "./news/data/apnews/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        if "Access Restricted" in resp:
            raise Exception("Connection reset by peer") 
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select(".RichTextStoryBody")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            ad_elements = soup.select("div")
            for element in ad_elements:
                element.decompose()
            # 删除最后两个 p 标签
            p_elements = soup.select("p")
            if len(p_elements) >= 2:
                # 删除最后两个 p 标签
                p_elements[-1].decompose()
                p_elements[-2].decompose()

        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run(url):
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml")
        nodes = soup.select("h3.PagePromo-title a")
        util.info("nodes: {}".format(len(nodes)))
        for node in nodes:
            if post_count >= 3:
                break
            link = str(node["href"])
            title = str(node.text)
            title = title.replace('\n', '')
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = ""
            try:
                description = get_detail(link)
            except Exception as e:
                util.error("request: {} error: {}".format(link, str(e)))
                if "Access Restricted" in str(e):
                    break
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "apnews",
                        "pub_date": util.current_time_string(),
                        "source": "apnews",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 40:
                articles = articles[:40]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://apnews.com/hub/financial-markets")
