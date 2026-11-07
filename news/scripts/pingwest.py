# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

IMPERSONATE = "chrome120"
_session = None

def _get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session

filename = "./news/data/pingwest/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info(f"link: {link}")
    current_links.append(link)
    try:
        response = _get_session().get(link, timeout=30)
    except Exception as e:
        util.error(f"request: {link} error: {e}")
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        soup = body.find(class_="article-style")
        if not soup:
            return ""
        for element in soup.select(".ad"):
            element.decompose()
        return str(soup).strip()
    else:
        util.error(f"request: {link} error: {response.status_code}")
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = _get_session().get("https://www.pingwest.com/", timeout=30)
    except Exception as e:
        util.log_action_error(f"request error: {e}")
        return
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        seen = set()
        items = []
        for a in soup.select('a[href*="/a/"]'):
            href = a.get("href", "")
            title = a.text.strip()
            if title and href not in seen:
                seen.add(href)
                items.append((href, title))

        for index, (href, title) in enumerate(items):
            if index > 2:
                break
            link = f"https:{href}" if href.startswith("//") else href
            if link in ",".join(_links):
                util.info(f"exists link: {link}")
                break
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(index, {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "pingwest",
                    "kind": 1,
                    "language": "zh-CN",
                })

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")


if __name__ == "__main__":
    util.execute_with_timeout(run)
