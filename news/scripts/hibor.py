# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
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
    "upgrade-insecure-requests": "1",
    'Cookie': 'safedog-flow-item=A487CB9015593BAC637092F0954B86FD; c=; Hm_lvt_d554f0f6d738d9e505c72769d450253d=1724225376; HMACCOUNT=5ACB58B6AB3FBE4A; ASP.NET_SessionId=wtbszgyvtt3vz302lrvn34kc; MBname=HW776439194; MBpermission=0; robih=ZXEWsNqPoQqMsRuNrQwPnR; ASPSESSIONIDCGQSAQRR=ABICDKMCJGJCEJOMENDDHHCI; ASPSESSIONIDCWDSARSS=LALAFPNCCJNBHMGPCKCBOEFM; Hm_lpvt_d554f0f6d738d9e505c72769d450253d=1724238476'
}

detail_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "c=; Hm_lvt_d554f0f6d738d9e505c72769d450253d=1724225376; HMACCOUNT=5ACB58B6AB3FBE4A; ASP.NET_SessionId=wtbszgyvtt3vz302lrvn34kc; MBname=HW776439194; MBpermission=0; robih=ZXEWsNqPoQqMsRuNrQwPnR; ASPSESSIONIDCGQSAQRR=ABICDKMCJGJCEJOMENDDHHCI; ASPSESSIONIDCWDSARSS=AHLAFPNCEMAIJPENIJKOBFLD; safedog-flow-item=8D7B570DDDD5327563CA73410A3D456A; ASPSESSIONIDQUDSBQQS=CIIHJPPDMKOKOMNKDIHONECH; Hm_lpvt_d554f0f6d738d9e505c72769d450253d=1724391550; ASPSESSIONIDQECTBSTS=NEJIKNAAJCFBJPDEOHLIIING",
    "Referer": "https://www.hibor.com.cn/data/a667000ad4265496c8ad4a695931acbd.html",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

base_url = "https://www.hibor.com.cn"
filename = "./news/data/hibor/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def parse_detail_id(link):
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        scripts = soup.select("script")
        for script in scripts:
            if "var ncid = " in script.text:
                result = re.findall(r'.*var ncid = \'(.*)\';*', script.text)
                if len(result) > 0:
                    return result[0]
        return ""
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def get_detail(link, source):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    id = parse_detail_id(link)
    if id == "":
        return ""
    
    data = "ncid={}".format(id).encode('utf-8')
    request = urllib.request.Request("https://www.hibor.com.cn/hiborweb/DocDetail/NewContent?ncid=0f162bc8-3a7d-41ef-bf4d-dc7fc9621b56", data=data, headers=detail_headers, method="POST")
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select(".abstruct-info")[0]
        
        ad_elements = soup.select('.related_stories_left_block')
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
            
        # 追加
        new_tag = lxml.new_tag('p')
        new_tag.string = "来源: {}".format(source)
        soup.append(new_tag)
        return str(soup)
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""
    
def run():
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.hibor.com.cn/elitelist.html", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".trContent")
        for node in nodes:
            if post_count >= 3:
                break
            link = base_url + str(node.select("td:nth-child(2) > a")[0]["href"])
            if link in ",".join(links):
                util.info("hibor exists link: {}".format(link))
                break
            pub_date = str(node.select("td:nth-child(6)")[0].text)
            title = str(node.select("td:nth-child(2) > a")[0]["title"])[:-7]
            titles = title.split("-")
            security_company = ""
            if len(titles) > 0:
                security_company = title.split("-")[0]
                title = title.replace("{}-".format(security_company), "")
            post_count = post_count + 1
            description = get_detail(link, security_company)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": pub_date,
                        "link": link,
                        "author": "hibor",
                        "source": "hibor",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
