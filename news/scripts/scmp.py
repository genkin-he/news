# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "apikey": "MyYvyg8M9RTaevVlcIRhN5yRIqqVssNY",
    "content-type": "application/json",
    "if-none-match": 'W/"2efcd-zd00UtKcKIzmnIpYQEl9eL4ahy4"',
    "origin": "https://www.scmp.com",
    "priority": "u=1, i",
    "referer": "https://www.scmp.com/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

base_url = "https://www.scmp.com"
filename = "./news/data/scmp/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("news: " + link)
    try:
        request = urllib.request.Request(link, None, headers)
        response = urllib.request.urlopen(request)
        if response.status == 200:
            body = response.read().decode("utf-8")
            if 'articleBody' in body:
                result = body.split('"articleBody":"')[1].split('"')[0]
                return result
            else:
                return ""
        else:
            util.error(f"request error: {response.status}")
            return ""
    except Exception as e:
        util.error(f"Error fetching article content: {str(e)}")
        return ""


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    urls = data["links"]
    insert = False

    api_url = "https://apigw.scmp.com/content-delivery/v2?extensions=%7B%22persistedQuery%22:%7B%22sha256Hash%22:%22a1bfbe3d505deb22ac31b088ab65c619817a7b86eb1d315c950d9cf8cf5df91b%22,%22version%22:1%7D%7D&operationName=livePageLatestPaginationQuery&variables=%7B%22after%22:%22%22,%22applicationIds%22:%5Bnull,%222695b2c9-96ef-4fe4-96f8-ba20d0a020b3%22%5D,%22count%22:30,%22excludeArticleTypeIds%22:%5B%5D,%22excludeSectionIds%22:%5B%5D,%22scmpPlusPaywallTypeIds%22:%5B%5D%7D"
    request = urllib.request.Request(api_url, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        data = json.loads(body)
        posts = []
        if "data" in data and "contents" in data["data"]:
            items = data["data"]["contents"]["edges"]
            for item in items:
                if "node" in item:
                    node = item["node"]
                    if "headline" in node and "urlAlias" in node:
                        posts.append({
                            "title": node["headline"],
                            "link": base_url + node["urlAlias"]
                        })
        util.info("posts length: {}".format(len(posts)))
        for index in range(min(5, len(posts))):
            link = posts[index]["link"]
            if link in ",".join(urls):
                util.info("exists link: " + link)
                continue

            title = posts[index]["title"]
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "scmp",
                        "kind": 1,
                        "language": "en",
                    },
                )
        
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run)
    # detail = get_detail("https://www.scmp.com/news/hong-kong/society/article/3330763/bear-attacks-japan-why-are-they-rising-and-how-can-hongkongers-stay-safe")
    # util.info("detail: {}".format(detail))
