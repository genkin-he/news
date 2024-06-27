# -*- coding: UTF-8 -*-
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": "browser-session-counted=true; user-browser-sessions=1; adBlockerNewUserDomains=1719227288; udid=58fd3ff80e401a8378af34b89452a0b1; _gid=GA1.2.1878202623.1719227291; __eventn_id=58fd3ff80e401a8378af34b89452a0b1; _hjSessionUser_174945=eyJpZCI6IjA4ZDEwZDU4LTVlNWQtNWQ3ZS1hN2U2LWE0MTZiMGEwOWQ3MCIsImNyZWF0ZWQiOjE3MTkyMjcyOTI0NTksImV4aXN0aW5nIjp0cnVlfQ==; pm_score=clear; _cc_id=d88091f4633935077bddfa4a374f0401; panoramaId_expiry=1719313715051; PHPSESSID=eeqbtsmmj6ree52j1f5ifta9lf; geoC=CN; Hm_lvt_a1e3d50107c2a0e021d734fe76f85914=1719286973; _imntz_error=0; cto_bundle=uRyY7F90VHFJWDI3VEx3OTZ0UzUlMkZYMjVVSiUyRiUyRnN5QW5vcWxKNWt1U0ZYdWVBUWk2NWNaRzgwdXc0WEd1SnN3eVBhJTJCSzdpUEVPWURvYVdEJTJCMURRNmk3QjFVbnE4d2NaRGpIc3R2d0prQiUyRkwlMkZ1NlVaMnNob3gzUjk5MkJDdEp5Q3FIRDdRZkpjZ1JJWEppZkF3NW55QTdsJTJCZEYxbWVSVE5wUjg4OGZyaG5ZeDhmYmZNJTNE; reg_trk_ep=google%20one%20tap; adsFreeSalePopUp=3; lifetime_page_view_count=8; cf_clearance=BROX_JJO6ETlAcWXyGKHSZSuvnkTxJ0pe2Qwju43kuU-1719296449-1.0.1.1-1.F6mNOZ0u5d8W6PkJ9wxHrzMF9B0NNy7ykwCy9iL_it3fgmOjwKNAxf9m1xL_OhbmtD9n.b8dJUcCt87GYFwQ; nyxDorf=MTZlNjFgYyFmMWlhbzRifmIyP2VjYjsnMjJvbmdh; Hm_lpvt_a1e3d50107c2a0e021d734fe76f85914=1719296456; invpc=33; page_view_count=26; _ga=GA1.1.433675690.1719227291; _ga_C4NDLGKVMK=GS1.1.1719295804.5.1.1719296455.43.0.0; smd=58fd3ff80e401a8378af34b89452a0b1-1719298870; _gat_allSitesTracker=1",
}
base_url = "https://cn.investing.com"
filename = "./news/data/investing/list_cn.json"


def get_detail(link):
    print("investing_cn: ", link)
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
        .split("<p>还在为买什么而犹豫不决吗")[0]
    )
    return "<div>" + body + "</div>"


def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request 中放入参数，请求头信息
    request = urllib.request.Request("https://cn.investing.com/news/", None, headers)
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
                id = post[0].split("article-")[1]
                if link in ",".join(links):
                    print("investing_cn exists link: ", link)
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
        print("investing_cn request error: ", response)


try:
    run()
except Exception as e:
    print("investing_cn exec error: ", e)
