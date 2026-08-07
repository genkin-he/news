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


util = SpiderUtil()


def _proxies():
    proxy = util.get_random_proxy()
    url = proxy.get("http") if proxy else None
    return {"http": url, "https": url} if url else {}


def _safe_get(url, **kwargs):
    try:
        return _get_session().get(url, proxies=_proxies(), verify=False, **kwargs)
    except Exception:
        return _get_session().get(url, verify=False, **kwargs)


base_url = "https://www.reporterosdelsur.com/"
filename = "./news/data/reporterosdelsur/list.json"


def get_detail(link):
    util.info(f"link: {link}")
    try:
        response = _safe_get(link, timeout=30)
    except Exception as e:
        util.error(f"request: {link} error: {e}")
        return ""
    if response.status_code == 200:
        lxml = BeautifulSoup(response.text, "lxml")
        soup = lxml.select_one(".entry-content")
        if not soup:
            return ""
        for element in soup.select("div[itemprop='video']"):
            element.decompose()
        return str(soup).strip()
    else:
        util.error(f"request: {link} error: {response.status_code}")
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        response = _get_session().get("https://lisboatv.pt", timeout=30)
    except Exception as e:
        util.log_action_error(f"request error: {e}")
        return
    if response.status_code == 200:
        lxml = BeautifulSoup(response.text, "lxml")
        posts = lxml.select("article")
        for index, post in enumerate(posts):
            if index >= 3:
                break
            h2a = post.select_one("h2 > a")
            if not h2a:
                continue
            title = h2a.text.strip()
            link = h2a["href"].strip()
            image = post.select_one("figure img")
            image = image["src"].strip() if image else ""
            if link in ",".join(links):
                util.info(f"exists link: {link}")
                break
            if util.contains_language(title):
                continue
            description = get_detail(link)
            if description:
                insert = True
                articles.insert(0, {
                    "title": title,
                    "description": description,
                    "image": image,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "reporterosdelsur",
                    "kind": 1,
                    "language": "en",
                })
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")


if __name__ == "__main__":
    util.execute_with_timeout(run)
