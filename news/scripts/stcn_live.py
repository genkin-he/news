# -*- coding: UTF-8 -*-

from datetime import timedelta, timezone
import requests  # 发送请求
from util.spider_util import SpiderUtil

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "acw_tc=1a1c720617417611872291601e03bf868b220d52b036943637c8ec63a88b5b; advanced-stcn_web=7mvrte4mm31ca7pqn5f9b3rf26; UM_distinctid=195890e914459f-0b256141605ff8-1c525636-1fa400-195890e914520a7; _c_WBKFRo=kgTZ5rfeWNmghHdZBCr2VqTy6wqVQdaqiaMBmf5q; _nb_ioWEgULi=; CNZZDATA1281191046=652689479-1741761216-%7C1741761216; CNZZDATA1281265122=1239071273-1741761216-%7C1741761216; CNZZDATA1281188246=1658523165-1741762232-%7C1741762232; CNZZDATA1281265113=667652499-1741762232-%7C1741762232; CNZZDATA1281180659=390309885-1741761188-%7C1741762762; CNZZDATA1281265092=723305418-1741761188-%7C1741762762; CNZZDATA1281169049=648567861-1741761189-%7C1741762763; CNZZDATA1281264856=1368405688-1741761189-%7C1741762763",
}
base_url = "https://www.stcn.com/"
filename = "./news/data/stcn/live.json"
util = SpiderUtil()


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用requests发送请求获取响应
    response = requests.get(
        "https://www.stcn.com/article/list.html?type=kx",
        headers=headers
    )

    # 检查响应状态
    if response.status_code == 200:
        result = response.json()["data"]
        for index in range(len(result)):
            if index < 10:
                link = "https://www.stcn.com{}".format(result[index]["url"])
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                id = result[index]["id"]
                title = result[index]["title"]
                pub_date = util.convert_utc_to_local(
                    result[index]["show_time"], tz=timezone(timedelta(hours=8))
                )
                description = result[index]["content"]
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "id": id,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "stcn",
                            "kind": 2,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)

    else:
        util.log_action_error("request error: {}".format(response))


util.execute_with_timeout(run)
