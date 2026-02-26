# -*- coding: UTF-8 -*-
import time
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
}

cookies_str = "UDN_FID=42696731eb5cf98a11762789baea9fbd; _gcl_au=1.1.1556304921.1766628651; _ga_9JF5B6B4XT=GS2.1.s1766628651$o1$g0$t1766628651$j60$l0$h0; _ga=GA1.1.475227870.1766628651; _ga_FER55E1780=GS2.1.s1766628651$o1$g0$t1766628651$j60$l0$h0; __AP_SESSION__=ea74dae0-e1ec-418c-86c4-b0a9bf84fe31; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22ea193dbf-674b-43ea-b77b-fc5b9c7e3998%5C%22%2C%5B1766628652%2C350000000%5D%5D%22%5D%5D%5D; __gads=ID=45d81e160cdf3a52:T=1766628652:RT=1766628652:S=ALNI_MbPKlNGTDPWIoEFkCM5i7syGyoPIg; __gpi=UID=000011d33cf46525:T=1766628652:RT=1766628652:S=ALNI_MYRiSF2l8t5KhgBcEThI1ARO4wvsA; __eoi=ID=470eff46ba9316f7:T=1766628652:RT=1766628652:S=AA-AfjYsI1skHWSP1Co_KKQ5gUR-; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId_expiry=1767233453505; panoramaId=634981e977399532212294ad33ff185ca02c4b1e31d914eecb32fa2e903c547e; panoramaIdType=panoDevice; cto_bundle=uyiAP19OVGtnclFsZlo3VTgzZ2N4YU9GUFplYmFsSWQ0N3V0Y3VnZXhZVG94c1NXbFNSQmFDV3BxZjFseFZDZFZDVnQlMkZTa01UZXFJQUw1YzFMN2tjcm50N0lhVUxNYmh5U2dzc3R3JTJCV0NOck81WmxMJTJCWGxHOUclMkZ4RSUyQkpaMWlXZHQlMkZvbHd1OVNUQjJRUGtiTnRDcklIankxJTJCVGZFRUhkVGlqdnFEJTJCaFJJaU1hWGx2V3JZQ2wlMkJIcGNiJTJGWkR1ZWhTcnBQNg; __qca=P1-3ec61dd6-78c9-4b78-95cf-8fb44debabf0; FCNEC=%5B%5B%22AKsRol_5rVfMoLu7N3InTu8uIeFs-3DLdh1RLRIL5Kd04T2M73qm_tN5jqRzo3YC8ta0sNJZo1EyTwgORd-gSHbIPsfBCfiD-cITSK0F3_uR8Tjo2HlvSFtinlBqx_h2iu6-T8SKMadJrUDvOUxWKIyee5-XPb7spw%3D%3D%22%5D%5D; dable_uid=56682658.1757476444221"

base_url = "https://money.udn.com"
filename = "./news/data/udn/list.json"
current_links = []
util = SpiderUtil(notify=False)

session = requests.Session()
session.headers.update(headers)


def parse_cookies(cookie_string):
    cookies = {}
    for item in cookie_string.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


cookies_dict = parse_cookies(cookies_str)
for key, value in cookies_dict.items():
    session.cookies.set(key, value, domain=".udn.com")


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    time.sleep(1)
    try:
        response = session.get(link, timeout=10, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one("#article_body")
            if not soup:
                return ""
            ad_elements = soup.select("figure, div")
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
        all_items = []
        response = session.get(
            "https://money.udn.com/rank/newest/1001/0/1",
            timeout=10,
            proxies=util.get_random_proxy(),
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items1 = soup.select(".story__content a")
            for item in items1:
                link = item["href"].strip()
                title = item.select_one(".story__headline").text.strip()
                if link and title:
                    all_items.append({"link": link, "title": title.strip()})
            for index, item in enumerate(all_items):
                if index > 4:
                    break
                link = item["link"].strip()
                title = item["title"].strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description != "":
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "forbes",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        else:
            util.error(
                "request url: {}, error: {}".format(
                    "https://money.udn.com/rank/newest/1001/0/1", response.status_code
                )
            )

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run)
