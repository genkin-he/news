# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie": "pgv_pvid=4789840291; _qimei_uuid42=1890d0b380a100ae7892a3d5634134a3f2ecf2bb0e; pac_uid=0_DmwAW53xw9Qb1; _qimei_fingerprint=aeabff70721dd0ba31bdff8e1e2ef645; _qimei_h38=bafb75bb7892a3d5634134a30300000f41890d; _qimei_q36=; _clck=3562680173|1|fp8|0; RK=QLclrsSTG8; ptcz=a70854edd76a5e859ffae97817e32974ded748c6500099d32734ab44388feaec; suid=user_0_DmwAW53xw9Qb1; o_cookie=625118164; RECENT_CODE=09988_100%7C600519_1; w_token=87_D8KSmeaBx1IaLiPDbm8iF1hdslHXroVsZiHuQNWWA6eKbXZ0d1yuFOkpHRVw-OCBVWuaiumKXQTS_sYb4pGiovB1fPbE7NgJjTfvLe7dQk0; current-city-name=chengdu; lcad_appuser=EAEBE1F6F8B08D84; lcad_o_minduid=WxwK8cqQoWprEO-JWAEj3GvWi_LMorte; lcad_LPPBturn=406; lcad_LPSJturn=694; lcad_LBSturn=342; lcad_LVINturn=859; lcad_LDERturn=773",
    "Referer": "https://news.qq.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://news.qq.com"
filename = "./news/data/qq/list.json"
current_links = []
post_count = 0

util = SpiderUtil()


def get_detail(link):
    print("qq link: ", link)
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup_elements = lxml.select(".rich_media_content")
        if not soup_elements:
            soup_elements = lxml.select(".article-content-wrap")
            if not soup_elements:
                log_action_error(
                    "qq error: 未找到{} .article-content-wrap 元素".format(link)
                )
                return ""
        soup = soup_elements[0]

        ad_elements = soup.select("style")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        print("qq request: {} error: ".format(link), response)
        return ""


def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        posts = json.loads(resp)["data"]["list"]
        for index, post in enumerate(posts):
            if index > 5:
                break
            if post["article_type"] != 0:
                continue
            link = post["url"]
            if link in ",".join(links):
                print("qq exists link: ", link)
                continue
            title = post["title"]
            pub_date = post["publish_time"]
            author = post["media_name"]
            id = post["article_id"]
            image = post["img"]
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": pub_date,
                        "link": link,
                        "author": author,
                        "source": "qq",
                        "image": image,
                        "kind": 1,
                        "language": "zh-CN",
                        "id": id,
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 25:
                articles = articles[:25]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("qq request error: {}".format(response))


link1 = "https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list?sub_srv_id=tech&srv_id=pc&offset=0&limit=10&strategy=1&ext={%22pool%22:[%22high%22,%22top%22],%22is_filter%22:10,%22check_type%22:true}"
link2 = "https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list?sub_srv_id=finance&srv_id=pc&offset=0&limit=10&strategy=1&ext={%22pool%22:[%22high%22,%22top%22],%22is_filter%22:10,%22check_type%22:true}"
util.execute_with_timeout(run, link1)
util.execute_with_timeout(run, link2)
