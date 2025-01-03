# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts, log_action_error, parse_time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'cmp=t=1720432063&j=0&u=1YNN; axids=gam=y-bH4pTTBE2uLRALDRdWG79sGpMXLG0Uf8~A&dv360=eS1lTjh3Q0poRTJ1R18uWTV5X2Fob0JwZjhZanFXaVl1VH5B&ydsp=y-LxjP.ZxE2uJK082lsvIMBBGyGx3Mo9UD~A&tbla=y-y5og7XVE2uKgML8oyKKpVOhyYCqQga8m~A; tbla_id=d0ee6fa9-ca26-4709-b82b-4980c3d45b23-tuctd7e6efc; GUC=AQEBCAFmobJm00IXwgP0&s=AQAAADusuNHQ&g=ZqBqrQ; A1=d=AQABBHr9hWYCEAm577LVUXmFsKEHvJrhhBQFEgEBCAGyoWbTZivg7L8A_eMBAAcIev2FZprhhBQ&S=AQAAAskhET8gh63-eVO8uhMvM6I; A3=d=AQABBHr9hWYCEAm577LVUXmFsKEHvJrhhBQFEgEBCAGyoWbTZivg7L8A_eMBAAcIev2FZprhhBQ&S=AQAAAskhET8gh63-eVO8uhMvM6I; A1S=d=AQABBHr9hWYCEAm577LVUXmFsKEHvJrhhBQFEgEBCAGyoWbTZivg7L8A_eMBAAcIev2FZprhhBQ&S=AQAAAskhET8gh63-eVO8uhMvM6I',
}
base_url = "https://news.yahoo.com/"
filename = "./news/data/yahoo/list_us.json"

def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://news.yahoo.com/fp_ms/_rcv/remote?ctrl=StreamGrid&lang=en-US&m_id=react-wafer-stream&m_mode=json&region=US&rid=4c18971j77t3g&partner=none&site=news", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        html = json.loads(body)["html"]
        uuids = re.findall(r'data-uuid="([^"]+)"', html)
        uuids = list(set(uuids))
        print("yahoo us uuids:", uuids)
        # request中放入参数，请求头信息
        detail_request = urllib.request.Request(
            "https://news.yahoo.com/caas/content/article/?uuid={}&appid=news_web&device=desktop&lang=en-US&region=US&site=news&partner=none&bucket=news-dweb-nca-blog-test-2,seamless&features=enableEVPlayer,contentFeedbackEnabled,enableAdFeedbackV2,enableInArticleAd,enableOpinionLabel,enableSingleSlotting,enableVideoDocking,outStream,showCommentsIconWithDynamicCount,enableStickyAds,showCommentsIconInShareSec,enableInlineConsent,enableAdSlotsNewMap,enableGAMAds,enableGAMAdsOnLoad,enableFinancePremiumTicker,enableAdLiteUpSellFeedback,enableRRAtTop,enableCommentsCountInViewCommentsCta,enableRRAdsSlots,enableRRAdsSlotsWithJAC,newsModal,enableViewCommentsCTA&rid=2ndsttpj77ta5".format(','.join(uuids)), None, headers
        )
        # urlopen打开链接（发送请求获取响应）
        detail_response = urllib.request.urlopen(detail_request)
        if detail_response.status == 200:
            body = detail_response.read().decode("utf-8")
            posts = json.loads(body)["items"]
            for post in posts:
                link = post["data"]["partnerData"]["url"]
                title = post["data"]["partnerData"]["title"]
                id = post["data"]["partnerData"]["uuid"]
                summary = post["data"]["partnerData"]["summary"]
                author = post["data"]["partnerData"]["publisher"]
                pub_date = parse_time(post["data"]["partnerData"]["publishDate"], "%a, %d %b %Y %H:%M:%S %Z")
                if link in ",".join(links):
                    print("yahoo us exists link: ", link)
                    break
                description = post["markup"]
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "summary": summary,
                            "author": author,
                            "pub_date": pub_date,
                            "source": "yahoo_us",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                        
            if len(articles) > 0 and insert:
                if len(articles) > 5:
                    articles = articles[:10]
                with open(filename, "w") as f:
                    f.write(json.dumps({"data": articles}))
        else:
            print("yahoo us request error: ", response)
    else:
        print("yahoo us request error: ", response)


try:
    run()
except Exception as e:
    print("yahoo us exec error: ", repr(e))
    log_action_error(f"yahoo us exec error: {repr(e)}\n")
