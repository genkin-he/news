# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_lscache_vary=7e15a74c1fa7fd685f7458c5922efa5e; _ga_60NDG0QP7D=GS1.1.1738565659.1.0.1738565659.0.0.0; _ga=GA1.1.1397454213.1738565660; pll_language=en",
}
base_url = "https://www.reporterosdelsur.com/"
filename = "./news/data/reporterosdelsur/list.json"
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one(".entry-content")

        ad_elements = soup.select("div[itemprop='video']")
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
    response = requests.get(
        "https://lisboatv.pt",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.text
        lxml = BeautifulSoup(body, "lxml")
        posts = lxml.select("article")
        for index, post in enumerate(posts):
            if index < 3:
                title = post.select_one("h2 > a").text.strip()
                link = post.select_one("h2 > a")["href"].strip()
                # 判断图片是否存在
                image = post.select_one("figure img")
                if image:
                    image = image["src"].strip()
                else:
                    image = ""
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                if util.contains_language(title):
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
                            "source": "reporterosdelsur",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
