# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "cache-control": 'max-age=0',
    "if-none-match": '16zs8h2mo9pbs0b',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    "accept-language": 'zh-CN,zh;q=0.9',
    "accept": "application/json",
    "cookie": 'hk01_annonymous_id=b4c4c05f-e010-44c0-920d-21af5c65f5ed; hk01_font_size_level=medium; _gcl_au=1.1.2006357044.1757475194; pbjs_unifiedID=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-08-10T03%3A33%3A13%22%7D; hk01_asp_type=anonymous; hk01_segment_id=K0130%2CK1330; ps_uid=ps1zsfwpjumfdfcwkt; cto_bundle=rfIjlV9FZ0pLbmVUaEJHaGhqdGlQJTJGSTJWVHlGOTlwdGFKa3pEQyUyQmlYODEycnhsc0dKYkpqN21zMFhCeVVqem9vOHF5eTgzemVRak1pR2YxZnlEbFdRJTJCSjh1eTlXdlAxQzdjM3ZFaFFMS2JteDR5Q3pSUmIya08lMkJXQUJLbWJ6TWhJaDBqbVVZaHprYmYwRkM2dmtOcjJKbHQ0c0FnUmRUcERxb0d2SnhmU0s1a3o0dWVFQU50SnclMkZuVHBvbU9HTEIyTWd5azFGRWh5MTNQS2x0RHRlUW5xbDE2USUzRCUzRA; pbjs_unifiedID_cst=zix7LPQsHA%3D%3D; _gid=GA1.2.383654718.1757475220; __gads=ID=5e29d4a2c746eac9:T=1757475193:RT=1757476234:S=ALNI_MaZnSO9O4VLl62lYD5B61d7VP6NlA; __gpi=UID=00001193fa88621e:T=1757475193:RT=1757476234:S=ALNI_MbEzGn4v-MpDcqKarAcl64xI_9MsQ; __eoi=ID=909b169fbf5acce8:T=1757475193:RT=1757476234:S=AA-Afjaw5Hp-mNyOO-OzBN1CiX_M; _pk_id.6.7b04=870d7b958ce36418.1757475193.1.1757476238.1757475193.; _ga=GA1.1.809251792.1757475195; _ga_ZMN9XP2DVQ=GS2.1.s1757475194$o1$g1$t1757476243$j60$l0$h0; _ga_F5LMN5VKW1=GS2.1.sfcd1cb90-5d1d-a141-1373-179f71ab1c8a$o1$g1$t1757476244$j60$l0$h0; _ga_P13VP8RY2F=GS2.1.sfcd1cb90-5d1d-a141-1373-179f71ab1c8a$o1$g1$t1757476244$j60$l0$h1506995970; FCNEC=%5B%5B%22AKsRol-MKvtiA5KArR7W8rRcrrmhMUnKmMLM__S93RC7fDy1yr3wC2BuQ_DvwGD-WVVZ6gH1apOmxVtokG57ixjyiTFGuHqiXjdkDqaJJTugSu752MxRsEUbaSbztagW_zaiyuD8GT4BYlUW72z9wq-14eRLGVkyZw%3D%3D%22%5D%5D; _ga_6FR9D2HLWB=GS2.1.s1757475215$o1$g1$t1757476303$j60$l0$h0'
}

base_url = "https://www.hk01.com"
filename = "./news/data/hk01/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    # request = urllib.request.Request(quote(link, safe="/:"), None, headers)
    # response = urllib.request.urlopen(request)
    response = requests.get(link, headers=headers, timeout=5)
    if response.status_code == 200:
        resp = response.text
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one("article#article-content-section")
        content_paragraphs = []
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            content_paragraphs.append(str(p))
        return "\n".join(content_paragraphs)
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    response = requests.get(
        link, headers=headers
    )
    if response.status_code == 200:
        body = response.text
        json_data = json.loads(body)
        items = json_data["items"]
        for index in range(len(items)):
            link = items[index]["data"]["publishUrl"]
            link = link.encode().decode('utf-8')
            title = items[index]["data"]["title"]
            title = title.encode().decode('utf-8')
            util.info("link: {}".format(link))
            util.info("title: {}".format(title))
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
                        "source": "hk01",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 40:
                _articles = _articles[:40]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    # util.execute_with_timeout(run, "https://www.hk01.com/channel/396/%E8%B2%A1%E7%B6%93%E5%BF%AB%E8%A8%8A")
    util.execute_with_timeout(run, "https://web-data.api.hk01.com/v2/feed/category/396?limit=12&bucketId=00000")
