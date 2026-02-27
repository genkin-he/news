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
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_sf=eyJpdiI6Ii9yY2Zjdll4UEdMQnJMbSt3cWVocUE9PSIsInZhbHVlIjoiOUVzNVJ3eXlERnpwcDlncWdPS2d2TVIvOFJSUHdFR0Yrc3MwbnJqYzV2VWRhYUNSTGQ1akF0V3NPV3M1aUdRTUdKWDM5R0ZmTFphRXlGVUJDeVZvV0d0d2lHSEVPMktWNm5za0VYZ2JFcytCMXRCb2R4aWJaZGtTQTZKd3pSRTIiLCJtYWMiOiI5YTk0MDAxODcxZGJjZTBjOGI5OGFkYjI0NTJhZDFhNjM0YTU2NmI4YmYxMmU4ZGQzMmUxY2ZiMWZhM2ZmNjUyIiwidGFnIjoiIn0%3D; filter-exchanges=NASDAQ%2CNYSE; __cflb=0H28vjwrb7sZu7pFWbWQzPirLkxC6LE9sKJ9aLx23gp; _gcl_au=1.1.1812158087.1724925129; pushalert_67684_1_c_expire_time=1756461128736; _ga=GA1.1.813994316.1724925129; cf_clearance=a55MZ8yK8DmbenWFETQZr5s9wDSc7U8Nv5nfUJXFy00-1724925129-1.2.1.1-uRa5OV7E.V8kv87b2omQvvfDukdrpGd3D1ykYAT7qMHgvdIS.3UMjvzRi884u79r7A1RdFTowb1FA8DzygbbguFNX_bNCECRXLsXeVRFCjuRx3ke8YDhpoah2Mic1Tay048BT.wqOnWDLs_MYlB5Y4SQm1jSMr6oG.ubwby5XK.CB90JrO2zp9MEExdNSWdjmr5hUsSVNud5XB.ptkXBmFut7MBNC_SmRKgQ7HHJ0bHmylIUQvL3MMNZanpAVJ2Swt0IMeNZ7.FSUKSsQgU3rlGn_XQjgCjTsIYSIFfK1V0OS7CnLFOej8dnraVXUZc6t7K5WKZKPx9FF9pgs.qyoFlgkYvfoE8uvqvTOf.8oRmZG7g0VhcTmWUKzUlU8dcQfWO2evj8_b.qsnQbw8pIKg; lgnPpCl=1; pushalert_67684_1_subs_status=denied; _ga_PDGY9YVDNG=GS1.1.1724925128.1.1.1724925289.60.0.0; XSRF-TOKEN=eyJpdiI6ImZ2L2gyQXZvUm5mY2tsbHd4dXI4T3c9PSIsInZhbHVlIjoiMEEvSGZIUjJPZ1JxSVF3V2RSbktkYXlBMUlFNm8zTWcva3hTWlJITnpNSjhFL2ovMHhrdGdEREkvZ2FZdFFKWjRGa1M1ZzlvYlF1TTdiODlOa21OL1FqbUNEaFJ5NHNQQ2JmVXlka1F0YjhPeUpzTTlHM0lLK2gzMFl4V2ZtNEsiLCJtYWMiOiIzMjIyZjM4YzBlMmNhNWY0NzViZDUyNDQzNWUyOTA0ZWQ5MmNhNmU1NzVhM2NmNzJhMzIzMDM4NTU4ZjRiZmE0IiwidGFnIjoiIn0%3D; st_s=eyJpdiI6IkNkSkc0RmdFZUdPQXBKLzdFUm0yRHc9PSIsInZhbHVlIjoiRkRaSXEwUnFGS2JoMk9oUjR1bGpzVklaWGNxN2VUb3pjTFljQ2JHRUw0ckk5bFRSclZvcXlWMm5ybEN1MVB2TUp6YTUrL3FmeUovWGJXbDhwZ05paDJ5bHNEbU8xMHBHMUpmVllBMjZoRWhleWM0L0FyVzZLcWhDcXRGTVpOMWMiLCJtYWMiOiI3NmI1OTIxZWJmMDM0MTIxYTEyNzMzYzEwNTMxMTk1YWQ5Yjc3NmUyNTQzMTQzZTRhNDI3OTI2YzVjOTA1ZmNjIiwidGFnIjoiIn0%3D",
}
base_url = "https://stockinvest.us"
filename = "./news/data/stockinvest/list.json"
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
        soup = body.select(".digest-article-content")[0]

        ad_elements = soup.select(".caas-da")
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

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".digest-grid > div > .btn-header")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].select(".font-size-16 > a")[0]["href"].strip()
            title = items[index].select(".font-size-16 > a")[0].text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
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
                        "source": "stockinvest",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(
        run, "https://stockinvest.us/digest/category/latest-stock-market-news?page=1"
    )
    util.execute_with_timeout(
        run, "https://stockinvest.us/digest/category/analysis-and-ideas"
    )
