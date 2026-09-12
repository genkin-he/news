# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
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
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": '_ga=GA1.1.526183142.1757671510; _pubcid=b6f8b727-ef2a-4f9f-86e3-3a748a469a5c; _pubcid_cst=zix7LPQsHA%3D%3D; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-08-12T10%3A05%3A11%22%7D; pbjs-unifiedid_cst=zix7LPQsHA%3D%3D; panoramaId_expiry=1758276311782; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId=67aecb7dc70f8f8b79bf48d5d4bb185ca02c256fbffaa87e7f3e11d714e81b9c; cto_bundle=pOiR5V9hbkRnY3RoVHVQZ0xqc0NXRUdVeWs2ZzZZQlIyVlBBQXU2TFNXMWtLT3hFWVlCR2tXZE1COVZuYllMZHVGc21TRXpBOVV1a1laUVpDa2Y3TFFOU3BVcWpYJTJGZGQlMkZxcE9JdjFKWiUyRnFIdVVNWmlwOXRXSnUyenZ4ZnZmN09mc1laTnolMkJXcHFuSThhZDRpdGZ0dTJ4Y21SNmtCWCUyQjBMbkt6bG9pb3dzMXlIc1dkbUQ3NUdJUWoyZDU4a25yTjhDQm9Fb3dsS0Q1cUVIckd5VnZOYXhSbWZmdyUzRCUzRA; cto_bidid=D-wF119tVkxLNEpSMjRLSkpPNlBOWWV0ZlM5c3dkSm9NMW5WS1lBbWdtRk5nT0gxZVpWMzhscyUyRkJ3R3c4RlFRdGZnMkNkcmtmUGd6Z2ZUVUVMNjQ3SW5sRyUyRlBUJTJCelJmWkFZMGdTVUljNENiMTJaVUI0MFNmWjk4eE8wakdUME1GeVR4YUZJeWhBS1paN1ElMkJsdHp4cHdhdlAzUSUzRCUzRA; __cf_bm=YK9PvQX557el62VkLOoYl7T8Pmknlxjv4Cvvyjb8dSo-1757990903-1.0.1.1-Kp_1JsOapTyDYCvFV5irm_5Md5aOmYeMAlZRU1GbjvVYSrGm1cRMthfDLyZzFjQB_tk2Gnfbg6qgESTEnTsZUwpOthMH8Koy4pP70xZw93k; cf_clearance=rb2Ojlr18dh9ZIMKwZmAHPn4y1Vbf0neP5JG9xdqUzM-1757990914-1.2.1.1-LeOUMCTWiS1e7GVlH8.DiHtwOfJttyq2s4WpNB1VuZftuzDAR8XwRJsDbvexEKykQAvPuYQnSzzRDLCUMNHkJUA6kBcvQVrVo9xtj9pto7dDp.k.oSKKsPKouzckbVT6GlX6ouJfAdoC1Ydai703V32oinHS_O1Y3m3dT4mI.wD1jyeMBMDwnY.I1_mQLCaADCR2vDZ.r7rW.sLTfHqng.AGSo0n2EDVjyREWz0e2ZU; pum-44754=true; __cf_bm=Xx0gamGSbq2IkGJgfNnIUuVwF5DQiniQ52B0RL.pPBI-1757990920-1.0.1.1-5u1jGmsRaRi4zWYO8rzwg.JwPXqYQt322H2P_SchNUKMZ3rt3Bv2iOkuOQ72DFo4boVSnzDd5ZdP2PoGxh3IhYUI3eHPi0o_WuLkzGGK1dA; __gads=ID=f2f55c409258422e:T=1757671511:RT=1757991250:S=ALNI_MbTLG-TAzsN9NdxO6-SzWvJOrcHeg; __gpi=UID=000011215f412b95:T=1757671511:RT=1757991250:S=ALNI_Mae5hyoGKF2l5SHoiMJCEj057X7kQ; __eoi=ID=489a4f9329810465:T=1757671511:RT=1757991250:S=AA-AfjZUnBEv3sN1NGUMmRSzM7tu; _ga_XPNT8R93HC=GS2.1.s1757990907$o2$g1$t1757991472$j58$l0$h0',
}

base_url = "https://www.seeitmarket.com"
base_path = "./news/data/seeitmarket/{}.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode(response.headers.get_content_charset())
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one(".td-post-content")
        ad_elements = soup.select("div, figure")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        result = str(soup).strip()
        result = result.split("<p><strong>Twitter")[0]
        result = result.split("<p><em>This report is authored by")[0]
        result = result + "</div>"
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link, filename):
    file_path = base_path.format(filename)
    data = util.history_posts(file_path)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".td-main-content .item-details h3 a")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 1:
                break
            a = items[index]
            link = a["href"].strip()
            title = a.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "seeitmarket",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, file_path)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.seeitmarket.com/category/investing/", "investing")
    util.execute_with_timeout(run, "https://www.seeitmarket.com/category/chartology/", "chartology")
    util.execute_with_timeout(run, "https://www.seeitmarket.com/category/market-commentary/", "market_commentary")
