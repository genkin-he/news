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
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "acw_tc=1a193f3e17422067469935196ee4f9e77e4f67c75ef57b975a2fefcaeedd50; advanced-stcn_web=kvcf1lf1ediai9s7dsg0see0h0; UM_distinctid=195a39d43802390-0db1e9189c1cf8-1b525636-1fa400-195a39d4381460a; _c_WBKFRo=R2On5yDbNfABM73S02p0tz7ykN6tqknC8inEIOg9; _nb_ioWEgULi=; CNZZDATA1281180659=1225199122-1742206748-%7C1742206866; CNZZDATA1281265092=1479603193-1742206748-%7C1742206867; CNZZDATA1281169049=1283367098-1742206748-%7C1742206867; CNZZDATA1281264856=216425009-1742206748-%7C1742206867",
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
        "https://www.stcn.com/article/list.html?type=kx", headers=headers
    )

    # 检查响应状态
    if response.status_code == 200:
        result = response.json()["data"]
        if not result:
            util.log_action_error("result is empty")
            return

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

# util.execute_with_timeout(run)
