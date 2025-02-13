# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": '_gcl_au=1.1.2081355469.1723167681; bz_landing_url=https://www.benzinga.com/; ajs_anonymous_id=56331343-dd8d-4d22-be6d-23f2f5e6f57c; _gid=GA1.2.320630503.1723167681; _omappvp=QiCAtZ3ghz1RdCueWCf6W0N3Ke3FlZNQhyp66XXQFlBlDhCLvqgzTcuXx20y3MCwZkL3S1oiOnve2lnpCAMWCAmNhKSAMtdf; _clck=14o2qjx%7C2%7Cfo6%7C0%7C1682; _hjSessionUser_15446=eyJpZCI6Ijg0YmNmOTBlLTI2YTEtNTIzOC04YzhiLWYxZTAxNTJlYzJhMiIsImNyZWF0ZWQiOjE3MjMxNjc2ODIxOTcsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_15446=eyJpZCI6IjIxYjRjNzc2LTIwNjgtNDlhZC1hN2RlLWRkZThiYjkyOWEwZCIsImMiOjE3MjMxNjc2ODIxOTgsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; bz_access_type=anonymous; benzinga_token=yi2q07sso9ftwduqbrk0qotbqpau0oxt; bz_access=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzMTY4NTgyLCJpYXQiOjE3MjMxNjc2ODIsImp0aSI6IjA2MzVlYjM5MjljNjQ0YjU5M2M4YzFiOGIwZjBiMmM2IiwidXNlcl9pZCI6Ik5vbmUiLCJpc3MiOiJodHRwczovL3d3dy5iZW56aW5nYS5jb20ifQ.miCGC4VdjJl7jKxn9QB0YknAeSN_14i2jf0_V8ud3PSbQMoWeaMsQdhpDbKM__3FXLcbGcRxbpjF5pN_zfcSOqBu-_7_LgkDUl3PXe4e61ziC1IcZoRoex4N7TM8MB91yDAI5v9ub1btcTQFOoeiWHxp8qV3l6alWLlAoqvvEmr3xd86mQ15BmK3BT5BPioKZablwQePwIUO1ToLGD9sXjvFzpzPciyZLtdSP7yC0wXwp44-5RVwJuKllhlJQoyHIUCZhcrE5jNEnygAMDKoe5FvWXz8Fp2uptCbfYCo-Gw_GFShlzUCOgk_tSFAGI08g4kFCGaH1e0IfcCRGA0-Tw; csrftoken=fk40QGAPHbSUsRiTLL06JhxERNAiDiX1; __cf_bm=NR67dHR3brBfSolKi6sLEW4zdqF8CStYxwuvfeNd9ro-1723167682-1.0.1.1-fIXkiARjWxfayXm2ZflI2HcffVlcqCYS6jIyPGZu6WMlc3gzicmG5dwlPNhcNRBhFhBxDE956XmXRoIMSjFvjQ; _cfuvid=gIa4nykjV7orS9o6SSdLgHvts_6ysswXrx1PwMUW0o0-1723167682232-0.0.1.1-604800000; _hjDonePolls=1053816; usprivacy=1---; _li_dcdm_c=.benzinga.com; _lc2_fpi=f4f35c7bd450--01j4rr73pyekfazmbdm5yt475q; _lc2_fpi_meta=%7B%22w%22%3A1723112591070%7D; _lr_retry_request=true; _lr_env_src_ats=false; omSeen-p6in73m20w3wkgrr3oez=1723167688436; om-p6in73m20w3wkgrr3oez=1723167693875; wordpress_logged_in=0; trc_cookie_storage=taboola%2520global%253Auser-id%3D7bdc49a0-b2aa-4064-935b-f42015a6b6e3-tuctdae220c; _omappvs=1723168016208; _ga=GA1.2.704396085.1723167681; _gat=1; _clsk=17gvcfw%7C1723168019489%7C7%7C1%7Ct.clarity.ms%2Fcollect; _ga_V7ZK73W7N0=GS1.1.1723167681.1.1.1723168019.0.0.0',
}
base_url = "https://www.benzinga.com/"
filename = "./news/data/benzinga/list.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.benzinga.com/api/news?limit=10", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["storyId"]
                title = post["title"]
                image = post["image"]
                link = post["url"]
                description = post["teaserText"]
                pub_date = util.parse_time(post["created"], "%Y-%m-%dT%H:%M:%SZ")
                if link in ",".join(links):
                    print("benzinga exists link: ", link)
                    break
                if description != "" and "Read the full article here" not in description:
                  insert = True
                  articles.insert(
                      0,
                      {
                          "id": id,
                          "title": title,
                          "description": description,
                          "image": image,
                          "link": link,
                          "pub_date": pub_date,
                          "source": "benzinga",
                          "kind": 1,
                          "language": "en"
                      },
                  )
        if len(articles) > 0 and insert:
            if len(articles) > 5:
                articles = articles[:5]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("benzinga request error: {}".format(response))

util.execute_with_timeout(run)
