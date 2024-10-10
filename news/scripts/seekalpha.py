# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
from util.util import history_posts, parse_time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=3758427501792; pxcts=2909d9d8-6f55-11ef-b90b-0b1c657b30ed; _pxvid=2909ce07-6f55-11ef-b90a-2880f277ed1a; _sasource=; _gcl_au=1.1.1804368556.1725959821; _ga=GA1.1.322761926.1725959822; _pcid=%7B%22browserId%22%3A%22m0w7wyyu27glfp5c%22%7D; __pat=-14400000; hubspotutk=946d47548c3fe751efb3b4011711298f; __hssrc=1; session_id=820b9a83-ebc9-4542-956f-c4b93f8080ea; __hstc=234155329.946d47548c3fe751efb3b4011711298f.1725959852030.1725959852030.1726710188406.2; _sapi_session_id=iM4%2FvovVzPQGpOYftyX%2F8SGUOxzjJqpha2K3fE18P0MHr4zq8Jf1Mq2sGZ2eBSss8%2FDNdLnDnHYgi8JsXGSasqPq5800WlORDdCTuxqOUq9ZP0Y7G4YNJdYxshJ0GRQN%2Bp7q%2BQmH8CeAyuiSO9v6v69I2YfNEFPOuomYXHuHXyHgmX3kHqKf%2F%2BnDdAr3NJkzK3j6cVzPzatUwAx0LEMtjB3JBaik%2B2kgekpD8RUSwZeRGlRw8JlmR9%2BmInMsIyy6r%2F47a71pNQXPf5clIT4QGcco8qGPdFMMN5PUJHbyelN2sncY99wtcvj8k%2FjQXJQQSPlEkvUQt82iPVvdlT0DWHmJpi5nLs4YX1dt3gPGCcy4Cvri7HhD5K3EHBqKWYC763u8Lc2EI1Ud1WmdEunt2xj2kJ7%2B4zDjLgJgZPToAZ4QZvLao%2BHkBnqIVqyhj864wsiIpvPyqiqLESTCiYXgM3BpN%2Fg%3D--Tj88D6k%2FSFbt4L9K--0oy%2FD15BHp5ybMZDbuh3MQ%3D%3D; _fbp=fb.1.1726711597602.18345378779054913; sailthru_hid=cd04a3350e81d2bd1ad549ac3030dce6665eab798920a91be60c7865e832e32deb6379925c9adcf901df80d3; _ig=60486164; _pctx=%7Bu%7DN4IgrgzgpgThIC5gF8A05owMoBcCGOkiIeAdgPakjoQCWOUAkgCaKlgA2HyQA; sailthru_visitor=7e66f66f-83a3-423c-8b11-1a80c75b6708; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fmarket-news%22%2C%22pageKey%22%3A%228cd80b00-c08f-4f5e-b197-b798babb88c0%22%7D; _ga_KGRFF2R2C5=GS1.1.1726710184.2.1.1726712513.60.0.0; sailthru_content=54d2fa8334bb76a61cce289937560910b10a229cf40fd395776d272d478e6441b6f09daf178879a54eed98528b6242aa; __pvi=eyJpZCI6InYtMjAyNC0wOS0xOS0wOS00My0xMi00MjAtbHEzWkcxdDJOMmtoZnRZSy1lNTg5MDdhOTAwMTBiNDRhNmM3YjNjMDA5Mjg2ZmQ0ZCIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTcyNjcxMjUxNDQ5MX0%3D; __tbc=%7Bkpex%7D90kOVrf3p0Fo1G7GLg9OIAG1Sn0vdZP4qwrb-rWzMtgwA75AfFmA_eSFgY7p3f_X; xbc=%7Bkpex%7DMzReatBvUWQFScovEdXd2PnSp69gvqSXT6vBBf3xZqr7W5KNXQiQMi3AGsp3Vv05EL_Kaj5KkgEohXzFRT1HgyYu1FuxrLctndtOOCWBeCjv6x0a54RioaXzG9XeMsToDu1z7CdUxYdTsdIV2kuA5Q8bmzHPJPJQ3qO6Luqqpkq3LABiUaX0lmGkyq_GpYJIVoKuJLlmbHfUDyrq0ZMkyYmMFlDnubCjyZQJ_zt-pzU; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%223758427501792%22%2C%22machineCookieSessionId%22%3A%223758427501792%261726710187969%22%2C%22sessionStart%22%3A1726710187969%2C%22sessionEnd%22%3A1726714510502%2C%22firstSessionPageKey%22%3A%228f499640-921e-41e2-9a39-2b74c85ee957%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1726712710502%7D%7D; _px3=ebc20cd9d1a41411d286a5b6cfc3659f85d96c6df0c05a5120a3081581ef5577:nfJgX6aaPd3onZ7xgLf/K5OgRZEs/SOZUq3TTTJjmDLffLbBrwA4BNYh7Ulrw2S1i+2D4U5Qf7eu2+c5Fv5NDw==:1000:0zBDhAIqABKoNwFWeEBlAnRo2Jx1IxScY6022KBA4bdLgTHF2Z4ltEhopSXeIaAAeljTeRipC20n5JnYdU9/TAnkQPlcXmpDZkBBt2Ekc67r4m0XXaLqEZJ1BLLurQTgNLA4fYAXvDcDeFqpJPnf3RVfTeheu7CF4WcC+j9htCGtA0hmhimiC1sLXQkqIGpVMOTYTg/SWj1jzUOZl2nJ8Hnbty0mIKBY/t8BbmMJBbg=; _pxde=8ac6b547b0bb0015416616e8fab43d88443cdec479455b02be6bc440f12fcf10:eyJ0aW1lc3RhbXAiOjE3MjY3MTM3ODg2NTIsImZfa2IiOjB9",
}
base_url = "https://seekingalpha.com/"
filename = "./news/data/seekalpha/list.json"


def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=5&page[number]=1",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 2:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = post["links"]["canonical"]
                pub_date = parse_time(
                    post["attributes"]["publishOn"], "%Y-%m-%dT%H:%M:%S-04:00"
                )
                if link in ",".join(links):
                    print("seekalpha exists link: ", link)
                    break
                soup = BeautifulSoup(post["attributes"]["content"], "lxml")
                ad_elements = soup.select("#more-links")
                # 移除这些元素
                for element in ad_elements:
                    element.decompose()
                description = str(soup)

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
                            "pub_date": pub_date,
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("seekalpha request error: ", response)


try:
    run()
except Exception as e:
    print("seekalpha exec error: ", e)
    logging.exception(e)
