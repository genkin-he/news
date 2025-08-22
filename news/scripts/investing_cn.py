# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Domain-Id": "cn",
    "Cookie": "gcc=HK; gsc=; udid=5a1588ed8de0fc102554e84796c508df; smd=5a1588ed8de0fc102554e84796c508df-1722482229; video_location_variant=2; __cf_bm=GR4QWeZh1ATVneP.OQHL.3oprCpY4Mq0SbVWUkrVDKo-1722482229-1.0.1.1-sBdI6JH_YI3xSjD0nVNmeeUOBhYj.UgacqmiF.aOxP_Igy3fyUid9LSWujRSkWMJkVYqCIY3E8BlnNznDAIcDVBKNkIM3vii7E2KMNEkpG8; invpc=1; adBlockerNewUserDomains=1722482230; lifetime_page_view_count=1; __eventn_id=5a1588ed8de0fc102554e84796c508df; _imntz_error=0; cf_clearance=MAhgxQA_hY9NHQKO6T0afik80xNthN1iSa0FVmXv1Ys-1722482230-1.0.1.1-s7m8EjOQ.J4ezxqRdtbq.CWo83F3tyyOpAHmwDbU6FBkAfti1tGe1jDH.v7kbjUju9U68CewVPeFmmzmx19bfg; _hjSessionUser_174945=eyJpZCI6ImE2YTZlODlmLTI1MzktNTUyZC05NjA3LTM2MTFiNjQzNmRmZSIsImNyZWF0ZWQiOjE3MjI0ODIyMzA4NzYsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_174945=eyJpZCI6ImVkZGY2Mzk4LTFkMWUtNGI3OC05MmE4LTMwZjBkNDk5OGRjZiIsImMiOjE3MjI0ODIyMzA4NzcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; r_p_s_n=1; reg_trk_ep=on%20mouse%20exit%20sign%20up; _ga=GA1.1.1037023375.1722482231; pm_score=clear; _ga_C4NDLGKVMK=GS1.1.1722482231.1.1.1722482234.57.0.0; _cc_id=3a5f8063497b3a384528b8568dc7973; panoramaId_expiry=1723087041549; panoramaId=9514424a2f825d3bb086c7733604185ca02c3fc752a8fa612b4b7510c447ce72; panoramaIdType=panoDevice; cto_bundle=vLCdSV9vSmJ1QVNZR0ZLV29DVVNLQ1I3OEdjTkRrWFJpVW51MGxqQ2NNSzhYMjY1ZXJxMzlXa2JOczAlMkZGNU94ZnQxUUdLMDA0eVk4SWE4Z092eHlSaEZJUXNjd00yMTRvcTVQTDhwYlZyVkMlMkJqeHoyakVzdTZhWTdLOG4wd1UzTUdiNlFKOHB2NEc1WWhWVTVsTDM1c2d1MzNNNzVodzU5M0pTSmdld0djN0ZrJTJCQUUlM0Q",
}
base_url = "https://cn.investing.com"
filename = "./news/data/investing/list_cn.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
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
                    util.info("exists link: {}".format(link))
                    break
                
                description = post["body"]
                pub_date = util.current_time_string()
                if post["updated_date"]:
                    pub_date = util.parse_time(post["updated_date"], "%Y-%m-%dT%H:%M:%SZ")
                if description != "":
                    description = f"<div>{description.replace('\n', '<br>')}</div>"
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "investing_cn",
                            "kind": 1,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 5:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
