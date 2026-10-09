# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "oly_fire_id=6678I9124356A5P; oly_anon_id=38247952-f20f-4238-954f-1a204680d00c; cto_bundle=48bPkF91U0lmbnU2QjNnN1BFciUyRjhwcHpBQ0duMG9HNVIydW5HczBYZlZ5UjZPbkRaUEVUZWN6RXlUY3AlMkZBWVVjNXNhd0djNW1FSVVDVnluQ2JQNDRLZUhLdGhFQ0NyUkJXM2ljWTlsT1glMkZpMmUxcHpabGdRSllJJTJGdkd0cEEwaW9ZJTJCTEV1JTJCUGVDMWp5R0RhRk5iY3Z1N1VqajY4eXFhcVhEdWU5aVdQcnQ2Sk5XVE0lM0Q; cebs=1; _ce.clock_data=55%2C110.191.214.247%2C1%2C0845b309c7b9b957afd9ecf775a4c21f%2CChrome%2CCN; _swb=b9858e33-a5c1-4103-999e-04c1490dbed7; _ketch_consent_v1_=eyJhbmFseXRpY3MiOnsic3RhdHVzIjoiZ3JhbnRlZCIsImNhbm9uaWNhbFB1cnBvc2VzIjpbImFuYWx5dGljcyJdfSwiYmVoYXZpb3JhbF9hZHZlcnRpc2luZyI6eyJzdGF0dXMiOiJncmFudGVkIiwiY2Fub25pY2FsUHVycG9zZXMiOlsiYmVoYXZpb3JhbF9hZHZlcnRpc2luZyJdfSwiZXNzZW50aWFsX3NlcnZpY2VzIjp7InN0YXR1cyI6ImdyYW50ZWQiLCJjYW5vbmljYWxQdXJwb3NlcyI6WyJlc3NlbnRpYWxfc2VydmljZXMiXX19; _t=pp%3A; optimizelyEndUserId=oeu1733388936081r0.3535902487207747; optimizelySegments=%7B%222324341034%22%3A%22referral%22%2C%222355610638%22%3A%22gc%22%2C%222361140622%22%3A%22false%22%2C%225704160262%22%3A%22none%22%7D; optimizelyBuckets=%7B%7D; _gid=GA1.2.1364434600.1733388938; _ga=GA1.1.1367452999.1733388546; _ga_1XKY0K1N6C=GS1.1.1733388937.1.0.1733388939.58.0.0; _parsely_session={%22sid%22:2%2C%22surl%22:%22https://www.fiercepharma.com/marketing%22%2C%22sref%22:%22%22%2C%22sts%22:1733396830902%2C%22slts%22:1733388546268}; _parsely_visitor={%22id%22:%22pid=c31553f5-2d92-469c-9acb-6e17da7d8e76%22%2C%22session_count%22:2%2C%22last_session_ts%22:1733396830902}; _ga_X6PEPHSF9L=GS1.1.1733396831.2.0.1733396831.60.0.0; cebsp_=39; _swb_consent_=eyJjb2xsZWN0ZWRBdCI6MTczMzM5NjgzMiwiZW52aXJvbm1lbnRDb2RlIjoicHJvZHVjdGlvbiIsImlkZW50aXRpZXMiOnsiX2dvb2dsZUFuYWx5dGljc0NsaWVudElEIjoiR0ExLjEuMTM2NzQ1Mjk5OS4xNzMzMzg4NTQ2Iiwic3diX2ZpZXJjZV9waGFybWEiOiJiOTg1OGUzMy1hNWMxLTQxMDMtOTk5ZS0wNGMxNDkwZGJlZDcifSwianVyaXNkaWN0aW9uQ29kZSI6ImRlZmF1bHQiLCJwcm9wZXJ0eUNvZGUiOiJmaWVyY2VfcGhhcm1hIiwicHVycG9zZXMiOnsiYW5hbHl0aWNzIjp7ImFsbG93ZWQiOiJ0cnVlIiwibGVnYWxCYXNpc0NvZGUiOiJkaXNjbG9zdXJlIn0sImJlaGF2aW9yYWxfYWR2ZXJ0aXNpbmciOnsiYWxsb3dlZCI6InRydWUiLCJsZWdhbEJhc2lzQ29kZSI6ImRpc2Nsb3N1cmUifSwiZXNzZW50aWFsX3NlcnZpY2VzIjp7ImFsbG93ZWQiOiJ0cnVlIiwibGVnYWxCYXNpc0NvZGUiOiJkaXNjbG9zdXJlIn19fQ%3D%3D; _zitok=57cf59a1e0551e766afa1733396832; _oly_seg=[]; _ce.s=v~11343663872b5e2a66b4ffb45f8034e0921d9fbc~lcw~1733396836439~vir~new~lva~1733388547572~vpv~0~v11.cs~380816~v11.s~137dd830-b2f9-11ef-a3e9-eb8fc9608af5~v11.sla~1733396836439~v11.send~1733396837186~lcw~1733396837186",
}

base_url = "https://www.fiercepharma.com"
filename = "./news/data/fiercepharma/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.find(id="article-body-row")
        if soup is None:
            util.error("article-body-row not found: {}".format(link))
            return ""

        ad_elements = soup.select(".ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        top_items = soup.select(".content-wrapper .title a")
        list_items = soup.select("article .element-title a")
        items = top_items + list_items
        record_count = 0
        for index in range(len(items)):
            if index > 6:
                break
            if record_count >2:
                break
            title_element = items[index]

            link = "{}{}".format(base_url, title_element["href"].strip())
            title = title_element.text.strip()
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
                        "source": "fiercepharma",
                        "kind": 1,
                        "language": "en",
                    },
                )
                record_count = record_count + 1
        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.fiercepharma.com/marketing")
