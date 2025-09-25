# -*- coding: UTF-8 -*-

import logging
import traceback
import requests  # 发送请求
import json
import re
import time
from util.spider_util import SpiderUtil


headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cooike": '_ga=GA1.1.39404020.1755599302; _pcc=OA0HXhv92nRLOP/4McmB0T6JN491oXj+puI1YMwV4qcdfXgD7ymNcDJKCB951ZngTFQjq1ZQEQx08CnDu8kpEPryfZV91nn404UxB7s+PnM0uN+6868JJMShanQQv17qYMVVv5vfqnqyqJ6iw69d77XXL8gFvkawlAG/lJszyME=; _ga_GRC680FPZR=GS2.1.s1758791392$o2$g0$t1758791392$j60$l0$h0; 168uci=; _cid=07cc19bc68a4a7470fb7489801da1a32; _fxaid=B035ED9623BE659E082C88C30082D6B9%1DNrlA5QN0s%2BMNqB90jxUPpkgy9AzBzbTRf2UYrWHwM0E%3D%1DX%2B3iwmbxM5uTLNSELOAVK0PMFEDrUsyvkXUhpR2WwPm11c%2BzihwG1q07FsyAwa6Y%2FKlM%2Be%2Fw6W7LShi%2F%2FlPwXSUOQnKxIf6Z8jpECV0HCSwk9NEsqqYlPmxVRqCYNP%2B2DMXWeKrXqPE%2FAxXD4oiY59%2BkpoZBR0%2BnR8k2qaMIZUM%3D'
}
base_url = "https://www.fx168news.com/"
filename = "./news/data/fx168/live.json"
util = SpiderUtil()


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    url = "https://centerapi.fx168api.com/cms/api/cmsFastNews/fastNews/getList?fastChannelId=001&pageNo=1&pageSize=20&appCategory=web&direct=down"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()["data"]["items"]
        for index in range(len(result)):
            if index < 5:
                if result[index]["isTop"] != 0:
                    continue
                id = result[index]["fastNewsId"]
                link = "https://www.fx168news.com/express/fastnews/{}".format(id)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                pub_date = result[index]["publishTime"]
                description = result[index]["textContent"]
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": description,
                            "id": id,
                            "description": "",
                            "link": link,
                            "pub_date": pub_date,
                            "source": "fx168",
                            "kind": 2,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)

    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
