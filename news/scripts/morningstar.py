# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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
    "cookie": "mbuddy=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXSyIsImtpZCI6IjE2NjYwMjExMjkifQ.eyJzZXNzaW9uIjoiOGJhMTIyOGMtMWFiNC00ODUxLWEzYmUtNDNhMjQxZWQ2NTRjLjFmOTAwODAwMGQwN2E0ZDhlZjVmMzhiNzQxYjJkOTkwYjRhOWZhNmJjNmI1ODAwZmM1MjViN2JlODUwYzg2OGUiLCJpYXQiOjE3MzYxNTQwMzcsImlzcyI6Imh0dHBzOi8vaW52ZXN0b3IubW9ybmluZ3N0YXIuY29tIiwiZXhwIjoxNzM2MTU0MzM3fQ.gZxgx4_dFHDzVD8PNlyP5IlM_1gewC4ShEAKDq1XRvQGouFwCRny-d2qgNBpaf45pvlhUYfQk0WfhofNG4IsRhp5EVM5Vz0Rp_cGvQ8_XlFPSW9knUC3TLt3YAST_RQ6KLgeZEZyst2bOrdWd_WTL7Il2UUk_oQ-osAM_8I6GCs7oDzkRHaUYVtJ1TjgZLQ-j-OmUKI4TUpDLRykoVH9y-ipNDMuGvJ-RHdqw8viR35LaiNMfRWA8iyo5n-2AsAuCeFR_2MivLses-lzezkr5i3pfPv0_TXxuQPc0-vfC1YJFqDHZAE5EHRDx3Zcwq9BNWuqaXfpKjeZsAmSOFrc9w; msession=8ba1228c-1ab4-4851-a3be-43a241ed654c.1f9008000d07a4d8ef5f38b741b2d990b4a9fa6bc6b5800fc525b7be850c868e; test; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.morningstar.com/news%22%2C%22sref%22:%22%22%2C%22sts%22:1736154040055%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=9b2bca8f-fe4a-420f-91d9-88b09b2d9f9d%22%2C%22session_count%22:1%2C%22last_session_ts%22:1736154040055}; _gcl_au=1.1.1873539593.1736154040; AwinChannelCookie=direct; _ga=GA1.1.54914329.1736154041; _cb=D39bdCiyPDKCRwdQS; mid=6292954010651283371; ELQCOUNTRY=CN; _gd_visitor=4c8de1f7-019b-4b71-8eb4-922fdf9d684a; _gd_session=e06f4979-ffe0-4112-8c63-d962a5ef1b54; ELOQUA=GUID=138B679F1A994E0CB87D27FDD91ADA6F; _an_uid=2365920397145872819; _ga_G8C0R44VCK=GS1.1.1736154040.1.1.1736154086.14.0.0; _chartbeat2=.1736154040950.1736154087055.1.DmRcwlCmveDLCwebOXBI5ShgB65XtP.1; _cb_svref=external; aws-waf-token=c3fb293a-6c06-4767-b60d-7b00ffa4784e:AAoAocc/DuClAAAA:bVLT7M+Ese22/34TMdnRQxom/IFj7W4gm1COXcXS1Hp6MZlcP2Lkzh2mYvgiJIufNANTqzWUVwbhwDt0ECeMFXFL6k+qGp8Db8rb2vK+maZ2u7FeZFRX638QqheIEFwocJ3aiSfpyuJXLPQQq1ZRpI+MPdXCX8Fm8V272MAHcz4kAk3UQjsot/EOHKkcPsmcFBvNZ4LAQMTWnEoRLdwwsQgrsT1q83Nrp6fPNkKI0aApjxEDLFSJVifS69ECqbBhrneCb/Ab9t9pSa7oXGmd",
}

base_url = "https://www.morningstar.com"
filename = "./news/data/morningstar/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select(".mdc-article-body")[0]

        ad_elements = soup.select(".article-ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(url, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".mdc-feed__mdc > a")
        for node in nodes:
            if post_count >= 2:
                break
            link = base_url + str(node["href"].strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break
            title = str(node.select_one("header > h2").text.strip())
            if title == "":
                continue
            post_count = post_count + 1
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "morningstar",
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
    util.execute_with_timeout(run, "https://www.morningstar.com/news")
