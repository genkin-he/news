# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": 'MC_INTERSTITIAL_DFP_AD_LOGIC_20250107={"0":"https://www.moneycontrol.com/news/business/markets/"}; A18ID=1736213843818.973322; MC_PPID_LOGIC=normaluser25775195772758296mcids; _gcl_au=1.1.431898145.1736213844; _ga=GA1.1.1655263577.1736213844; _ga_4S48PBY299=GS1.1.1736213844.1.0.1736213844.60.0.0; FCNEC=%5B%5B%22AKsRol9Jyd-MwRM1rIjjVEpJEy8NdW6qfj0wn6eMyOFlQPLuKzJqQLncatVS5uLuOV-NLrQklvBmUMue5cB3IeYq9LfzkQmLCJ2Q6QSM9JvnvXoPp9yHfTAupZgADooUNjgNJWNGqqnBcJalEcyShUtVe19BVoVR6Q%3D%3D%22%5D%5D; _cb=BmuCyLBlL9xgC0s3yD; _chartbeat2=.1736213847690.1736213847690.1.cUt5MDa7MG0BwODuagzDAD45-SW.1; _cb_svref=external; WZRK_G=eadad07f53cb411392d1c91c3ead38af; WZRK_S_86Z-5ZR-RK6Z=%7B%22p%22%3A1%2C%22s%22%3A1736213849%2C%22t%22%3A1736213849%7D; __gads=ID=925169a456627330:T=1736213849:RT=1736213849:S=ALNI_MYRckFkI-kQONM4La3u_HIT2sM_Rg; __gpi=UID=00000fd7c3ca909a:T=1736213849:RT=1736213849:S=ALNI_MbtsO-q5w602eO3CfhhX0f0G6sVXQ; __eoi=ID=d008d5206d7ace14:T=1736213849:RT=1736213849:S=AA-Afja9CewnUhyK_VtBNOppEqic',
}

base_url = "https://www.moneycontrol.com/news/business/markets/"
filename = "./news/data/moneycontrol/list.json"
post_count = 0
util = SpiderUtil()

def get_detail(link):
    print("moneycontrol link: ", link)
    if "videos" in link:
        return ""
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(resp, "lxml")
        soup = soup.select(".content_wrapper")[0]

        # 移除 <div class="mid-arti-ad"> 的元素，使用通配 -ad 方式
        ad_elements = soup.select("[class*=-ad]")
        for element in ad_elements:
            element.decompose()

        ad_elements = soup.select(".related_stories_left_block, script, style, .social_icons_list")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).encode("utf-8").decode("utf-8")
    else:
        print("moneycontrol request: {} error: ".format(link), response)
        return ""


def run():
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(base_url, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select("#cagetory h2 > a")
        for node in nodes:
            if post_count >= 5:
                break
            link = str(node["href"])
            title = str(node.text)
            if link in ",".join(links):
                print("moneycontrol exists link: ", link)
                break

            description = get_detail(link)
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "MoneyControl",
                        "pub_date": util.current_time_string(),
                        "source": "moneycontrol",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("moneycontrol request error: {}".format(response))

util.execute_with_timeout(run)
