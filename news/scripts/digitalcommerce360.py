# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
from datetime import datetime
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "Referer": "https://www.digitalcommerce360.com/type/news/",
    "Referrer-Policy": "no-referrer-when-downgrade",
}
base_url = "https://www.digitalcommerce360.com/"
filename = "./news/data/digitalcommerce360/list.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    data = {
        "requests": [
            {
                "indexName": "wp_searchable_posts_genre",
                "params": "facetingAfterDistinct=true&facets=%5B%22genre%22%2C%22taxonomies.vertical%22%5D&filters=taxonomies.genre%3A'News'&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=50&page=0&query=&tagFilters=",
            }
        ]
    }

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://rsx8q1fola-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.18.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.56.5)%3B%20JS%20Helper%20(3.13.2)&x-algolia-api-key=62bbeeff0c155050d813eec2f8bb0b36&x-algolia-application-id=RSX8Q1FOLA",
        bytes(json.dumps(data), encoding="utf8"),
        headers,
        method="POST",
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["results"][0]["hits"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["post_id"]
                title = post["post_title"]
                link = post["permalink"]
                description = post["subhead"]
                pub_date = datetime.fromtimestamp(post["post_date"]).strftime("%Y-%m-%d %H:%M:%S")
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "digitalcommerce360",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 5:
                articles = articles[:5]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
