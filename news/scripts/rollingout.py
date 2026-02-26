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
    "cache-control": 'max-age=0',
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
    "cookie": 'cf_clearance=qPQU_MKDpIuGzQw1lfCbwQRbl5rK2M2A6ppMYU6Jd_g-1762745743-1.2.1.1-DvVmuQBGl8BciaL47xHJfi398soZAvDsn5BMWnY_Jw5tOPQ0WU0N5bkJgAaQnnQyTl_oP1S1stFeKU2lLTeZj5q36yxN3_Q9h9q82VuCvpjWcdDZmmg_GirO6BCAlZMZoNawHVI.h1xRXRO6BFA5F47T8eM7ThMi8VrSDSnzqqIYG48tJd7ps9rGzPtB0y4pmi0K8WaYbCottaj1wUCwW038nnkKyVx7JXJTOHdO3IQ; advanced_ads_visitor=%7B%22browser_width%22%3A1512%7D; _ga=GA1.1.1672398979.1762745746; _clck=1nlzoas%5E2%5Eg0w%5E0%5E2140; __gads=ID=2a4d3bf0b9ba17af:T=1762745746:RT=1762745746:S=ALNI_MZQyYhlP8FTBULfF6s1AEkieFFV8A; __gpi=UID=000011b24c9eb842:T=1762745746:RT=1762745746:S=ALNI_Ma-Fnw1hQ55AvjVqBnL7QkykpOG0g; __eoi=ID=dca59e312a71da0b:T=1762745746:RT=1762745746:S=AA-AfjZiP25QjnvvsbHWQJva5M5n; _fbp=fb.1.1762745746488.283068091880331641; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1794281748%2C%22data%22%3A%22https%3A%2F%2Frollingout.com%2Fcategory%2Ftech%2F%22%7D; izootoWpConfig=%7B%22b_type%22:1,%22d_type%22:1,%22evt_trk%22:1,%22izooto_uid%22:%22c79e58f6-42e2-4d68-b5c9-7be024db375d%22%7D; pvc_visits[0]=1762832149b1704172; advanced_ads_page_impressions=%7B%22expires%22%3A2078105745%2C%22data%22%3A3%7D; _ga_077WJ26B3P=GS2.1.s1762745745$o1$g1$t1762745759$j46$l0$h0; _awl=2.1762745760.5-52fa01054d7d1d484ab25c5863083461-6763652d617369612d6561737431-0; _clsk=tf5frn%5E1762745761664%5E3%5E1%5Ek.clarity.ms%2Fcollect'
}
base_url = "https://rollingout.com"
filename = "./news/data/rollingout/list.json"
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
            # util.info("body: {}".format(str(body)))
            soup = body.select_one('div.standard-markdown')
            if not soup:
                soup = body.select_one('div.elementor-widget-theme-post-content')
            if not soup:
                util.error("article content not found: {}".format(link))
                return ""
            ad_elements = soup.select("script, style, iframe, noscript, div")
            for element in ad_elements:
                element.decompose()
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
            "https://rollingout.com/category/tech/", headers=headers, timeout=5, proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select("h3.elementor-post__title a")
            for index, item in enumerate(items):
                if index > 4:
                    break
                link = item["href"].strip()
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

        else:
            util.error("request url: {}, error: {}, response: {}".format("https://rollingout.com/category/tech/", response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)

