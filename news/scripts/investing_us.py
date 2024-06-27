# -*- coding: UTF-8 -*-
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": "PHPSESSID=3goj1r86ajg2d84f82c2p6nqp7; page_equity_viewed=0; browser-session-counted=true; user-browser-sessions=1; adBlockerNewUserDomains=1719227288; gtmFired=OK; udid=58fd3ff80e401a8378af34b89452a0b1; __cflb=0H28vY1WcQgbwwJpSw5YiDRSJhpofbwDa1j7hdVXk5a; _gid=GA1.2.1878202623.1719227291; usprivacy=1YNN; __eventn_id=58fd3ff80e401a8378af34b89452a0b1; _imntz_error=0; _hjSessionUser_174945=eyJpZCI6IjA4ZDEwZDU4LTVlNWQtNWQ3ZS1hN2U2LWE0MTZiMGEwOWQ3MCIsImNyZWF0ZWQiOjE3MTkyMjcyOTI0NTksImV4aXN0aW5nIjp0cnVlfQ==; pm_score=clear; _cc_id=d88091f4633935077bddfa4a374f0401; panoramaId_expiry=1719313715051; OneTrustWPCCPAGoogleOptOut=false; r_p_s_n=1; adsFreeSalePopUp=3; reg_trk_ep=google%20one%20tap; _hjSession_174945=eyJpZCI6ImM0MzJkMTgyLWVhMzQtNDJkZi05ZjE2LWEzMThiMGQ2ODFiNyIsImMiOjE3MTkyOTg5MDMwOTcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; gcc=US; gsc=CA; smd=58fd3ff80e401a8378af34b89452a0b1-1719301701; cf_clearance=j_lWgdhMV9UfK8_v8vZluf8L_.GTCzAYh4zXynw5tlg-1719301704-1.0.1.1-VG5pg7OtnBqPpgn.2cKvGZLh0iLrsoBnZDppUGKSGhEq4E0iHYPfsHnpNP63PM.HCExWFMSjst3QqKOOejD_sA; lifetime_page_view_count=15; geoC=US; nyxDorf=NzZiNGQsNm02aW1%2FMGI5O2IzMXRmYGBiNzU%3D; page_view_count=29; _gat=1; _gat_allSitesTracker=1; invpc=42; _ga=GA1.2.433675690.1719227291; _gat_UA-2555300-55=1; _ga_C4NDLGKVMK=GS1.1.1719301539.7.1.1719303498.39.0.0; cto_bundle=xZhr2l90VHFJWDI3VEx3OTZ0UzUlMkZYMjVVSjVxOWxIcDRFOVpZNWFxbVJmSXdVTkJKM1V6aDhoQ0U3eVB1YmV5U1llSGdkOVFDUyUyRjJOJTJCanpyb01IUGJPbXZmNkVHMnZONEdsWCUyRmpZYklBUjZxVDFIaVlvJTJGeU9ZRlNoam80UDM4JTJGTTdqdHVOcjVEcDlRJTJGSnR3JTJGWCUyQmRubEZGMTRCRzVBOVp1UVBPU0F6WnglMkZhdTRKNCUzRA",
}
base_url = "https://investing.com"
filename = "./news/data/investing/list_us.json"


def get_detail(link):
    print("investing_us: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split('<span id="comments"></span>')[0]
        .split(
            '<div class="article_WYSIWYG__O0uhw article_articlePage__UMz3q text-[18px] leading-8">'
        )[1]
        .split("<p><em>InvestingPro</em><em>")[0]
    )
    return "<div>" + body + "</div>"


def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request 中放入参数，请求头信息
    request = urllib.request.Request("https://investing.com/news/", None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        body = body.split('<div class="mostPopularsContainer ">')[1].split(
            "window.isAdNotificationEnabled"
        )[0]
        posts = re.findall('.*<a href="(.*)" title="(.*)" class="title">*', body)

        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                link = base_url + post[0]
                title = post[1]
                elements = post[0].split("-")
                id = elements[len(elements) - 1]
                if link in ",".join(links):
                    print("investing_us exists link: ", link)
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
                          "link": link,
                      },
                  )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("investing_us request error: ", response)


try:
    run()
except Exception as e:
    print("investing_us exec error: ", e)
