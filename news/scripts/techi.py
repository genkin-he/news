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
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"141.0.7390.108"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.108", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

base_url = "https://www.techi.com"
filename = "./news/data/techi/list.json"
current_links = []
util = SpiderUtil(notify=False)

# Cookie string for RSS feed access
cookies_str = "cf_clearance=rYFzojphyvZqzh4eOtzdeamD4pT4b6cFs3rx50lez7c-1762753514-1.2.1.1-lHuWOddpI5ImY2mqM.V9YPooDbj8aUnacetP9JgJB8Gk4S69ue6sziRpH8.4HKWQKdm.R0suRiODCbuVL0XMkoTPaMtm7_jXkosw9qtXJUBdwagn0fVI4ywYEzc9qvZh5J2UteDo5ZdB5zAqEWjO0bU3ANX3qx3YEMfIvDK4NBNubLLzLG55ydNdalC_92n.OavW3BMdAe10oVdERStE0kajHhe7IwFlHH5P6m0t7h4; aawp-country=CH; _gcl_au=1.1.741167545.1762753519; _ga=GA1.1.870660519.1762753519; _ga_0BXX1SX6FP=GS2.1.s1762758160$o2$g1$t1762758198$j22$l0$h1599032632"

# Create a session to maintain cookie state
session = requests.Session()
session.headers.update(headers)


def parse_cookies(cookie_string):
    """Parse cookie string into dictionary"""
    cookies = {}
    for item in cookie_string.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


# Set cookies in session
cookies_dict = parse_cookies(cookies_str)
for key, value in cookies_dict.items():
    session.cookies.set(key, value)


def parse_rss_xml(xml_content):
    """Parse RSS XML feed and extract items"""
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""
                if title and link:
                    items.append({
                        'title': title,
                        'link': link
                    })
        return items
    except ET.ParseError as e:
        util.error("XML parse error: {}".format(str(e)))
        return []
    except Exception as e:
        util.error("RSS parse error: {}".format(str(e)))
        return []


def get_detail(link):
    """Fetch and extract article content from detail page"""
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = session.get(
            link,
            headers=headers,
            timeout=10,
            proxies=util.get_random_proxy(),
            allow_redirects=True
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select_one('div.post-content')
            if not soup:
                util.error("article content not found: {}".format(link))
                return ""
            ad_elements = soup.select("script, style, iframe, noscript")
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except requests.exceptions.RequestException as e:
        util.error("request exception: {}".format(str(e)))
        return ""
    except Exception as e:
        util.error("unexpected exception: {}".format(str(e)))
        return ""


def run():
    """Main function to fetch RSS feed and process articles"""
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        url = "https://www.techi.com/category/instruments/feed/"
        response = session.get(
            url,
            headers=headers,
            timeout=10,
            proxies=util.get_random_proxy(),
            allow_redirects=True
        )
        if response.status_code == 200:
            rss_items = parse_rss_xml(response.text)
            data_index = 0
            for item in rss_items:
                if data_index >= 5:
                    break
                link = item['link']
                title = item['title']
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                if not title:
                    continue
                description = get_detail(link)
                if description:
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "techi",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1
                    time.sleep(0.5)
        else:
            util.error("request url: {}, error: {}".format(url, response.status_code))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run)

