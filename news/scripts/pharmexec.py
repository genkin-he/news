# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from datetime import datetime
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "DNT": "1",
    "Host": "www.pharmexec.com",
    "upgrade-insecure-requests": "1",
    "cookie": "f5avraaaaaaaaaaaaaaaa_session_=LOBGKMJDLBLOFGAGHOKDAIMPMJAHPAPKGKEFADBHHJJCJDKJEOCALIBILNPHOPMPFEJDBMONLCOFCIPACCIANCCJFJMNJJIOFOLGBNNJGGLAKFNDPHIKAJCLHCCGBPNO; _gcl_au=1.1.1138836933.1725261422; _ga=GA1.1.836911480.1725261423; hubspotutk=d2febbe79b52fd64b53d775bd0c6e287; __hssrc=1; OptanonAlertBoxClosed=2024-09-02T07:19:07.128Z; ak_bmsc=9504B952F7E3FE9A242638EF860D6C6D~000000000000000000000000000000~YAAQs8HJF8tdeJmRAQAAGZA7shiAHPuz8W3DLDZrBIdFi+LiEN8rodH+hNFIp8y0DoyHSdgrVIp1XtVM6fvHmEdxbIUJPnLgFu5f8jUNLuNYX8MG2xiR8KUNAElr7tdAAr0FSmkPufeOqpOP1QwcOrInaFVwi7dDvFgkoJ3VJ4acnCcqo9F5NRCv8CSxoshvGhiU9qiF4ggFsgA+XZlzxTdwBpRNRIn2ArC8Jy9fxh928yRCB2mDilljRKjQ9pHrxxQfA3kp7u2RO+i0znpiGHosSduAri2r8VMwMg8GDB073CU9pXTpWYUzvVE+3lBXvme7I/X8yq9YrYoNMi3pugPpH4Bn9lgUVnhmchDBwuEBZnkviHOjImPbNT34FZp1b/qxrq/c+W2PlctCYPoI0PTyILmQrzv5JFC/SrRP85anJ30axOaPGVLzraS2Ftst+g/QWVzLm5LGMw==; __hstc=241090844.d2febbe79b52fd64b53d775bd0c6e287.1725261433591.1725261433591.1725272135885.2; portal.JSESSIONID=XLb5mVQNZypMkQHnhV4c0x1hnThwxTQgJvhmLjNmj9Kmp7nlXYZC!2023601388!-481950389; TS01d0bfe4=0102e294408e66faebdbb710f1e420c9931ea4c2aa41cc75a6bac4ac00319f8bb2c02526a6ec9a769c308660e715feb9370b3b61e353a961ee9dfad0cb2e1a9c866fad187e8e2c51734a0131537d76f0182b503ff3; TS01c09a27=0102e2944048d352681ad6b440182c19c33782875b1359f4d330502669f92b79350eba8c9caf6ea9b79b2e8cb09242a9defa3049af11ea8163dc6589e42e916000b66a243c; bm_sv=B5A0F47C1FC207D26C565292AE095C4D~YAAQddgjF/rB25iRAQAAxulQshj2pR28Vbgw3Pyc/jLkn43fAkqoC6Wez4BfPFcctdGIRZyX7hBmXkq7on6S0wR1l3rlmzEPZVbQ2jZzNJDpNv4Lk8lfsDFEFf7Spv1udy4LR8x3I/BAOUtBm97GdGssbDwe+1SMSm25hbCtscVeQhLZJm2kQYwSacxwJZDNUW6L74AE3Q5SPplo/sGAZ5pInx4gJRs/+h1/E77LWhKMGJgg2FfB0YjIbbqH9qS+uAtc9fmiwg==~1; OptanonConsent=isIABGlobal=false&datestamp=Mon+Sep+02+2024+18%3A38%3A52+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.4.0&hosts=&consentId=f5a2fc7f-4244-43bb-9518-d85b5a16100f&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1&geolocation=CN%3BSC&AwaitingReconsent=false; _ga_ZQWF70T3FK=GS1.1.1725272130.2.1.1725273533.55.0.0; __hssc=241090844.14.1725272135885",
}

base_url = "https://www.pharmexec.com/"
filename = "./news/data/pharmexec/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one("#block-content")

        # 移除 astro-island 元素
        astro_elements = soup.select("astro-island")
        for element in astro_elements:
            element.decompose()
        
        # 移除 article 元素
        article_elements = soup.select("article")
        for element in article_elements:
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
    response = urllib.request.urlopen(request, timeout=3)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "xml")
        items = soup.find_all("item")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].link.string.strip().replace("onclive", "pharmexec")
            title = items[index].title.string.strip()
            pub_date = util.parse_time(
                items[index].pubDate.string.strip(), "%a, %d %b %Y %H:%M:%S GMT"
            )
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
                        "pub_date": pub_date,
                        "source": "pharmexec",
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
    util.execute_with_timeout(run, "https://www.pharmexec.com/rss")
    # detail = get_detail("https://www.pharmexec.com/view/collaborations-advancing-antibody-drug-conjugates-treatments-autoimmune-diseases")
    # util.info(detail)

