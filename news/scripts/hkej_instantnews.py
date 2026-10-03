# -*- coding: UTF-8 -*-

import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "referer": 'https://www.hkej.com/instantnews',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie":'cf_clearance=HR8OMn2w2yPh2FCSB_Pwxix_9wXTvQZUzYWWlwuQg9g-1760514276-1.2.1.1-b_5kn.krQxsjgJg0n2FpE18CFfYE1LNmnM04IiVFtNqOM7WeYJYADi_Pl7m7oFn__eTm41zigMNlPFwaqYqQBvdcZkRsIXfqc0s_lg8x35UKJm4iMeX9O3MfqqWm0pssJFTuHlZTCizQ_BeHGV0BKfm4phN0hAu1wJ4rPalJ0ynLDxy7TmFCb0rUb.CkNmWk3Pn_AQ.056q5NuMsOszlISLYySP9V4yKzxjj1lS1JV0; PHPSESSID=dcun0se8u1v35npei49gepk1um; __utma=231706246.371857075.1760514280.1760514280.1760514280.1; __utmc=231706246; __utmz=231706246.1760514280.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.1.1921937716.1760514280; _gcl_au=1.1.424345055.1760514280; _clck=2jxo4d%5E2%5Eg06%5E0%5E2114; ejUID=188f0581-b713-4ec3-ed34-fb611d24fa67; __utmb=231706246.8.9.1760514804656; AWSALBTG=a1J3OxBv0ZbX0uyggK6qy7f87wDHA1CLvIbthPQuAqnOCKou0udxBl1dJncSmgBS/WaWlNEU6159tvsrVmvFf6v9TdAIAjj0Q01hKkLmSwUPv8uTf/IqTaNBhSWbE0c1fhLAMshcs1I/IckFAw6VRr9LUOAIPTDfcXUtAjZAAgYVcA0Te9yAeGnFFx/dhT5H1qdDlPH2PjvgKfSiEYYfcvwLw4tNIAQ8etO/cCwLP6QvsmrTQ6LM/1WDnQ5z11vRfMdNoKcob4ANr02NIuhelEnxgoLDuWOVqRnqz2yxyZEz4bqsysIEu9abs/nv5RWycCXKkJovAoeNOEZG/e9XGAtSx1fEaWWMgzgs0nL1jXhfhsOY4cu+texXjvsEmI736va93n0jRMURkX9A4IY+ORovAyAQ6G8eXaas7bDs; AWSALBTGCORS=a1J3OxBv0ZbX0uyggK6qy7f87wDHA1CLvIbthPQuAqnOCKou0udxBl1dJncSmgBS/WaWlNEU6159tvsrVmvFf6v9TdAIAjj0Q01hKkLmSwUPv8uTf/IqTaNBhSWbE0c1fhLAMshcs1I/IckFAw6VRr9LUOAIPTDfcXUtAjZAAgYVcA0Te9yAeGnFFx/dhT5H1qdDlPH2PjvgKfSiEYYfcvwLw4tNIAQ8etO/cCwLP6QvsmrTQ6LM/1WDnQ5z11vRfMdNoKcob4ANr02NIuhelEnxgoLDuWOVqRnqz2yxyZEz4bqsysIEu9abs/nv5RWycCXKkJovAoeNOEZG/e9XGAtSx1fEaWWMgzgs0nL1jXhfhsOY4cu+texXjvsEmI736va93n0jRMURkX9A4IY+ORovAyAQ6G8eXaas7bDs; AWSALB=R0fvV9YHY+qG/rDK7ixnlpIu9cDfCTQ3yFAc2oKDM5eSU7xVflRq+AHUaAis3d8PpA8DlMZFvvUhOCjukdfL57ONug9bO17d33kAgGJAgJZVtMkMhKRuDcHmF8oC1R98x+kp55aBq/GddAlyZwpPkK7Djc8jvxDLrrGFRrcjS75a5Gow3SOM4Dcxu8xLLA==; AWSALBCORS=R0fvV9YHY+qG/rDK7ixnlpIu9cDfCTQ3yFAc2oKDM5eSU7xVflRq+AHUaAis3d8PpA8DlMZFvvUhOCjukdfL57ONug9bO17d33kAgGJAgJZVtMkMhKRuDcHmF8oC1R98x+kp55aBq/GddAlyZwpPkK7Djc8jvxDLrrGFRrcjS75a5Gow3SOM4Dcxu8xLLA==; _clsk=kuutsq%5E1760514805600%5E4%5E1%5Ev.clarity.ms%2Fcollect; __gads=ID=dc71249e3b35f890:T=1760514281:RT=1760514805:S=ALNI_MbnCBxfNL1nwlulSTLD-aTZkZKEjw; __gpi=UID=000011a3ee3ba4b1:T=1760514281:RT=1760514805:S=ALNI_MYjlMtpq-fXZnC6JipjKw_-6F1IEw; __eoi=ID=3f7fba0e69e48f9d:T=1760514281:RT=1760514805:S=AA-AfjZelfeoKpXV2ftAwYvCqnwv; _ga_7353J2WJ9W=GS2.1.s1760514280$o1$g1$t1760514805$j59$l0$h0; FCNEC=%5B%5B%22AKsRol-bsXqOdHXJaMnYmSeo1A3zbWKk-w_CThDislYBCl6cIijFD1AWdDb4W_ZyrYB-KSH6q1aWrEn3EDEoybnlfcAOnMreXFz7Fye763Go0w4mdzvyNH_gzD9CsZlOofJEQO70Sf1nJpyu9nL61Ak3dUZ-PnzmUQ%3D%3D%22%5D%5D',
}
base_url = "https://www2.hkej.com"
filename = "./news/data/hkej/list.json"
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split("<div id='article-content'>")[1]
        .split('<div id="hkej_sub_ex_article_nonsubscriber_ad_2014">')[0]
    )
    body = re.sub(r"(\t)\1+", "", body)
    body = re.sub(r"(\n)\1+", "\n", body)
    body = body.lstrip()
    return body


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request("https://www2.hkej.com/instantnews", None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        item1 = soup.select("h4.hkej_hl-news_topic_2014 a")
        item2 = soup.select("h3 a")
        items = item1 + item2
        for index, node in enumerate(items):
            if index < 7:
                a = node
                href = str(a["href"].strip())
                link = base_url + href
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                title = a.text.strip()
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "hkej",
                            "kind": 1,
                            "language": "zh-HK",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
