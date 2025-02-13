# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

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
    "cookie": '_pxhd=738c13fa1501390f79517e5207bde4109ce0145e886564416862aec5a06dbd13:8cd543b8-d21a-11ef-b2ef-fa2ddf210381; referralId=Direct; pxcts=8e30d4b9-d21a-11ef-9933-a14a07e0c5ba; _pxvid=8cd543b8-d21a-11ef-b2ef-fa2ddf210381; usprivacy=1---; _cb=ChFN-m1a4OsDZfy3D; minVersion={"experiment":288997026,"minFlavor":"headlinesmi-1.17.1.140.js100"}; repeat_visitor=1736819699447-997387; bob_session_id=1736819699447-143786; BCSessionID=f05e77f1-7013-4e8d-92e7-75e713c3903b; OTGPPConsent=DBABBg~BUUAAAGA.QA; s_ips=244; s_ppv=thehill%253Anews%2C4%2C4%2C4%2C244%2C25%2C1; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_cluster=sgp3; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_identity=CiY0NTE2MDYwMzE0NzgwNTE3Mzk4NDE0MjIxMTYyNTY5ODA1MjIxNFITCJz0lZTGMhABGAEqBFNHUDMwAPABnPSVlMYy; permutive-id=9104b247-ed05-470a-9dc0-468a50f40db2; s_tp=6303; s_plt=9.49%2Cthehill%3Anews; seg_sessionid=0e40955a-3c8c-4029-b123-d84d8fc38090; _cb_svref=external; OneTrustWPCCPAGoogleOptOut=true; sailthru_pageviews=2; sailthru_content=e8b25caad75cd79293442f3d1a30c1fa; sailthru_visitor=f782a11e-9713-4abe-aace-dd557e57e122; _chartbeat2=.1736819697308.1736819740469.1.BZmnOmOfp1I5xdGYvQ_o8BPoFBA.2; minUnifiedSessionToken10=%7B%22sessionId%22%3A%22abf721c6ba-cba08a3e65-e6cb668360-c5304338b7-fd9b66c50a%22%2C%22uid%22%3A%22246f561607-39b414d2bb-fb04b3617d-dc0c9394cc-14b5c5f9d7%22%2C%22__sidts__%22%3A1736819740598%2C%22__uidts__%22%3A1736819740598%7D; AMP_TOKEN=%24RETRIEVING; last_visit_bc=1736819740639; _px2=eyJ1IjoiYTdmNGI2YjAtZDIxYS0xMWVmLTljODUtMTc4ZmE5ODQwY2NmIiwidiI6IjhjZDU0M2I4LWQyMWEtMTFlZi1iMmVmLWZhMmRkZjIxMDM4MSIsInQiOjE3MzY4MjAwNDE1NTUsImgiOiJjY2IyYzRkNTc2OTJjYjk3MDI1OWY3ZWExMDNmYWY0YzQ3OGNmMTVjMDE3ZmFjMTFjYjQ5YTE5ZTYzNDcxYzc4In0=; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jan+14+2025+09%3A55%3A43+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=8ea0fb5f-8620-43d3-bbf2-45119f188e30&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fthehill.com%2Fnews%2F&GPPCookiesCount=1&groups=C0001%3A1%2CSPD_BG%3A0%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0',
}
base_url = "https://thehill.com/news/"
filename = "./news/data/thehill/list.json"


def get_detail(link):
    print("thehill link: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".article__text")[0]

        ad_elements = soup.select(".ad-unit,.hardwall, style, script")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("thehill request: {} error: ".format(link), response.status)
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://thehill.com/wp-json/lakana/v1/template-variables/",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["sidebar"]["just_in"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                kind = post["post_type"]
                id = post["id"]
                title = post["title"]
                link = post["link"]
                if link in ",".join(links):
                    print("thehill exists link: ", link)
                    break

                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "kind": kind,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "thehill",
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("thehill request error: {}".format(response))


util.execute_with_timeout(run)
