# -*- coding: UTF-8 -*-
import traceback
import urllib.request  # 发送请求
import json
import re
import logging
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'GCLB=CIHp763R_8i_eBAD; tr-plan-id=0; tr-plan-name=free; tr-experiments-version=1.14; tipranks-experiments=%7b%22Experiments%22%3a%5b%7b%22Name%22%3a%22general_A%22%2c%22Variant%22%3a%22v1%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_B%22%2c%22Variant%22%3a%22v1%22%2c%22SendAnalytics%22%3afalse%7d%5d%7d; tipranks-experiments-slim=general_A%3av1%7cgeneral_B%3av1; rbzsessionid=a2b5b37d7d72fadca9b56bfbce246c9c; distinct_days=["2024-07-04"]; _fbp=fb.1.1720057207428.111030367195245647; _ga=GA1.1.1861535169.1720057208; FPAU=1.2.74915611.1720057208; _gcl_au=1.1.2070938247.1720057209; ic_tagmanager=AY; usprivacy=1---; _pbjs_userid_consent_data=3524755945110770; prism_90278194=45864d57-5add-459b-b69a-5db7843c27b2; _ce.clock_data=-56%2C46.232.121.104%2C1%2C10f9287deaf609ee36fb37783f2b89c0%2CChrome%2CHK; trc_cookie_storage=taboola%2520global%253Auser-id%3Dd0ee6fa9-ca26-4709-b82b-4980c3d45b23-tuctd7e6efc; _lr_env_src_ats=false; pbjs-unifiedid=%7B%22TDID%22%3A%227edd8cd1-b122-4c84-8336-0a324b793325%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222024-06-04T01%3A40%3A13%22%7D; pbjs-unifiedid_last=Thu%2C%2004%20Jul%202024%2001%3A40%3A13%20GMT; panoramaId_expiry=1720143613341; _cc_id=bdf09b17b4d99187de2388c46613ad29; _hjSessionUser_2550200=eyJpZCI6ImQ5OGJjMzBlLTZiODQtNTY5NC1hNmRiLWI3ZGU2OGVlZTViNyIsImNyZWF0ZWQiOjE3MjAwNTcyMDg5MTEsImV4aXN0aW5nIjp0cnVlfQ==; noTopRibbon=true; DontShowPopupCampaign=true; rbzid=NpwfKkk/BgTbZlzbw5gefEfDSwwt6gCplm81kdq2uyrkzHjlgs0Q/C79lxiq5huGy7eyfpMpwhOj8baUgN8wCy20lDwD1cZdstqisXbad6KM7c9S3ID+tX4XwkNr9xLoRQpluFrKDrsc6GR1MjdUAGrZL1Xpw4ZULATlzOSBNCvSwxeCOMpH1qusOxh86Pn1mwd2dWgDzl+iN2iRfg690W7qcqA6JDcqe4YdZ4ELCpZZ8oVL149wr3QsRE8zsRN1INtlDK9NgvA4SHVwBQS1Neem1l6PccCDgplH60lWq6Q=; viewed_tickers={"tickers":["doyu"],"exp_time":"2024/7/5 09:40:07"}; plsVisitorGeo=HK; plsVisitorCity=; instiPubProvided=0c87d332-2935-49ea-997f-1e01a12db386; _pubcid=583ff421-7c4b-4095-9719-d652a8a43f90; _pubcid_cst=zix7LPQsHA%3D%3D; plsVisitorIp=46.232.121.104; plsGeoObj={"ip":"46.232.121.104","country":"HK","region":"HWC","city":"","zip":"","location":"22.2848,114.1703"}; _au_1d=AU1D-0100-001720059490-0XX2TG2B-7IGM; _ga=GA1.1.1861535169.1720057208; _gid=GA1.1.1190609948.1720059494; IC_ViewCounter_www.tipranks.com=1; _hjSession_2550200=eyJpZCI6Ijk3MDBmZmU5LTJmMWEtNGEyMi1hZmQzLTEyZjQzYmU0YzY5MSIsImMiOjE3MjAwNzU3NzA0MjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; __gads=ID=ce6619743c1ed099:T=1720057212:RT=1720075772:S=ALNI_Ma8Yh6Qn8eduCgyREi_kr9Tt0v2Jg; __gpi=UID=00000e71e5646af9:T=1720057212:RT=1720075772:S=ALNI_MbyAzcKE0Shn5DQshVr2G6jCuxbng; __eoi=ID=e05c526a502d64b2:T=1720057212:RT=1720075772:S=AA-AfjaqXmVLahJmEdAlQfIz5Ua8; cto_bundle=mLDe3V9nd0MlMkY3U3A1Rk8wSk1IJTJCaDBTUkxCaWtnUEpnWXZnbGZwZWE2OVpralFRSldNaTNLUG1IaU9FNnc0bEVIZVhRV0Q2U3g2VUolMkJnNW9taVVJczNBaDJHalg4UXV6cFhLUEtYcWclMkZMJTJCMmtRcHZZbW9SbHNscnVBWjlqaVFBaHVabjVFJTJCZWIwdEI0ZlhKZ0tkOG5iem5UaVElM0QlM0Q; _ga_FFX3CZN1WY=GS1.1.1720074431.3.1.1720075775.0.0.2111778184',
}
base_url = "https://tipranks.com"
filename = "./news/data/tipranks/others.json"


def get_detail(link):
    print("tipranks others: ", link)
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

def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        url,
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["_id"]
                title = post["title"]
                image = ""
                if post["image"]:
                    image = post["image"]["src"]
                link = post["link"]
                author = post["author"]["name"]
                pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if link in ",".join(links):
                    print("tipranks others exists link: ", link)
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
                            "source": "tipranks_others",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("tipranks others request error: {}".format(response))

util.execute_with_timeout(run, "https://www.tipranks.com/api/news/posts?per_page=5&category=article")
    
util.execute_with_timeout(run, "https://www.tipranks.com/api/news/posts?per_page=5&category=global-markets")

util.execute_with_timeout(run, "https://www.tipranks.com/api/news/posts?per_page=5&topic=dividend-stocks")

