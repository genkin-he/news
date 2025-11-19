# -*- coding: UTF-8 -*-
import urllib.request  # 发送请求
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
    "cookie": "XSRF-TOKEN=eyJpdiI6ImdjOFpxSUxVT29BK05zcFRkZGRUYmc9PSIsInZhbHVlIjoidzJIY0VqMVdRTHU0RHVHK3Q1R3VrVmhNckEwSzJmaUxBaDE0dEFQNHVUaHhSXC9QNGpGazRPTkViWGMyMkVPbUZYQnp5cGlXRmt3REdNSlNuOW9maVNnPT0iLCJtYWMiOiI2MjJiMGI0MzhjZjY4YmI5OGM2YzQ5NzA2MTY4ZmJkM2VjYTFlM2MyZjFkMjVhNmYwYjQxNTUzMGE3NDJmOTYxIn0%3D; bioon_session=eyJpdiI6IldhaTh1WVFXeXg5eHUwWXRSSHRrUWc9PSIsInZhbHVlIjoiUkRoUGZYMnV2U00xc2gwMDFpMCtJV0U0bWFWb1Bhclk3bDVwWFVjUEhcL0xZdXVYZlFHSm03M2tHMzR6UEN1QllHSkJrNERERklKYmpkXC9ZTUFrVnZmZz09IiwibWFjIjoiNzA1NjkzZWU3OWU2YjA2MTYwZDIxMDU4ZWY3NDEzNzAwZWRhZGNmMTliODg4OGM0YTkwYTM1YjcwYzM2NDNhNiJ9; _ga_Q9WJ5CGWD2=GS1.1.1737343905.1.0.1737343905.0.0.0; _ga=GA1.1.1580633639.1737343906; Hm_lvt_1e2aa76b9e893c2641e3129643165132=1737343906; Hm_lpvt_1e2aa76b9e893c2641e3129643165132=1737343906; HMACCOUNT=6B118520F26BD1AD; gr_user_id=d60314aa-2af4-49b7-936b-493b650d5e93; aea9aa242cc95dc5_gr_session_id=8380781d-460d-4eb9-8a77-e6bb8367b234; msStatisUserId=1737343906099_d461b2e2; aea9aa242cc95dc5_gr_session_id_sent_vst=8380781d-460d-4eb9-8a77-e6bb8367b234",
}

base_url = "https://www.bioon.com/"
filename = "./news/data/bioon/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select('.composs-main-content div[style="color: #303a4e;"]')[0]

        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".composs-blog-list > .item")
        for index in range(len(items)):
            if index > 1:
                break
            link = items[index].select(".item-content> h2 > a")[0]["href"].strip()
            title = items[index].select(".item-content> h2 > a")[0].text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
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
                        "source": "bioon",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
