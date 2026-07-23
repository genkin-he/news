# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'en;q=0.9',
    "cache-control": 'max-age=0',
    "if-none-match": '"5d983-himsmE9zWcK1u7otxdNbP3aWyJg"',
    "priority": 'u=0, i',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'device_id=4fccd9d6-056d-4d80-878c-6831c18fd195; _gid=GA1.2.1074707447.1759027181; permutive-id=1d28bc32-326f-4752-9d56-4fcb06140fcb; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://sherwood.news/markets/%22%2C%22sref%22:%22%22%2C%22sts%22:1759027181583%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=d83f4c08-92da-4027-bc20-08d4a9d0e1d2%22%2C%22session_count%22:1%2C%22last_session_ts%22:1759027181583}; _hp5_meta.3593826604=%7B%22userId%22%3A%223982498583538161%22%2C%22sessionId%22%3A%225328511002307226%22%2C%22sessionProperties%22%3A%7B%22time%22%3A1759027182250%2C%22id%22%3A%225328511002307226%22%2C%22utm%22%3A%7B%22source%22%3A%22%22%2C%22medium%22%3A%22%22%2C%22term%22%3A%22%22%2C%22content%22%3A%22%22%2C%22campaign%22%3A%22%22%7D%2C%22initial_pageview_info%22%3A%7B%22time%22%3A1759027182250%2C%22id%22%3A%22927273680250621%22%2C%22title%22%3A%22Markets%20-%20Sherwood%20News%22%2C%22url%22%3A%7B%22domain%22%3A%22sherwood.news%22%2C%22path%22%3A%22%2Fmarkets%2F%22%2C%22query%22%3A%22%22%2C%22hash%22%3A%22%22%7D%7D%2C%22search_keyword%22%3A%22%22%2C%22referrer%22%3A%22%22%7D%7D; __gads=ID=70bfbdafc5c28361:T=1759027310:RT=1759027310:S=ALNI_MZYPZQlh7eoB5K9SCiGEzWHHQU17w; __gpi=UID=000011567ff0af39:T=1759027310:RT=1759027310:S=ALNI_Map58Spf_PvCgVrpCnwN5FNNOETXQ; __eoi=ID=e4df9d0ea12238fe:T=1759027310:RT=1759027310:S=AA-AfjZlNSnesoFUvs7I3I1k1dfw; _fbp=fb.1.1759027578397.243223015708302734; _hp5_event_props.3593826604=%7B%22author_name%22%3A%22Nia%20Warfield%22%7D; sailthru_hid=7167cd923381ef9a845d83e5b33526e668d8a4aa4db7f3cdbf06df96221a6d1647c8ceed34aa925c22171c4b; sailthru_hid=7167cd923381ef9a845d83e5b33526e668d8a4aa4db7f3cdbf06df96b9264d30fb0eb972c604e864c353d0ae; sailthru_bid=68d8a4ab58967e597a55733a; _ga=GA1.1.1356125287.1759027181; sailthru_pageviews=12; session_id=48496150-7bc6-4bdb-84d5-2c0cc978ce96; sailthru_content=5afa1839d084d79e9a8cec903d729227bc0326ad0cd22e6d5c63f9e94e6df3ba02eaa2c076d99384e6c3efea4efe2069fff679c911d576b2abe95ead00e5e146d1b73bcd31a451e7801f9fcb04c292df83b603c5263ef60b9fad365fdd49b210; sailthru_visitor=916d5598-ea20-42c2-85f4-5fb918c25107; _ga_FYF4EQB2TV=GS2.1.s1759027181$o1$g1$t1759028601$j60$l0$h0; _parsely_slot_click={%22url%22:%22https://sherwood.news/markets/%22%2C%22x%22:472%2C%22y%22:478%2C%22xpath%22:%22//*[@id=%5C%22__next%5C%22]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/a[1]%22%2C%22href%22:%22https://sherwood.news/markets/croc-rises-on-new-marketing-campaign-for-heydude-brand-starring-sydney/%22}; _hp5_let.3593826604=1759028617329',
}

base_url = "https://sherwood.news"
filename = "./news/data/sherwood/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(node):
    a = node.select("a")[0]
    a.decompose()
    ad_elements = node.select("div")
    # 移除这些元素
    for element in ad_elements:
        element.decompose()

    return str(node).strip()

def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(url, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes_one = soup.select("div.css-ivtglt")
        nodes_two = soup.select("div.css-12fbs19")
        nodes = nodes_one + nodes_two
        for node in nodes:
            # if post_count >= 2:
            #     break
            a = node.select("a")[0]
            link = base_url + str(a["href"].strip())
            title = str(a.text.strip())
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            if title == "":
                continue
            post_count = post_count + 1
            description = get_detail(node)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "sherwood",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


link1 = "https://sherwood.news/markets/"
if __name__ == "__main__":
    util.execute_with_timeout(run, link1)
