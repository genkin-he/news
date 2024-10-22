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
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=4110210316990; session_id=20807958-4caa-4df0-a5cc-8f10e23ed662; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2F%22%2C%22pageKey%22%3A%224db06f74-8f75-4372-911a-f07e5d100db6%22%7D; _sasource=; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%224110210316990%22%2C%22machineCookieSessionId%22%3A%224110210316990%261729564070448%22%2C%22sessionStart%22%3A1729564070448%2C%22sessionEnd%22%3A1729565870455%2C%22firstSessionPageKey%22%3A%224db06f74-8f75-4372-911a-f07e5d100db6%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1729564070455%7D%7D; _gcl_au=1.1.155019668.1729564072; sailthru_pageviews=1; _ga_KGRFF2R2C5=GS1.1.1729564072.1.0.1729564072.60.0.0; _ga=GA1.1.174284074.1729564072; _fbp=fb.1.1729564072576.162626509936558317; _uetsid=3d2e7d50901d11efa493474d2b89aa1d; _uetvid=3d2ea7f0901d11ef97a0fde4bc5e6f6f; sailthru_content=3c5f57e561d9315a8a9a86be8720511e; sailthru_visitor=369b72f7-54a5-48d6-9939-9846a5487e23; __hstc=234155329.bb58cd9178d3db5b68a91cb337cd2559.1729564074319.1729564074319.1729564074319.1; hubspotutk=bb58cd9178d3db5b68a91cb337cd2559; __hssrc=1; __hssc=234155329.1.1729564074320; _clck=1v4y8zk%7C2%7Cfq8%7C0%7C1756; pxcts=3f19b19a-901d-11ef-9e40-81ba85b2fe73; _pxvid=3f19a267-901d-11ef-9e3f-635d2f484ad9; _clsk=91l90%7C1729564076364%7C1%7C0%7Cf.clarity.ms%2Fcollect; _px3=80096e5b9eccf99c73e742fbb50780ed4afb7ed2be552586a67e7f02f52058a3:n9rAn48+UsUM7IehMDSkCqVEeT0Rq5GpynUG1FLuAqUB0lXGvWlMcLZPLwHC89SIH/AhG2IuE4+rH+1gLLr3wg==:1000:YPXMyhcJ0Hpy8ARuMm38TRTcFnzQ748eZUgUUf84zhQEvtfXgKxeb5avtAedGBsn347+OyGpggrNGA43HTqVwvFPGJU9LCwiQtuJEvFLQuxgdYFmIH4+u7XPnDchc1pNkkPx/zLwGaBfyiqQMQbpRV2MExMd6MRNHraHmdc74qqUcrwTLc5Hfy/bWkt2JgvLQl3I3ijJzOwurKX0TB+2j35f1z3rbKB9KcVljUfwuNQ=; _pxde=77f5d30e60add0ec344e0f3cae22dfb7c716e062c34cd5a76b6114cef6412ab0:eyJ0aW1lc3RhbXAiOjE3Mjk1NjQwNzc1NDksImZfa2IiOjB9",
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
