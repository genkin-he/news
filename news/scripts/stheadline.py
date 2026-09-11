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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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
    "cookie": "ci_session=5bdvsa8ubjet35ke9qsknub8gieiki82; _gid=GA1.2.1190824774.1736757527; _gat_UA-41819048-3=1; AMCVS_E1E31A3C5BB4BED90A495E47%40AdobeOrg=1; s_cc=true; AMCV_E1E31A3C5BB4BED90A495E47%40AdobeOrg=-1303530583%7CMCIDTS%7C20102%7CMCMID%7C07644662150011444184385747985278753106%7CMCAAMLH-1737362327%7C3%7CMCAAMB-1737362327%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1736764727s%7CNONE%7CMCSYNCSOP%7C411-20109%7CvVersion%7C3.3.0; _cc_id=515b9a2e0e2370f87d3d1d6b736b283c; panoramaId_expiry=1736843928426; cto_bundle=TWDrv19KZGhNJTJCbGJQdklpWHZhbHNSSjJvaWlpSmpPSEs4ZFdKcWpjWlM0ektrMVR4dURYeDhrUGdSUTJlY3V6T3BzaU1OQlpqciUyQmdxa2JubXdFd2FXSmE1dDJVUXJDVkdnYjM0R1ZiVTJKRjhGdFBGd3hUOEVkNWhXOUElMkJKdkl4Nm5NS2hnalFhalFmWjRlblM2ZXFqckl2RjhUQnJBNndvZUVLellFUTklMkJ4cjkxSSUzRA; purecookieDismiss=1; s_pn=%E6%98%9F%E5%B3%B6%E6%97%A5%E5%A0%B1.%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E; s_getNewRepeat=1736757553740-New; tp=3257; s_ppv=%25u661F%25u5CF6%25u65E5%25u5831.%25u5373%25u6642%25u65B0%25u805E%2C29%2C29%2C932; s_sq=%5B%5BB%5D%5D; _ga=GA1.1.1170196146.1736757527; _ga_T9RMKL3N37=GS1.1.1736757527.1.1.1736757554.33.0.0; FCNEC=%5B%5B%22AKsRol-aPCS9pWmLEdsQb4avYqJLNDII1xiB5sWDvDyTDTom_XkVJpnlO-G0eWvQl01nZQIKSN_pVUbMm6zgkwea1T4R9NmS9a1zyqdLX-s-_QbhZqXqkXZcH_efPRGBpufqMEV4gl2recPLOgyp_-RKbf8Y9LrrqA%3D%3D%22%5D%5D",
}

base_url = "https://www.stheadline.com"
filename = "./news/data/stheadline/list.json"
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
        soup = body.select_one("div.content-body ")
        ad_elements = soup.select("ad, .img-block, .img_caption, img")
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
        items = soup.select("div.news-detail")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 5:
                break
            title_element = items[index].select_one(".title")
            a = items[index].select_one("a")
            link = base_url + a["href"].strip()
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
                        "source": "stheadline",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.stheadline.com/finance/%E8%B2%A1%E7%B6%93")
