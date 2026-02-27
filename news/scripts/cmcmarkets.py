# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en,zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "OptanonAlertBoxClosed=2025-04-25T06:40:39.700Z; _gcl_au=1.1.123003522.1745563241; _ga=GA1.1.481219085.1745563241; IR_gbd=cmcmarkets.com; sa-user-id=s%253A0-1874c8d3-7a98-5445-538c-81b6c2bcb495.Hl2POnqdxdkkrhyyOaF0xBeJ%252Bzk5vlkfqH4vN6VZVBM; sa-user-id-v2=s%253AGHTI03qYVEVTjIG2wry0lVvHVHk.I5vjcLwusGMctJ0i9Usvc690C1TZ%252BZD%252BP6K4sKAxLTI; sa-user-id-v3=s%253AAQAKINIFgcrWeRbczg01g4SDP_Drpaepk7nzjOhGzj9KawQrEMABGAQg6dyswAYwAToEbwsAqUIEjfvcaw.3E4JkHzun4imHXeGKiaJyLf5t9OA3np%252B6vuEjU4XGqY; _clck=1c0nbni%7C2%7Cfvd%7C0%7C1941; _hjSessionUser_117155=eyJpZCI6ImJlM2FjZDYzLWZkYWYtNTU4NS05NTc5LTBhZGJkZjY0MzgxZSIsImNyZWF0ZWQiOjE3NDU1NjMyNDIxODgsImV4aXN0aW5nIjp0cnVlfQ==; cncode=HK; __utmzz=utmcsr=(direct)|utmcmd=(direct)|utmccn=(not-set)|mdevid=e20a1b43-3fec-48b2-3dcd-bb30444974f2|MPID=-6736787983516461804|GA=GA1.1.481219085.1745563241|cp1=/en-gb/news-and-analysis/us-dollar-entrenches-key-support-time-to-assess-the-damage|utmzz_session_id=7672687034; __utmzzses=1; _hjSession_117155=eyJpZCI6ImE2OWQxNDk2LTc1OTQtNDliYS1hNGUwLTZmMzE3OTI3MWEyMCIsImMiOjE3NDU1NzM1MTM4NjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; site=UK3; _rdt_uuid=1745573737793.6d19f2f9-fac3-484b-b873-eb542090f5e0; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Apr+25+2025+17%3A36%3A58+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202501.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=6171ae46-0959-4739-b9e4-dbfeeb3178c2&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; mprtcl-v4_B92A5B27={'gs':{'ie':1|'dt':'2a08c1fe05723347b37e0b7a853e0572'|'cgid':'de8b5192-15d0-42ec-65e3-2cdfbef44783'|'das':'e20a1b43-3fec-48b2-3dcd-bb30444974f2'|'csm':'WyItNjczNjc4Nzk4MzUxNjQ2MTgwNCJd'|'sid':'36378774-AB1D-42E7-4CF8-328DFBA0F291'|'les':1745573819059|'ssd':1745573512507}|'l':0|'-6736787983516461804':{'fst':1745563241945|'con':'eyJnZHByIjp7InN0cmljdGx5IG5lY2Vzc2FyeSBjb29raWVzIjp7ImMiOnRydWUsInRzIjoxNzQ1NTYzMjQxOTUxLCJkIjoic3RyaWN0bHkgbmVjZXNzYXJ5IGNvb2tpZXMiLCJsIjoiaHR0cHM6Ly93d3cuY21jbWFya2V0cy5jb20vZW4tZ2IvbmV3cy1hbmQtYW5hbHlzaXMvdGhlLXdlZWstYWhlYWQtdGVzbGEtZWFybmluZ3MtZ2xvYmFsLXBtaS1kYXRhLXVrLXJldGFpbC1zYWxlcyJ9LCJwZXJmb3JtYW5jZSBjb29raWVzIjp7ImMiOnRydWUsInRzIjoxNzQ1NTYzMjQxOTUxLCJkIjoicGVyZm9ybWFuY2UgY29va2llcyIsImwiOiJodHRwczovL3d3dy5jbWNtYXJrZXRzLmNvbS9lbi1nYi9uZXdzLWFuZC1hbmFseXNpcy90aGUtd2Vlay1haGVhZC10ZXNsYS1lYXJuaW5ncy1nbG9iYWwtcG1pLWRhdGEtdWstcmV0YWlsLXNhbGVzIn0sImZ1bmN0aW9uYWwgY29va2llcyI6eyJjIjp0cnVlLCJ0cyI6MTc0NTU2MzI0MTk1MSwiZCI6ImZ1bmN0aW9uYWwgY29va2llcyIsImwiOiJodHRwczovL3d3dy5jbWNtYXJrZXRzLmNvbS9lbi1nYi9uZXdzLWFuZC1hbmFseXNpcy90aGUtd2Vlay1haGVhZC10ZXNsYS1lYXJuaW5ncy1nbG9iYWwtcG1pLWRhdGEtdWstcmV0YWlsLXNhbGVzIn0sInRhcmdldGluZyBjb29raWVzIjp7ImMiOnRydWUsInRzIjoxNzQ1NTYzMjQxOTUxLCJkIjoidGFyZ2V0aW5nIGNvb2tpZXMiLCJsIjoiaHR0cHM6Ly93d3cuY21jbWFya2V0cy5jb20vZW4tZ2IvbmV3cy1hbmQtYW5hbHlzaXMvdGhlLXdlZWstYWhlYWQtdGVzbGEtZWFybmluZ3MtZ2xvYmFsLXBtaS1kYXRhLXVrLXJldGFpbC1zYWxlcyJ9fX0='}|'cu':'-6736787983516461804'}; _uetsid=34c36f2021a011f088e4ef618237258a; _uetvid=34c38f2021a011f0b1a1f31c068e85ee; IR_15933=1745573821905%7C0%7C1745573821905%7C%7C; _ga_VW93W7Y24M=GS1.1.1745573513.3.1.1745573823.2.0.0; _clsk=116ga8h%7C1745573823628%7C7%7C1%7Cn.clarity.ms%2Fcollect",
}

base_url = "https://www.cmcmarkets.com"
filename = "./news/data/cmcmarkets/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        body = BeautifulSoup(resp, "lxml",from_encoding=response.encoding)
        soup = body.select_one(".article-content")

        ad_elements = soup.select("script,style,.news-article-widget,.block")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # 使用requests发送请求
    response = requests.get(
        "https://www.cmcmarkets.com/en-gb/news-and-analysis", headers=headers
    )
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml", from_encoding=response.encoding)
        items = soup.select(".article-feature")
        for index in range(len(items)):
            if index > 1:
                break
            link = base_url + items[index]["href"].strip()
            title = items[index].select_one(".feature-headline").text.strip()
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
                        "source": "cmcmarkets",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename, encoding=response.encoding)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
