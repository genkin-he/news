# -*- coding: UTF-8 -*-
from datetime import datetime, timezone, timedelta
import logging
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import gzip

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "dnt": "1",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": 'bm_mi=337D321AAA9B239A9E0B9A90DC44352A~YAAQ0L0oF/gcAUKRAQAA/bjTRRjHlT4QfQbVxfedJHGqb1GCVbIarX8UPVLM2GxZmcfSA8syy5gcSzEorzizXUIwPvEusVR/fQdtk5iF/JQSOdPe7blzuDy2NJziLWIM7FmCX/gg/5zdyfo6VY4GwlwiVCdt6wVGOC3vQ9wBvKiF3tA1ojIXaZRWRQGDcPcjyQwJtMvr645RRQhQeHVRFATgs2f0sP8sNdzShHpWTm4G0ee/oi5c32QaYBcYlMqJW23jVl724ejG1zd8s8GF7awZWbLZfCUFHet8u7qq6uXpi7NJtcFxHGGCpA==~1; entryUrl=https://www.nasdaq.com/; _biz_uid=5bd685454d8642c8a0500fffc74879e9; volatileMarket=true; entryReferringURL=https://www.nasdaq.com/; FCNEC=%5B%5B%22AKsRol9Ej-fhOxzSzGH_20ZDYnwo8WPfsups21EuS9OEq1pNrpQ-NJO_cjR9R7WMvtQBi6Zim8SolCFv5jvSs28Nx-zOG17MKhC9eM4Eoq-zeCIxdp5cyZisEr7Zr0KfuokTxZWoqMuPzuaykQlCRGxORVlbYpeNNQ%3D%3D%22%5D%5D; _biz_flagsA=%7B%22Version%22%3A1%2C%22XDomain%22%3A%221%22%2C%22ViewThrough%22%3A%221%22%7D; _biz_nA=2; _biz_pendingA=%5B%5D; ak_bmsc=909537EF0B12265B87FE92B435983110~000000000000000000000000000000~YAAQ0L0oF9EdAUKRAQAAI8TTRRhjlyI2mRxyEnPKdmGvrAcD+DvYSrZBfVDVHDzvzRLxaBJkvgSVPjaEWDmD4Ne02a+F4R+eHBGNWnjIbsS3J+58dfTlJVvtn7D6h9ck4pe/jvdZLMN5FisehRwUgFmfwKF5L8mL3LElkDh7E2EWCUbDuyxVPwCnxB9rApy1f1LykXMK3yClRz3kuwP5aWgFjbCcNC5tqY2aMS5Lbb6+xYFx7g0swXm0IU0zlAd8GMFW/SHVOnCEMcI0KYUt10ig1rLIwvmEEcIEoiVj8z9c+KECjWc7AfZyrSzFvsR6Z6aBfNHHwcQunZqpnigCYUCn4/zjuTd2srfl5p4kdRMx0WFBf/ePXsVuGXL9DbIpiEHYW2sdSDbVAHmQNrpyzR37B6tYiBzPQytWHoJCFzwNJo+YIAGkUohKMNM+Y/DjBlZy9NMgF3EPHAKjocF95cqUZJ1Q5tgrzhg=; bm_sv=0AA36D5E144DAEA1898290A2C334B5B3~YAAQ0L0oFyAfAUKRAQAAXODTRRgpP88pcigmGDvy0oTnejESdMamtIyczRmiNq2xq02vf7KmW4DJwWDNRysNlvLbclEGelJbWif+V23dyxdHE02svcMtcoAFDL/JKuDVFTJM0nd2eaAZ2KHciuZlO7d1+bLBnthavXnJdG1QcmeYGCDNSiP0soUCper8IWE5jR39hYchDIPhdPlLnsvWvtoj6JD2eU90Y28tnx+Lgt+iLFmYTKy4UMGwZW4TVAElFg==~1',
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

base_url = "https://www.nasdaq.com"
filename = "./news/data/nasdaq/list.json"
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
        content = ""
        if response.headers.get('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=response) as f:
                content = f.read().decode('utf-8')
        else:
            content = response.read().decode("utf-8")
        body = BeautifulSoup(content, 'lxml')
        soup = body.select(".body__content")[0]
        
        ad_elements = soup.select('.ads__inline, .body__disclaimerscript, .video__inline, .taboola-placeholder')
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup)
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(base_url + "/api/news/topic/latestnews?offset=0&limit=10", None, headers)
    
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]["rows"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["id"]
                title = post["title"]
                author = post["publisher"]
                link = base_url + post["url"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                description = get_detail(link)
                if description != "":
                  insert = True
                  articles.insert(
                      0,
                      {
                          "id": id,
                          "author": author,
                          "title": title,
                          "description": description,
                          "link": link,
                          "pub_date": util.current_time_string(),
                          "source": "nasdaq",
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


# try:
#     run()
# except Exception as e:
#     util.info("nasdaq exec error: {}".format(e))
#     logging.exception(e)
