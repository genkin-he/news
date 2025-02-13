# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "ak_bmsc=CB9A666C9AFDAA687BD4A7B12EA8D00C~000000000000000000000000000000~YAAQddgjF9t0Z7aTAQAA2E6jLBoSuVV/cgF2p+cU6idOPFKsmknXFK/lSsJi7Ehkvss3gx0Qq+lGtR2kInYhhh6dT2wcELPDRsi5DPf1DYxsBiWJFaX0FmHmOOMP6g2xHq3tGPyut8tCjBGKN/wBtALD3iUxSFLmEoKr5nQuQghyF4dGmFW3Oo6qGBjHFLQO5NcvyHGue3R6V3m+XpNl6JdmEgdnh4movzQ9qFTmjAXQ8y2wo4Hk8TsVKFJeG77narlH3PcW/yOIHw2eS6hfON/hWYhfR/uPTpx85ULn3GfIZJrt08qLW0PD1SaPCdBo+Fa0FNTf4DolTHWpNShJf9Z7eCWt93jbAMvNVvrR/sFTYAiF29jPP4lglBxqG13NwlP7uJPppKuIu4VBLro7SKkrjcO++q8ZiDis6pl0mWxfBDQfpLhlmvF16OiivATtuSu2yF1FCKZx; TS01c09a27=0102e294407eb02dbb7f53767e62fefdb01347c7bea8112bcf472493e7323c4a3c9dca2045c538c94e01eaff60b22566b8a72008af3c9e80ff34e046170eb16b70549063bd; bm_sv=231F2EB612C6405F95E8D7732732C8A5~YAAQddgjF950Z7aTAQAAnVCjLBo32lbXFq+QrprlXhkvCYOx3uCadOJzZ1q/0OfaG2rOXocVz23Wan2XCuX+EPxsrMeASAdFxs6qUaMdmuN9BIY9oyE6qPQE2WKbpDlQjO2+Am7LQk0sCbczvPx2klapZXa5cql1B84BP4nHoZzqB7MG0AX2MUCNntiTQEbSz10SYXPBwIqUYMUNS0lSvxe93/3bFutJquacr08nf/Zz+j44fhzMNLxpOTfKuHku1MoWqCbX~1; _gcl_au=1.1.1282362216.1735915688; _ga=GA1.1.1345429448.1735915689; _ga_ZQWF70T3FK=GS1.1.1735915688.1.0.1735915688.60.0.0; __hstc=241090844.a1a57f9bd44d63b2a99b2f7f77683144.1735915689304.1735915689304.1735915689304.1; hubspotutk=a1a57f9bd44d63b2a99b2f7f77683144; __hssrc=1; __hssc=241090844.1.1735915689304; OptanonAlertBoxClosed=2025-01-03T14:48:35.655Z; OptanonConsent=isIABGlobal=false&datestamp=Fri+Jan+03+2025+22%3A48%3A35+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.4.0&hosts=&consentId=57f50885-b1c9-4e84-a9c7-d84d75de24cb&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1",
}

base_url = "https://www.businesswire.com/"
filename = "./news/data/businesswire/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    if link in current_links:
        return ""
    print("businesswire link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".bw-release-story")[0]

        ad_elements = soup.select(".bw-fsa")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("businesswire request: {} error: ".format(link), response)
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".bwNewsList > li")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].select(".bwTitleLink")[0]["href"].strip()
            title = items[index].select(".bwTitleLink")[0].text.strip()
            if has_chinese(title):
                continue
            if link in ",".join(_links):
                print("businesswire exists link: ", link)
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
                        "source": "businesswire",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("businesswire request error: {}".format(response))


util.execute_with_timeout(print,"businesswire exec 超时")
