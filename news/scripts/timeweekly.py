# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "Hm_lvt_0a94cb853fbc2b3f85ce27b0672ab48a=1739772321; HMACCOUNT=93EA506E2F8692F2; XSRF-TOKEN=eyJpdiI6IjhqOTc0eStka05IZUswazdrMVl4QUE9PSIsInZhbHVlIjoiaTg1UkFEcFplT0p2NExNYlU5XC9objM2dU5ZbWx2XC9cL1hmaEE1U1wvTFlETkdEZjRBTjlQZytHSmlPNEpEYkNkM20iLCJtYWMiOiIwM2E3NzIzN2I4MzgyMzM1MmE0ZWViNjkzMGNmN2JlMzcxOWFiYWQ0ODdhNWI4ZTc3ZGJiODU1NjE3MTgxYjY5In0%3D; timeonline_session=eyJpdiI6InEyZjZjM3h0WnA0dU53aStwWFVcL21nPT0iLCJ2YWx1ZSI6IkNQM2JQWXViOW1VeVFCS05xQzdoMVgxMWlqN2VHQVdvRU1tanFaXC9UVU9jNU5WMjREcGM5NmJOMEMyVk9BZExtIiwibWFjIjoiYzkxYzUyMWExNTBmMDM5YTIxZDllZDBmMTFhNjBjOWRjYzI5MTA4ZmZiNmMyMmI5M2I2NTYxMTgwZmI5MGVhOCJ9; Hm_lpvt_0a94cb853fbc2b3f85ce27b0672ab48a=1739774425",
}
base_url = "https://www.time-weekly.com/"
filename = "./news/data/timeweekly/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one(".main_article")

        ad_elements = soup.select("script,style")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    # 使用 requests 发送请求
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        body = response.text
        lxml = BeautifulSoup(body, "lxml")
        posts = lxml.select(".t4_block")
        for index, post in enumerate(posts):
            if index > 2:
                break
            title = post.select_one(".t4_block_text").text.strip()
            link = post["href"].strip()
            # 判断图片是否存在
            image = post.select_one(".t4_block_pic")
            if image:
                image = (
                    image["style"].strip().split("url(")[1].split(")")[0].strip()
                )
            else:
                image = ""
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description:
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "image": image,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "timeweekly",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

# 访问限制
# util.execute_with_timeout(run)
