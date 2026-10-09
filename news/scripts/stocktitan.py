# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
import xml.etree.ElementTree as ET
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}

base_url = "https://www.stocktitan.net"
filename = "./news/data/stocktitan/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        if "Access Restricted" in resp:
            raise Exception("Connection reset by peer") 
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select(".article")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            ad_elements = soup.select(".article-rhea-tools,.share-social-group,.adthrive-ad,#faq-container,script,#PURL,.article-title,time")
            for element in ad_elements:
                element.decompose()

        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def parse_rss_xml(xml_content):
    """Parse RSS XML feed and extract items"""
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall('.//item'):
            if len(items) >= 20:
                break
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""
                pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""
                if title and link:
                    items.append({
                        'title': title,
                        'link': link,
                        'pub_date': pub_date
                    })
        return items
    except ET.ParseError as e:
        util.error("XML parse error: {}".format(str(e)))
        return []
    except Exception as e:
        util.error("RSS parse error: {}".format(str(e)))
        return []

def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        xml_content = response.text
        rss_items = parse_rss_xml(xml_content)
        for item in rss_items:
            if post_count >= 3:
                break
            link = item['link']
            title = item['title']
            pub_date = item.get('pub_date', '')
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = ""
            try:
                description = get_detail(link)
            except Exception as e:
                util.error("request: {} error: {}".format(link, str(e)))
                if "Access Restricted" in str(e):
                    break
                continue
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "stocktitan",
                        "pub_date": pub_date if pub_date else util.current_time_string(),
                        "source": "stocktitan",
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

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.stocktitan.net/rss")
