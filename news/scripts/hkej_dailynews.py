# -*- coding: UTF-8 -*-

import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}
base_url = "https://www1.hkej.com"
filename = "./news/data/hkej/dailynews.json"
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split('<div  id="article-detail-wrapper">')[1]
        .split("<script>var isFullArticle=")[0]
    )
    body = re.sub(r"(\t)\1+", "", body)
    body = re.sub(r"(\n)\1+", "\n", body)
    body = body.lstrip()
    return body


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www1.hkej.com/dailynews/headline", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        result = re.findall(".*<option value='(.*) </option>*", body)
        for index in range(len(result)):
            if index < 3:
                item = result[index].split("'>")
                link = base_url + item[0]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                title = item[1]
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
                            "source": "hkej",
                            "kind": 1,
                            "language": "zh-HK",
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
