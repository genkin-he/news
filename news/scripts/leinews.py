# -*- coding: UTF-8 -*-

import logging
import traceback
import urllib.request  # 发送请求
import json
import re
import time
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}
base_url = "https://www.leinews.com"
filename = "./news/data/leinews/list.json"
util = SpiderUtil()


def get_detail(id):
    util.info("link: {}".format(id))
    data = {
        "flag": 1720686920447,
        "MethodName": "YiAPP.APP.SHOP%7CYiAPP.APP.SHOP.uNews.PC_GetNewsInfo",
        "queryparams": "%7B%22NewsCode%22%3A%22{}%22%7D".format(id),
        "sikw": 1,
    }

    try:
        request = urllib.request.Request(
            "https://www.leinews.com/Common/YiAPP.ashx?YiAPP_Method=uNews.PC_GetNewsInfo&YiAPP_Action=YiAPP.APP.SHOP&YiAPP_SIKW=true",
            bytes(json.dumps(data), encoding="utf8"),
            headers,
            method="POST",
        )
        response = urllib.request.urlopen(request)
        if response.status == 200:
            body = response.read().decode("utf-8")
            json_data = json.loads(body)
            if "data" not in json_data:
                util.info(f"API response missing 'data' field: {body}")
                return ""
            if "NewsContent" not in json_data["data"]:
                util.info(f"API response missing 'NewsContent' field: {json_data}")
                return ""
            body = json_data["data"]["NewsContent"]
            body = body.replace("雷递由媒体人雷建平创办，若转载请写明来源。", "")
            return body
    except Exception as e:
        util.info(f"Error getting detail for {id}: {str(e)}")
        return ""


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    data = {
        "flag": int(round(time.time() * 1000)),
        "MethodName": "YiAPP.APP.SHOP%7CYiAPP.APP.SHOP.uNews.PC_SearchNewsInfoList",
        "queryparams": "%7B%22ShopUser%22:%2280889%22,%22ColumnCode%22:%22%22,%22page%22:%221%22,%22rows%22:%2210%22%7D",
        "sikw": 1,
    }
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.leinews.com/Common/YiAPP.ashx?YiAPP_Method=uNews.PC_SearchNewsInfoList&YiAPP_Action=YiAPP.APP.SHOP&YiAPP_SIKW=true",
        bytes(json.dumps(data), encoding="utf8"),
        headers,
        method="POST",
    )

    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        result = json.loads(body)["data"]["data"]
        for index in range(len(result)):
            # 跳过第一个
            if index == 0:
                continue
            if index < 3:
                id = result[index]["NewsCode"]
                link = "https://www.leinews.com/n{}/detail.html".format(id)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                title = result[index]["NewsTitle"]
                image = result[index]["NewsImage"]
                pub_date = result[index]["CreateDate"]
                description = get_detail(id)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "id": id,
                            "description": description,
                            "link": link,
                            "image": image,
                            "pub_date": pub_date,
                            "source": "leinews",
                            "kind": 1,
                            "language": "zh-CN",
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
