# -*- coding: UTF-8 -*-

from datetime import timedelta, timezone
import requests
from util.spider_util import SpiderUtil

util = SpiderUtil()
base_url = "https://api.unusualwhales.com/market_news/api/free_news?page=0"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
filename = "./news/data/unusualwhales/list.json"

def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用requests发送请求
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        result = response.json()["news"]
        for index in range(len(result)):
            if index < 10:
                if result[index]["source"] == "Bloomberg":
                    continue
                id = result[index]["id"]
                link = "https://www.markets.news/headlines/{}".format(id)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                pub_date = util.parse_time(result[index]["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                title = result[index]["headline"]
                description = result[index]["summary"]
                if not description:
                    description = title
                    title = ""
                articles.insert(
                    0,
                    {
                        "title": title,
                        "id": id,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                        "source": "unusualwhales",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)

    else:
        util.log_action_error("request error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run)
