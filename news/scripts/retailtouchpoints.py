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
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": '_gcl_au=1.1.1832294804.1757670786; _fbp=fb.1.1757670989401.461926461500059465; hubspotutk=080bbf00adb9832c917f1787f7fa1424; __hssrc=1; _mkto_trk=id:212-UPB-292&token:_mch-retailtouchpoints.com-2456dae199e6c00a92202e08fd61649a; __gads=ID=61fe8a8b7416f459:T=1757670989:RT=1757671460:S=ALNI_MYXicfv4Cph8xHIsuGYgeBbQrQB6g; __gpi=UID=00001195a1d6f3b8:T=1757670989:RT=1757671460:S=ALNI_MZuWJTSicemf36PF_FqqdAGhziH7w; __eoi=ID=5cba4302500bc0ab:T=1757670989:RT=1757671460:S=AA-AfjYS2g6bWbbnKVBGxWqzU6t3; __cf_bm=VFaJ_OTca1X1FpgD92Pu.CLZ05EjgOtQYBTlRodOfoI-1757933705-1.0.1.1-GZPyLcqwt.Mci4GpIb6ae6CZH_Lf4F8wTmbBxibgqx2K_3bswz9vzIcKXuoVDewOIOsH6v.0HFil1DKY3Y0K02ZWJDUhvAKHakzSw73GnXE; _parsely_session={%22sid%22:5%2C%22surl%22:%22https://www.retailtouchpoints.com/articles%22%2C%22sref%22:%22%22%2C%22sts%22:1757933722581%2C%22slts%22:1757925480795}; _parsely_visitor={%22id%22:%22pid=2128e36e-4b74-4684-9ab7-a5f5efedc8ca%22%2C%22session_count%22:5%2C%22last_session_ts%22:1757933722581}; _ga=GA1.1.1215815410.1757670797; __hstc=26322466.080bbf00adb9832c917f1787f7fa1424.1757670994289.1757670994289.1757933734422.2; __hssc=26322466.3.1757933734422; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Sep+15+2025+19%3A00%3A05+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a5061c28-3d77-439e-8de3-10f85357534e&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CBG8%3A1%2CC0002%3A1%2CC0004%3A1&AwaitingReconsent=false; _ga_8GFXJ03ZPP=GS2.1.s1757933722$o3$g1$t1757934005$j60$l0$h0',
}

base_url = "https://www.retailtouchpoints.com"
filename = "./news/data/retailtouchpoints/list.json"
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
        soup = body.select_one("div.elementor-widget-theme-post-content")
        ad_elements = soup.select("div")
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
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select("article h3 a")
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
                        "source": "retailtouchpoints",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.retailtouchpoints.com/articles")
