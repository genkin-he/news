# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
import time
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": 'functional-cookies=1; optimal-cookies=1; privacy-notification=1; sxa_site=FOREX US CD; ASP.NET_SessionId=psedbc4z2pjn4klmdchfmdzk; wsEntity=CIMA; wsEntityLang=zh-CN; _misiteid=753454d74eea4d0d9a56528127813a34; forex us cd#lang=en; ARRAffinity=baa90e318a0f8647150e3584314873bb925316fa0ee4752a943e78d8af1eff54; mt.v=2.784926316.1761821367476; SC_ANALYTICS_GLOBAL_COOKIE=cf9ddbb2ff054dc4982d926252e0ffae|True; mt.s-lbx=2; _ga=GA1.1.2145977162.1761821377; __privaci_cookie_consent_uuid=6b83c5f1-e9d9-4bd4-ac63-5840e7d7d3f5:14; __privaci_cookie_consent_generated=6b83c5f1-e9d9-4bd4-ac63-5840e7d7d3f5:14; __privaci_cookie_consents={"consents":{"34":1,"35":1,"36":1,"37":1},"location":"null#HK","lang":"zh","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":true,"status":"record-consent-success","implicit_consent":false,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; __privaci_latest_published_version=64; _gcl_au=1.1.1018753732.1761821381; _cs_c=0; __tmbid=sg-1761821381-a5cd85e7f45c43b3ae02438ef2ab8e8e; _fbp=fb.1.1761821382014.876669056129376394; geoAdvise=0; _ga=GA1.1.2145977162.1761821377; extendedCookies=_ga; TimeZoneRegion=GB; TiPMix=5.041549429400261; x-ms-routing-name=self; mt.sc=%7B%22i%22%3A1761877128377%2C%22d%22%3A%5B%5D%7D; __cf_bm=UizegiQ2p.ZbTYln3quEbnTztMMWgW_KF3qTetpUdxA-1761878683-1.0.1.1-Oy6bwGiYhpyIE.LDUnAGto79kRkTR4zwKPu9a_KkwcTbfytnxX2avptNXHxWdti_dJrHpbR15UiqZtDVaCFPp2lkGX6Rw59QVTN67w9oUA4; cf_clearance=FJU8M6Pcdv4sUoNhhrzpiCVQtJkDAWeqOPcfwnKXj10-1761878692-1.2.1.1-FrV3inl5.RQHg3ZSiinTSNVWA5CRyegrlOaYBpAvgWhwwP7cGjdrzfqh62MVERoErusYmwsRfoQwxuIVBk_Xi2oXWWGb0aQY.zFl.iSuTdi.vzhrFVT941a9WIBxnRScekO9lJ0hBAFlP7sHEGIvpwOGzPpKenwmnaKts3oS7msWdV0N.99.CMpgVDQpvHZNCdU_ebZ_NHSUmWAcD4tkRVEhOqq_xoDp6nBUUHJPZ.E; _drupalArticleId=3b152e31-5c75-4c49-b62f-58864bbdbbb1; _drupalTags=16100|16184|19074|19072|16573; _cs_id=69e6f384-95f0-a832-bcae-fc7997321c6d.1761821381.3.1761878981.1761877130.1755790034.1795985381537.1.x; _cs_s=19.5.U.9.1761880781850; _ga_XPZTRCXSST=GS2.1.s1761877128$o2$g1$t1761878985$j56$l0$h0'
}

base_url = "https://www.forex.com"
filename = "./news/data/forex/list.json"
current_links = []
util = SpiderUtil()

# Create a session to maintain cookie state and connection
session = requests.Session()
session.headers.update(headers)

def get_detail(link, referer=None):
    util.info("link: {}".format(link))
    detail_headers = headers.copy()
    if referer:
        detail_headers["referer"] = referer
    try:
        response = session.get(link, headers=detail_headers, timeout=30, allow_redirects=True)
        response.encoding = 'utf-8'
        resp = response.text
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select_one(".field-content")
        if content_wrappers is None:
            return ""
        soup = content_wrappers
        ad_elements = soup.select("div")
        for element in ad_elements:
            element.decompose()

        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    except requests.exceptions.RequestException as e:
        util.error("request exception: {} error: {}".format(link, str(e)))
        return ""
    except Exception as e:
        util.error("unexpected error: {} error: {}".format(link, str(e)))
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
        nodes = soup.select(".news-list__article-title a")
        util.info("nodes: {}".format(len(nodes)))
        for node in nodes:
            if post_count >= 3:
                break
            link = base_url + str(node["href"])
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
                        "author": "forex",
                        "pub_date": util.current_time_string(),
                        "source": "forex",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    # 有人机验证，暂时无法解决
    # 403 Forbidden
    util.info("403 Forbidden")
    # util.execute_with_timeout(run, "https://www.forex.com/en-us/news-and-analysis/")
