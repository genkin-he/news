# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
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

cookies_str = "_pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIEYOAWDgTgBsAVgAcXDgCZJAZgHchAdhABfIA; _pcid=%7B%22browserId%22%3A%22mj8fhcb97tdkhhry%22%7D; _gcl_au=1.1.1318053505.1765880207; _ga=GA1.1.1190398296.1765880208; compass_uid=921d432b-9165-45c8-baba-86f855a7adf1; __pid=.americanbanker.com; __pnahc=0; oly_fire_id=4014E3567790A2D; oly_anon_id=d16de650-1385-40ce-b34a-048d1424b960; __pat=-18000000; _pcus=eyJ1c2VyU2VnbWVudHMiOnsiQ09NUE9TRVIxWCI6eyJzZWdtZW50cyI6WyJMVGM6Yjg5YTVlOTMyZWZjMWExMDM3M2ZkM2Q2OWE4YmM1ZGY3ZWMyMDk1MTpub19zY29yZSIsIkxUczpkN2M0ZTk4YmEzNDgyZDMyZjExYjM0Yzg2MDJlY2Y1MzI0MTEzYzRjOm5vX3Njb3JlIiwiTFRyZXR1cm46OWMzNDZiZTEyNDlhZTczMjQ0MWY1YzI0NmVmMThlYzBlNmViYzM0MDpub19zY29yZSJdfX19; _pc_sub_promo_bottom_banner=true; pnespsdk_visitor=d88jh8qhy9avbf3d; _cb=ByArpkBTVFAmSx_TZ; LANG=en_US; cX_P=mj8fhcb97tdkhhry; LANG_CHANGED=en_US; dpm_uid=019b26a9-b9e1-7dec-93f7-774de9fd1591; hasLiveRampMatch=true"

base_url = "https://www.americanbanker.com"
feed_url = "https://www.americanbanker.com/feed"
filename = "./news/data/americanbanker/list.json"
util = SpiderUtil()

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
    session.cookies.set(key, value)


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = session.get(link, timeout=10)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
        soup = BeautifulSoup(response.text, "lxml")
        content = soup.select_one(".RichTextBody")
        if not content:
            return ""
        ad_elements = content.select("script,style,div")
        for element in ad_elements:
            element.decompose()
        return str(content).strip()
    except Exception as e:
        util.error("exception: {}".format(str(e)))
        return ""


def run():

    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    post_count = 0

    try:
        response = session.get(feed_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            nodes = soup.select(".PromoMediumImageRight-title > a")
            for node in nodes:
                if post_count >= 3:
                    break
                href = node.get("href", "").strip()
                if not href:
                    continue
                link = href if href.startswith("http") else base_url + href
                if link in links:
                    util.info("exists link: {}".format(link))
                    continue
                title = node.get_text().strip()
                if not title:
                    continue
                description = get_detail(link)
                if description:
                    post_count += 1
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "americanbanker",
                            "kind": 1,
                            "language": "en",
                        },
                    )
            if len(articles) > 0 and insert:
                if len(articles) > 20:
                    articles = articles[:20]
                util.write_json_to_file(articles, filename)
        else:
            util.log_action_error("request error: {}".format(response.status_code))
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run)
