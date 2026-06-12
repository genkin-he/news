# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "cookie": "yu_id=cd44149626e78a1633fb5a1d563c0a14; _ga=GA1.1.376971415.1762767224; _ga_LYF4P32HZ2=GS2.1.s1762767223$o1$g1$t1762767454$j46$l0$h0; tfstk=gOFKK6b8XNLpKb-eJuXGE7nP7f_GnO4UWkzXZ0mHFlETlr-nFp2n2bE30bmhU978BuZZKDil80L-T52HZDjEwzZmwijcis4U8Xh5mibU_ElSN41oVODI6n_rYijci1vsSvQVmyDKhzhszcgIP2iCWVgqRbgWNuisCqgDAbG7VNHs-4OSPbGSf1grf0GSNua1W4msRbG7VP_tzU0F2cTIqQeEVvIc_n3eNQNtJA6gRc9jY53KpmaQ9FT632HKcyiOvwT_sYEKp5fp02e_kluL4sREOYeQhXNRD6h_uRqIWusvecwYT7H09ipqAWozDXwOfBhS6qU-nRbWHc2775HT9tYr7W47TxcfgHiuIrF-y7SP6oUQv-MbOHIPLSVxdq-mD4vCWNpyUvgZGpjBf9kzc20tmwCJULkN7QvLiiJWFnSoWmbgQLJrQN5..",
}

base_url = "https://www.yicaiglobal.com"
filename = "./news/data/yicaiglobal/list.json"


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one("#news-body")
            if not soup:
                util.error("article content not found: {}".format(link))
                return ""
            ad_elements = soup.select("script, style, iframe, noscript")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        for category_id in [3, 4, 5]:
            api_url = "https://www.yicaiglobal.com/api/getNewsList"
            params = {
                "type": "",
                "id": category_id,
                "pagesize": 10,
                "page": 1,
            }
            response = requests.get(
                api_url, headers=headers, params=params, timeout=5, proxies=util.get_random_proxy()
            )
            if response.status_code == 200:
                result = response.json()
                news_list = result if isinstance(result, list) else result.get("data", [])
                count = 0
                for news_item in news_list:
                    if count >= 2:
                        break
                    news_title = news_item.get("NewsTitle", "").strip()
                    news_url = news_item.get("NewsUrl", "").strip()
                    if not news_title or not news_url:
                        continue
                    full_url = urljoin(base_url, news_url)
                    if full_url in ",".join(links):
                        util.info("exists link: {}".format(full_url))
                        continue
                    description = get_detail(full_url)
                    if description:
                        insert = True
                        articles.insert(
                            0,
                            {
                                "title": news_title,
                                "description": description,
                                "link": full_url,
                                "pub_date": util.current_time_string(),
                                "source": "yicaiglobal",
                                "kind": 1,
                                "language": "en",
                            },
                        )
                        count += 1
            else:
                util.error("request url: {}, error: {}".format(api_url, response.status_code))

        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run)

