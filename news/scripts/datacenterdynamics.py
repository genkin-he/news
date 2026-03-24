# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": '_mkto_trk=id:665-KXY-697&token:_mch-datacenterdynamics.com-714c96905b7cf4f7df34c63fa62be2b5; __gads=ID=0d034027c26a3564:T=1762744726:RT=1762744726:S=ALNI_Mbq4VooZf_SDhYw-fYwZ24J9NV_RA; __gpi=UID=000011b24ace13eb:T=1762744726:RT=1762744726:S=ALNI_Ma-VN_KP7J6BE6en42IHZWtKcr3bg; __eoi=ID=021d50a9e95c2b79:T=1762744726:RT=1762744726:S=AA-AfjZmp0_9N0XtgI_bcvgNPBbD; _gd_visitor=ecf16f29-a9c8-4a05-87f8-da8fec8e812c; _gd_session=3571ae00-8403-4698-8035-4e1271f1c784; _clck=z9x65s%5E2%5Eg0w%5E0%5E2140; _gid=GA1.2.1797014931.1762744728; __adroll_consent=CQaq64AQaq64AAAACBENANFv_____0P__wwIASP_____wAkf_____gAA%23N7EHSCRPI5BI7EAVKEQAXU; __adroll_fpc=91ad641ddb10fe14e59a99c34812bd8b-1762744757574; _gat=1; _ga_4K5XCNKZYJ=GS2.1.s1762744726$o1$g1$t1762744815$j21$l0$h0; __ar_v4=N7EHSCRPI5BI7EAVKEQAXU%3A20251110%3A5%7CY25TPWYXGRFGVB3CFLLIPA%3A20251110%3A5%7CUX3TZRZKYRGVFLNQ3E7CIG%3A20251110%3A5; _clsk=yek7md%5E1762744816512%5E4%5E1%5Ek.clarity.ms%2Fcollect; _ga=GA1.2.642020076.1762744726'
}
base_url = "https://www.datacenterdynamics.com/"
filename = "./news/data/datacenterdynamics/list.json"
current_links = []
util = SpiderUtil(notify=False)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = requests.get(link, headers=headers, timeout=5, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select('div.block-text')
            for item in soup:
                p_elements = item.select("p")
                for p in p_elements:
                    result.append(p.get_text().strip())
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(
            "https://www.datacenterdynamics.com/en/news/?page=1", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select("h1.card__title a")
            data_index = 0
            for index, item in enumerate(items):
                if data_index > 4:
                    break
                link = base_url + item["href"].strip()
                title = item.get_text().strip()
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
                            "source": "startuphub",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format("https://www.datacenterdynamics.com/en/news/?page=1", response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.info("403 Forbidden")
    # util.execute_with_timeout(run)

