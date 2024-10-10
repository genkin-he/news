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
    "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=9523385106045; session_id=5aa3cf9f-9c24-4360-99cc-4584982a32ac; _gcl_au=1.1.885550938.1724378052; _ga=GA1.1.1777829336.1724378052; _pcid=%7B%22browserId%22%3A%22m06265dffox32b8x%22%7D; pxcts=99085b44-60f2-11ef-817b-c0c311790247; _pxvid=99085066-60f2-11ef-817b-be403a778a18; __pat=-14400000; __hstc=234155329.e4c6408d8b4dc8d6386145d567137ad3.1724378054535.1724378054535.1724378054535.1; hubspotutk=e4c6408d8b4dc8d6386145d567137ad3; __hssrc=1; sailthru_hid=39b04d7c8e25d63b5e45e1150895dd0066b463a8da7c1f8f4b0510de06f5a2bed999b02abf867b7ee4da86f9; user_id=60486164; user_nick=; user_devices=; user_cookie_key=1xpjjsx; u_voc=; sapu=101; user_remember_token=5b0c521806f67a31a6a3485c98ab60511b040bfa; gk_user_access=1**1724381546; gk_user_access_sign=c9a97e7a159ad97555a32a32cff567f1d8ded17c; _sapi_session_id=6Jpx7%2FmS1062Nzn%2BstX4uS6yvWOVharUc4twNZRgyE%2BpvLEr8WbofogmINUS6jjhuiLQ56%2BcoWMsb%2B1lVZ%2BxIYEgUBd7FukNNEhO6QvpZXuBJZDQaptUGp8ZW0gxvpGlrHh8ha1suYubaxGTlmDLpvlGOI%2Btr7Rvsn3mAl6GVq%2FqZnZ4q1MthtsdY1wfAV9Fn9RuEoZXPEGlw0m0j0dWSwwtGDlb1WtyCPFsf9L%2FFZDJzF9DM4J8pMujquIjJU6OmRBVxKFUe3d8PGh3sH8vOJri7236cUxUh7CR9jhCjJxjsZ2%2FHliYXIoplGyZv7QIqEG1UB1lllHWSUWjg%2BwtQKmf1W5IdkC2LdWm1Yyd9D0miPJHFKHOlETY%2FkVAQD65VbSXoAhFkCE%3D--XVzikb4yW9NxEdMJ--IZqp60VEuJHUdqtDxJRdfQ%3D%3D; _sasource=; _pctx=%7Bu%7DN4IgrgzgpgThIC5QDYAMAWAHMgjM9ioADjFAGYCWAHoiCADQgAuAnkVLQGoAaIAvn0aRYAZSYBDJpFqkA5hQhNYUACYMQECkoCSahADswAGyN8gA; _ig=60486164; __pvi=eyJpZCI6InYtMjAyNC0wOC0yMy0wOS01NC0xMy0zMDItR2EzRzV3MXN0QUdVV096Zy1jZmQ2N2JlYTRjYjZlNjE2NjlhYjc5MDcxNDkzMTFjNSIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTcyNDM4MTU2NjU3M30%3D; sailthru_pageviews=19; __tbc=%7Bkpex%7DFLU1LfNjCEqpsZTZ9EOyyLJLb9t3RwwWA-LchwSvrdzWrnT8_3kyf_rpvNSotnem; xbc=%7Bkpex%7DfYtxRyyHW5bVR8F-6Xev1PnSp69gvqSXT6vBBf3xZqr7W5KNXQiQMi3AGsp3Vv05EL_Kaj5KkgEohXzFRT1HgyYu1FuxrLctndtOOCWBeCjv6x0a54RioaXzG9XeMsToDu1z7CdUxYdTsdIV2kuA5Q8bmzHPJPJQ3qO6Luqqpkq3LABiUaX0lmGkyq_GpYJIBHCtEdv7QXTVgV-IdTPMs8FLQsoj9cCxKhsa4QSlbssHkiPlKAHN6apBexP9CKRw; sailthru_content=9e9e3b505d20c25082b306eaffa45ce5b6f09daf178879a54eed98528b6242aa38b84a410e2c73308382a6749c3030e63c5f57e561d9315a8a9a86be8720511ebec6acc30b8a969fadab1639b0df81fd4618d6229feb9cca4ab47dd847b971d6f0251524d6c5bdfecb6f06af6381eace3164005bb36f95ea87a5c194e633ace6; sailthru_visitor=f64b5360-2ac0-4011-9658-1f4956adc33e; _ga_KGRFF2R2C5=GS1.1.1724378051.1.1.1724381568.29.0.0; __hssc=234155329.19.1724378054535; LAST_VISITED_PAGE=%7B%22pageKey%22%3A%2262c43d45-96c1-4795-980c-d7f252cd1c0e%22%2C%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Farticle%2F4716617-titan-international-stock-near-recession-low-valuation-the-bottom-fishing-club%22%7D; _px3=422e60fb9ff86a9e8519a3ffc77f637e3800c75ce98ae966b59b181df5ec3af0:RjmDOVdDN78OUYxUkMGTEKAoIevFXtHZ7NELGtFPs96st9mMwbFjZ17CwoXqsCJJLn4G1oHCsOZH7O3GaoOHgw==:1000:R7h2vRPqFwd/l8Zo/PWH0Zdg9bUM1BCs9HQAcAz9ArOfJei5Ge5Jt9wHNAXSwq/bjTgp9R52Lfq1YaQv8MyAyHr2q91sbEYQDcLCB7szHIGfEfD3jjUdLgSFk+xzVk2wQefNzjIHONi8ousxb+EK39lj9UaaUXW1O+EGJ5MWXYvGlQw7Otm60sMDF0Qx3AnyXlfDb9R9dXlPrqK5uTBHELuP3wTX8Wh4bvgl687X61k=; _pxde=9f51d3e11421c19601d6f5f0be92e6e1cdb0f83d3123c8fb2d3d37339e78d767:eyJ0aW1lc3RhbXAiOjE3MjQzODIwMTgyNzMsImZfa2IiOjB9; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%229523385106045%22%2C%22machineCookieSessionId%22%3A%229523385106045%261724378049325%22%2C%22sessionStart%22%3A1724378049325%2C%22sessionEnd%22%3A1724383820534%2C%22firstSessionPageKey%22%3A%22b2c3ffc1-e0f5-4bf8-b2d7-d2ab1d4c50f1%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1724382020534%7D%7D",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"

def get_detail(link):
    print("seekalpha_articles link: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, 'lxml')
        scripts = soup.select("script")
        for script in scripts:
            if "window.SSR_DATA = " in script.text:
                return json.loads(script.text.replace("window.SSR_DATA = ","")[:-1])["article"]["response"]["data"]["attributes"]["content"]
        return ""
    else:
        print("seekalpha_articles request: {} error: ".format(link), response)
        return ""
    
def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=5&page[number]=1", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = base_url + post["links"]["self"]
                pub_date = parse_time(post["attributes"]["publishOn"], "%Y-%m-%dT%H:%M:%S-04:00")
                if link in ",".join(links):
                    print("seekalpha_articles exists link: ", link)
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
                          "pub_date": pub_date,
                      },
                  )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("seekalpha_articles request error: ", response)


try:
    run()
except Exception as e:
    print("seekalpha_articles exec error: ", e)
    logging.exception(e)
