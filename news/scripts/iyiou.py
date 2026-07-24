# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "UM_distinctid=191b6e1d73f10e-05e019dfcd48f1-18525637-1fa400-191b6e1d74020ad; CNZZDATA1279392180=182302582-1725350140-https%253A%252F%252Fwww.iyiou.com%252F%7C1725351241; w_tsfp=ltvuV0MF2utBvS0Q66/qkUqsEDglfDg4h0wpEaR0f5thQLErU5mH1IV/v8nxMXXd48xnvd7DsZoyJTLYCJI3dwMRE8qXe4lH3wiXk9Qm3YpBBxgxGMrdDFFMdrkk6mZDKHhCNxS00jA8eIUd379yilkMsyN1zap3TO14fstJ019E6KDQmI5uDW3HlFWQRzaLbjcMcuqPr6g18L5a5W2Nt1v4KFwiArxK0EOU1H4cC3kjsxS8fOoJNhStcJioSqA=",
}

base_url = "https://www.iyiou.com/"
filename = "./news/data/iyiou/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".post-body")[0]

        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # 使用requests发送请求
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        body = response.text
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".info-item")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].select(".webTitleShow")[0]["href"].strip()
            title = items[index].select(".webTitleShow")[0].text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "iyiou",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.iyiou.com/news")
