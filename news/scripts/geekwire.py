# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
import time
import xml.etree.ElementTree as ET
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

base_url = "https://www.geekwire.com"
filename = "./news/data/geekwire/list.json"
current_links = []
util = SpiderUtil(notify=False)

cookies_str = "csrf_token=a33f3157-f064-4de4-9cb8-412b8c0fc786; _gcl_au=1.1.461866101.1762757637; _ga=GA1.1.1167366699.1762757637; __gads=ID=9312d0ac3de0dbca:T=1762757636:RT=1762757636:S=ALNI_MbFTvI2TFkYK_1gJlAFBA_JqiMhag; __gpi=UID=000011b26ec612db:T=1762757636:RT=1762757636:S=ALNI_MaOHksVOfCI8NH2Cv3byGYZA0S6RQ; __eoi=ID=bfd1d7a71e78a438:T=1762757636:RT=1762757636:S=AA-AfjYFW6veBNzN-CZRI03Mn_qV; FPID=FPID2.2.MrLi3WRL9oWUvqpxLIKcFLxuTMyyfF1RpQ81gGCubuI%3D.1762757637; _fbp=fb.1.1762757636756.1072421584; FPLC=hszOdWF6v1PicMNSlMDX68oDR0rhFmrjbVULCBnHWGOtrF2S233yTTBkyH0lA2iF1Q6%2F6vMEt8OOYgMXde47PZJmLWcs0fh4yBpGebAAysNvULxVhqYxsRTxjTb%2Bgg%3D%3D; __cf_bm=63i7BGGEI0yekXffQZKCzc3Aac2tZMFAv36RtIWkVZI-1762757779-1.0.1.1-xVPhTWAJ9FlGH7nVF_2vIDU3MZVg0WAI6XfRv_ma3nx.rSEc7nZieTNyIDaNcE3fVasd.6orU_tZPDPNWi6BGFiXlqa2_7zHDhoOiiTzQG0; FPGSID=1.1762757636.1762757824.G-PD6PSC6MVD.UcBs1wSmlpZnSlctp7E-Ng; _ga_PD6PSC6MVD=GS2.1.s1762757636$o1$g1$t1762757946$j60$l0$h875564580"

session = requests.Session()
session.headers.update(headers)


def parse_cookies(cookie_string):
    cookies = {}
    for item in cookie_string.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def clean_content_encoded(content):
    if not content:
        return content
    try:
        soup = BeautifulSoup(content, "lxml")
        figure_elements = soup.find_all(["figure", "div"])
        for element in figure_elements:
            element.decompose()
        body = soup.find("body")
        if body:
            return body.decode_contents().strip()
        else:
            return str(soup).strip()
    except Exception as e:
        util.error("Error cleaning content: {}".format(str(e)))
        return content

cookies_dict = parse_cookies(cookies_str)
for key, value in cookies_dict.items():
    session.cookies.set(key, value)


def parse_rss_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)
        namespaces = {
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'atom': 'http://www.w3.org/2005/Atom',
        }
        items = []
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')

            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""

                if title and link:
                    content_encoded = None
                    content_ns = namespaces['content']
                    encoded_elem = item.find(f'.//{{{content_ns}}}encoded')
                    if encoded_elem is not None and encoded_elem.text:
                        content_encoded = encoded_elem.text.strip()
                    content_encoded = clean_content_encoded(content_encoded)
                    items.append({
                        'title': title,
                        'link': link,
                        'content': content_encoded
                    })
        return items
    except ET.ParseError as e:
        util.error("XML parse error: {}".format(str(e)))
        return []
    except Exception as e:
        util.error("RSS parse error: {}".format(str(e)))
        return []

def scrape_feed(feed_url, max_items=3):
    try:
        response = session.get(
            feed_url,
            headers=headers,
            timeout=10,
            proxies=util.get_random_proxy(),
            allow_redirects=True
        )
        if response.status_code == 200:
            rss_items = parse_rss_xml(response.text)
            return rss_items[:max_items]
        else:
            util.error("request url: {}, error: {}".format(feed_url, response.status_code))
            return []
    except Exception as e:
        util.error("Error scraping feed {}: {}".format(feed_url, str(e)))
        return []


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    feed_urls = [
        ("https://www.geekwire.com/amazon/feed/", "amazon"),
        ("https://www.geekwire.com/microsoft/feed/", "microsoft"),
        ("https://www.geekwire.com/ai/feed/", "ai"),
        ("https://www.geekwire.com/tech-moves/feed/", "tech-moves"),
    ]

    try:
        for feed_url, category in feed_urls:
            util.info("Scraping feed: {} ({})".format(feed_url, category))
            rss_items = scrape_feed(feed_url, max_items=3)
            for item in rss_items:
                link = item['link']
                title = item['title']
                content = item.get('content')
                if link in _links:
                    util.info("exists link: {}".format(link))
                    continue
                if not title:
                    continue
                description = content
                if description:
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "geekwire",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    if not content:
                        time.sleep(0.5)

        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run)

