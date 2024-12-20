# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
from util.util import current_time, history_posts, parse_time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=5625987321047; session_id=97e8f5d3-ebf9-41e7-9fa8-baa63e07e2a9; _sasource=; _gcl_au=1.1.1119644522.1733108115; _ga=GA1.1.984473142.1733108116; sailthru_pageviews=1; _uetsid=dbabc860b05811ef9eec67fd3d26cad7; _uetvid=dbac0400b05811efa7e12901d0c94483; sailthru_visitor=46dd1324-7b54-472d-bd75-22358f6f9689; pxcts=dc510cb4-b058-11ef-8b78-a7fba37b9544; _pxvid=dc50fd3f-b058-11ef-8b77-cb4199e49f14; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%225625987321047%22%2C%22machineCookieSessionId%22%3A%225625987321047%261733108113719%22%2C%22sessionStart%22%3A1733108113719%2C%22sessionEnd%22%3A1733109924587%2C%22firstSessionPageKey%22%3A%22c7e1fe77-b24b-4f6f-bc1c-aaa7f3463c9a%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1733108124587%7D%7D; _ga_KGRFF2R2C5=GS1.1.1733108115.1.1.1733108127.48.0.0; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Farticle%2F4741334-japanese-yen-warning-global-markets%22%2C%22pageKey%22%3A%227f7e844c-f0bb-4daf-83fc-c15bdc3d98bb%22%7D; sailthru_content=3c5f57e561d9315a8a9a86be8720511e6fd622d2a0fc6f618f747346eef2388b; _px3=959961dd87c30d708f24562dd2483d1857db4b6acfa1b195e040304997f006d9:2KEwsbN31CHlP/liRsiZLjLgMztOozJiZjBqjUzw76WKbBvfRedZyNw42soYI4qnKuwTZvEe4WsQ8n87qwQ3Fw==:1000:U801DJZsB5s4HPqapCjB3w/Su/CV8g5zjJ0X+l/KlY0FXutvv4Oq5M2FIL7IEi355brNBMtQJ4t4Y02Yl8XwV5PbsqMpZnU42GMKi803TaGHRs/YJarOIUTZJFuIBTJvlDnaKovFgO/X10zOM4zCqvbCeFlfWNQJMTzcDVYtrCM3UlbtD5ebxSeqKo15gJWJzF8DolZ2Up8WxqWLzS4ghaVUF15q9wMhZ68T1nibzuo=; _pxde=aca154332a96733e8056010fb363beb67a5f5400e32b0305f9198ff95ee8d6e8:eyJ0aW1lc3RhbXAiOjE3MzMxMDgxMjczNDgsImZfa2IiOjB9",
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
                publish_on = post["attributes"]["publishOn"]
                pub_date = current_time().strftime("%Y-%m-%d %H:%M:%S")
                if "-05:00" in publish_on:
                    pub_date = parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-05:00")
                elif "-04:00" in publish_on:
                    pub_date = parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-04:00")

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
                            "source": "seekalpha",
                            "kind": 1,
                            "language": "en",
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
