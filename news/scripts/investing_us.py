# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
from util.util import history_posts, parse_time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Domain-Id": "www",
    "Cookie": 'udid=1c25bd1070d8dacc320d7259d40ff556; smd=1c25bd1070d8dacc320d7259d40ff556-1724828406; video_location_variant=3; __cflb=02DiuGRugds2TUWHMkimYPAcC3JQrXKkBsJbTL5mkdrfv; adBlockerNewUserDomains=1724828408; _imntz_error=0; _hjSession_174945=eyJpZCI6IjI4MjY2YzNlLWMyNjAtNDYzYS04ZjBhLWFiNzRiYTFhYzZhNiIsImMiOjE3MjQ4Mjg0MDg5NzEsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; _iiq_fdata=%7B%22pcid%22%3A%22898e09f5-f2ed-d333-dfa0-ba24438865b0%22%2C%22pcidDate%22%3A1724828409136%7D; __eventn_id=1c25bd1070d8dacc320d7259d40ff556; r_p_s_n=1; pm_score=clear; _cc_id=ffd7caa856735ecac4a5412eabced70d; panoramaId_expiry=1724914821008; panoramaId=7918f20d0c3ee4ee08cb2a064d6da9fb927af0ceb00d023b803569e4c2b1f891; panoramaIdType=panoDevice; PHPSESSID=jvct4c7uk4q7toii9ke4odr9jb; geoC=HK; page_equity_viewed=0; browser-session-counted=true; user-browser-sessions=1; gtmFired=OK; _gid=GA1.2.583159469.1724828455; _hjSessionUser_174945=eyJpZCI6IjlhYTlhMmJjLWY5MjEtNWQwYy1iYThmLWQ3OWE0ZDRlY2FhYyIsImNyZWF0ZWQiOjE3MjQ4Mjg0MDg5NzAsImV4aXN0aW5nIjp0cnVlfQ==; editionPostpone=1724828466172; adsFreeSalePopUp=3; nyxDorf=MzdjOGQ3MXNlMW1lbjkyLjdkYTo%2FMGJ%2BYmIwNWFv; _ga=GA1.1.1345941948.1724828409; gcc=HK; gsc=; __cf_bm=bijEBSY3w4TaX6xsHWsVzCiUtmv25IhnsTad.eVvc3s-1724828642-1.0.1.1-Nb3ZzCHtTHu5UeN8S5VTWXOYxw20X6LTh.gJeCBBsXBxeRzrjmha15QTwFfhHCWd51QxPosQuwpmyyxmNazzZmq_Vdh6L6XMzDZivVUD788; cf_clearance=r0bB1omiy_v0eXxdqRG22dFfVZ3w5aBr9eZfLbGmeq8-1724828644-1.2.1.1-i4LF7H2qG.h5xRribZmaE4hKe90L6YNoLwwDWseVnCdtpPdR6RgMBZpd5TyjK9AsaF7WHQxLNIZklEbDEu6M_.xylRn8.XYPPheBA.38e5NICNLSR3_PsTHsUYUZElTfUuoS21zBHLb3VmbQ9S.0Q0QyP7k2XpJb0DN_Q6nQkr8wKLuGvDaryBUaeqCw7Qo3JkaXLDHoiMP5RWpohaYzMM0NumAu1Jo6xKkeoUkxSrOYVd5FTPmeSxCTmVdymWck8mZBsvmY7XZhcutUzwdDIM34OQvqCRAGYtbOlBEe6PEwTtKxU6Q3uRP9DehZ17NwL2LKSWvb75UenntA7QozN2Byeb7DIPoE_W0SHtLPFxvtia7DCLa3gdb0CJTYVRmJs0fWjE.u6mWSWk06RayDWw; reg_trk_ep=google%20one%20tap; cto_bundle=r4-iw19Ja0pSVk1wSkFRV2lub01xTFFwVlVhQzNZSDZraklzSklDVEs3RHlJYjl4UUJpVUFiTkVuVHNkWFFDRjU2YlJzQWR1WEtSSzRITTdCaFFmJTJCelU3JTJGdlhOQiUyRmJEbDZ4cGNLUnF3REJDcFBRMDNMJTJGTE1Oc2FHeW93NlAwdzZOdm8zJTJGYmFiUTFqQThVbVRaMDR6MHlwdDdKY1dxSzdsUW81V3V0UENIQVc0a2trJTNE; hide_promo_strip=1; invpc=10; page_view_count=7; lifetime_page_view_count=10; _ga_C4NDLGKVMK=GS1.1.1724828409.1.1.1724828794.55.0.0',
}
base_url = "https://www.investing.com"
filename = "./news/data/investing/list_us.json"

def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(
        "https://api.investing.com/api/news/homepage/21/5?is-ad-free-user=false&is-pro-user=false&max-pro-news-updated-hours=12",
        None,
        headers,
    )

    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["items"]

        for index in range(len(posts)):
            if index < 10:
                post = posts[index]
                link = base_url + post["href"]
                title = post["headline"]
                id = post["id"]
                if link in ",".join(links):
                    print("investing_us exists link: ", link)
                    break
                
                description = post["body"]
                pub_date = parse_time(post["updated_date"], "%Y-%m-%dT%H:%M:%SZ")
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 4:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("investing_us request error: ", response)


try:
    run()
except Exception as e:
    print("investing_us exec error: ", repr(e))
    logging.exception(e)
