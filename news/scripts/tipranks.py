# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'GCLB=CLSa-PLQp9ad7AEQAw; tr-experiments-version=1.14; tipranks-experiments=%7b%22Experiments%22%3a%5b%7b%22Name%22%3a%22general_A%22%2c%22Variant%22%3a%22v3%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_B%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%5d%7d; tipranks-experiments-slim=general_A%3av3%7cgeneral_B%3av2; rbzsessionid=7688e85a12286c68f7880fe65a080c48; _ga=GA1.1.772476228.1718697604; FPAU=1.2.396430585.1718697605; _fbp=fb.1.1718697604946.942849415717395583; _gcl_au=1.1.529088903.1718697606; prism_90278194=a2006884-f22e-45cf-8f9e-8180f77c3586; viewed_tickers={"tickers":[],"exp_time":"2024/6/21 10:41:06"}; FPGCLAW=GCL.1718851267.CjwKCAjwg8qzBhAoEiwAWagLrPtMh_ryduphx2hgC7Tc8lDET9cbfewqOm7n63jod56SqPY9Hb7sohoCTUsQAvD_BwE; _hjSessionUser_2550200=eyJpZCI6IjMxMWI2OWJiLTNkY2YtNWQ4Ny1iYTBmLTAxNmI4ZjdmODlmOCIsImNyZWF0ZWQiOjE3MTg2OTc2MDc0ODIsImV4aXN0aW5nIjp0cnVlfQ==; _gcl_gs=2.1.k1$i1718851290; _gcl_aw=GCL.1718851387.CjwKCAjwg8qzBhAoEiwAWagLrPtMh_ryduphx2hgC7Tc8lDET9cbfewqOm7n63jod56SqPY9Hb7sohoCTUsQAvD_BwE; rbzid=Yl+ttjGRrYuXcL+QG1wUgASb1ksyWyIqEu4H84aoSSOXppLTrBGtjlXVZ4twmTNUEO+sF43MZCbOCOn+L3EzXfa7hCYE7nXooxMpNYyZvyDHTeJkYznodxhEpYhI2zuANZ8irhtYQSGRmIV4SrWQ/C+jZ/evoswnMViJT/XpiNAPDla7IXFvQFT/jRvG6Fefjdggpq7rUXqvXM0C7andLOvMPy0D/A/ljLp8hgev8W+bYiVlmXihYnxEMQcdA9AwDv/KgyXvULKaANrTEG/xkaKsudYvrcoNhoqmKl20hD4=; _pbjs_userid_consent_data=3524755945110770; usprivacy=1YNY; TAPAD=%7B%22id%22%3A%22b3789e28-480c-4e35-979f-4ee0dfee371a%22%7D; .AspNet.ExternalCookie=3i-9BO_WmJbqHMKknvy2t4WZEO5RhJi_EmmMRpt8QdRbqh3N_XT1xvOCCoFSiHtA35gnvffEem6FB-wcudBJUlyclqGlirBxrCAr-YI6maSemkGnCTCvlYn1lCFZF20r1uIabCvkDcSgzLetY4m4vk_iaO0x6f7GXYvwcwzIAL0OMqZi-A8BohN7jfunJIUIYxkXt3Kgvm22F3sNAyuCQedLmS8-mpo9PIo3_dhaC286oDiG0w7o--WavqRZkQDBBUP3Is7cWAIS5IJ_j3xPrpMo--zs1riyDRsoj-EKXPEH87KP8fxx76G-TfEtZ98w7tVcBz4HiuNU6W8lrO1WhD7Xd-Xc-_D6kAU-aYu4BnR6--FyJZLOehYPCBGMVWcNTtkOQZtXauTL8-hr5zoOsP7TulGpfYLyd1WoDRelfzo-i93gm5nZ2BRkSKnwFH4rmpsLAPe-GDhAh4r9uScu5ZUQfcL5Mo7ivmZkG5NyPxjW5RNjOSZESh1zZjji5Hfz4pwihAEAazqF0qyKygoMH_mj94ORuCCh-A11BNsUV_5lN5ue0m9Yx676eqTJk979_eIOcjHJfLdllQg_Lgbq9OOJJVbRyuzh8v14klRxltAIDJahgm7-fa3iXQSR4iOS; token=ee68577935bd50a35562eec796da312cf48982b1; user=hemengzhi88@gmail.com,genkin he,; loginType=login; tr-plan-id=1; tr-plan-name=basic; tr-uid=D18BE707AC42BD348FA8A97603030ACB; TiPMix=92.82006784576825; x-ms-routing-name=self; distinct_days=["2024-06-18","2024-06-20","2024-06-21"]; trc_cookie_storage=taboola%2520global%253Auser-id%3Deac43e25-f72c-435b-9b78-b126a1d979a0-tuctd652e14; ic_tagmanager=AY; _hjSession_2550200=eyJpZCI6IjMzZDc1N2U5LWE1YzgtNDI2NS05YzRlLTVjNzM4MzBkNDIwMSIsImMiOjE3MTg5MzYzNTU5NDMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; __gads=ID=8e37c8099a513b47:T=1718878722:RT=1718936356:S=ALNI_MbLe-1EWMLc-6yDG24hfQBbTkCRng; __gpi=UID=00000e5714c7292e:T=1718878722:RT=1718936356:S=ALNI_MbwmNhRIVdXDaAk32SRXjzy1LP1VA; __eoi=ID=cf7b3e738018b138:T=1718878722:RT=1718936356:S=AA-AfjYXcVOQSedZfJP-1SKBG77Z; IC_ViewCounter_www.tipranks.com=2; cto_bundle=44aFg19UenY3TUgyTHV4M2ZnVkdHdkRGR21kSmFsJTJGRGNJNU9WQ1I1YUJMSXV2RGNoR2ZFQVBkV1FMcU5sbXR0UHlMeVU5UGhybyUyQnYzd0FyQmpYMU1XamQ4cklPcCUyRk1paUJDdHFVR2lBYXpyUlEyU2NZaTNMQ3lvTnVzJTJCS0lyUERGckxaYkNQZERnMFNaRkhaeHVYaEFEUGtDUSUzRCUzRA; _ga_FFX3CZN1WY=GS1.1.1718936347.5.1.1718936445.0.0.200861170',
}
base_url = "https://tipranks.com"
filename = "./news/data/tipranks/list.json"


def get_detail(link):
    print("tipranks: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = response.read().decode("utf-8")
    items = body.split("document.querySelectorAll")
    if len(items) > 1:
        body = items[1]
    else:
        return ""
    result = re.findall(".*window.__STATE__=JSON.parse\\((.*)\\);*", body)
    if len(result) > 0:
        resp = json.loads(result[0])
        result = re.findall('.*content":(.*),"date:*', resp)
        if len(result) > 0:
            result = eval(result[0])
            result = re.sub(r"(\n)\1+", "\n", result)
            return result


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://tr-cdn.tipranks.com/bff/prod/header/payload.json", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["posts"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["_id"]
                title = post["title"]
                image = ""
                if post["image"]:
                    image = post["image"]["src"]
                link = base_url + post["link"]
                author = post["author"]["name"]
                pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if link in ",".join(links):
                    print("tipranks exists link: ", link)
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
                          "image": image,
                          "link": link,
                          "author": author,
                          "pub_date": pub_date,
                          "source": "tipranks",
                          "kind": 1,
                          "language": "en",
                      },
                  )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("tipranks request error: {}".format(response))


util.execute_with_timeout(run)

