# -*- coding: UTF-8 -*-
from curl_cffi import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

base_url = "https://www.reporterosdelsur.com/"
filename = "./news/data/reporterosdelsur/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info(f"link: {link}")
    response = requests.get(link, impersonate="chrome136", timeout=10)
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
        raise Exception(f"request: {link} error: {response.status_code}")


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    # 使用 requests 发送请求
    response = requests.get(
        "https://lisboatv.pt",
        impersonate="chrome136",
        timeout=10,
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
                    util.info(f"exists link: {link}")
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
        raise Exception(f"request error: {response.status_code}")


if __name__ == "__main__":
    util.execute_with_timeout(run)
