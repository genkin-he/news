# -*- coding: UTF-8 -*-
import urllib.request  # 发送请求
import json
import gzip
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Cookie": "locale=zh-cn; ftreport-jssdk%40new_user=1; cipher_device_id=1719542555987312; device_id=1719542555987312; sajssdk_2015_cross_new_user=1; _gid=GA1.2.1416473133.1719542557; csrfToken=FetFFxU4cEL-78nhthfe7kPp; Hm_lvt_f3ecfeb354419b501942b6f9caf8d0db=1719542619; futunn_lang=zh-CN; _gcl_au=1.1.396785396.1719542628; _clck=tc8hlo%7C2%7Cfn0%7C0%7C1640; passport_dp_data=qupBq0IPIju1t3zGCce%2B%2FDmoYrVGUtlZty21t%2BHja4QG0FO0quygWbxRUv9IXk5HXmw4rpNzQphzyQHGsqlsIZc9PORc6o5BenWhc5cVL1w%3D; _uetsid=3ebc417034f811ef8264ad852bb58e4b; _uetvid=3ebc812034f811efbbd50d6414e51512; _ga_NTZDYESDX1=GS1.2.1719542627.1.1.1719542742.60.0.0; _clsk=j5lky8%7C1719542745121%7C3%7C1%7Ca.clarity.ms%2Fcollect; uid=11310442; web_sig=h659gBchTuqxqloreJPtlEflvWsn2WlrhBqAHhHp6%2FYFd9W%2BW8D0wtOdqYrp0MdTqm8GBWZLNviMLMyi%2BzChDyQHs8RPeueAKgooNqh95QCnAqxPswfKuMbTt2wHav58XNDSOaGb0ow0yqXOI1JUAg%3D%3D; _ga_FZ1PVH4G8R=GS1.1.1719542627.1.1.1719542790.0.0.0; _ga_K1RSSMGBHL=GS1.1.1719542627.1.1.1719542790.0.0.0; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22ftv1ucQDRkID1nkrznSbhA9E3ck3EPukSv1392pAxdjk3MZwuvVMAI7u81AaDrljlOTt%22%2C%22first_id%22%3A%221905cb923701848-0c43b46dd83f7d8-19525637-2073600-1905cb923712172%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfbG9naW5faWQiOiJmdHYxdWNRRFJrSUQxbmtyem5TYmhBOUUzY2szRVB1a1N2MTM5MnBBeGRqazNNWnd1dlZNQUk3dTgxQWFEcmxqbE9UdCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxOTA1Y2I5MjM3MDE4NDgtMGM0M2I0NmRkODNmN2Q4LTE5NTI1NjM3LTIwNzM2MDAtMTkwNWNiOTIzNzEyMTcyIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22ftv1ucQDRkID1nkrznSbhA9E3ck3EPukSv1392pAxdjk3MZwuvVMAI7u81AaDrljlOTt%22%7D%2C%22%24device_id%22%3A%221905cb923701848-0c43b46dd83f7d8-19525637-2073600-1905cb923712172%22%7D; locale.sig=ObiqV0BmZw7fEycdGJRoK-Q0Yeuop294gBeiHL1LqgQ; Hm_lpvt_f3ecfeb354419b501942b6f9caf8d0db=1719572202; PHPSESSID=9f5ddjmsc5bsi5mkfrv02jius4; _gat_UA-71722593-3=1; ftreport-jssdk%40session={%22distinctId%22:%22ftv1ucQDRkID1nkrznSbhA9E3e1is8u55xPzmV7m6IFfmtBwuvVMAI7u81AaDrljlOTt%22%2C%22firstId%22:%22ftv1L1mJBS2iZZOA8k/Lz2+ye5olMHB+s9ZNF8XstShG16qYgtWJcTIkJHSHfvr0f+K8%22%2C%22latestReferrer%22:%22https://www.futunn.com/stock/TSLA-US/news/news%22}; _ga=GA1.1.234964489.1719542557; _ga_370Q8HQYD7=GS1.2.1719572203.5.0.1719572203.60.0.0; _ga_EJJJZFNPTW=GS1.1.1719572203.4.1.1719572208.0.0.0; _ga_XECT8CPR37=GS1.1.1719572203.4.0.1719572208.55.0.0",
}

def get_detail(link):
    print(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = gzip.decompress(response.read()).decode("utf-8")
    data = json.loads(body)["data"]
    print(data)
    return data


def get_stock_id(link):
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = response.read().decode("utf-8")
    elements = body.split("stock_id=")
    body = elements[len(elements) - 1]
    stock_id = body.split("&")[0]
    print("url: ", link, "stock_id: ", stock_id)
    return stock_id


sources = []
stock = "08427-HK"
market = 1
if stock.split("-")[1] == "US":
    market = 2
seq_mark = "1_1693488981"
stock_id = get_stock_id("https://www.futunn.com/stock/{}/news/news".format(stock))
for index in range(15):
    time.sleep(0.5)
    list_url = "https://www.futunn.com/quote-api/quote-v2/get-news-list?stock_id={}&market_type={}&type=0&subType=0&seq_mark={}".format(
        stock_id, market, seq_mark
    )
    data = get_detail(list_url)
    seq_mark = data["seq_mark"]
    list = data["list"]
    for post in list:
        sources.append(post["source"])

print(set(sources))
