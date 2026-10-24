# -*- coding: UTF-8 -*-

import requests
from datetime import datetime, timezone
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8",
    "pa-accept-language": "en",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://www.panewslab.com/",
}
base_url = "https://www.panewslab.com/"
filename = "./news/data/panewslab/list.json"
util = SpiderUtil()


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    response = requests.get(
        "https://universal-api.panewslab.com/articles?type=NEWS&isShowInList=true&take=20&skip=0",
        headers=headers,
    )
    if response.status_code == 200:
        posts = response.json()
        for index, post in enumerate(posts):
            if index < 4:
                id = post["id"]
                link = f"https://www.panewslab.com/articles/{id}"
                if link in ",".join(links):
                    util.info(f"exists link: {link}")
                    continue
                title = post["title"].strip()
                pub_date = util.convert_utc_to_local(
                    datetime.fromisoformat(post["publishedAt"].replace("Z", "+00:00")).timestamp()
                )
                description = post["desc"].strip()
                if description:
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "panewslab",
                            "kind": 2,
                            "language": "zh-CN",
                        },
                    )
        if articles and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")


if __name__ == "__main__":
    util.execute_with_timeout(run)
