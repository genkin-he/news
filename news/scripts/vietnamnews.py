# -*- coding: UTF-8 -*-
from urllib.parse import quote
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

IMPERSONATE = "chrome120"
_session = None

util = SpiderUtil()


def _get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


def _proxies():
    proxy = util.get_random_proxy()
    url = proxy.get("http") if proxy else None
    return {"http": url, "https": url} if url else {}


def _safe_get(url, **kwargs):
    try:
        return _get_session().get(url, proxies=_proxies(), verify=False, **kwargs)
    except Exception:
        return _get_session().get(url, verify=False, **kwargs)


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
}

cookie = util.get_env_variable("vietnamnews", "")
if cookie:
    headers["cookie"] = cookie

base_url = "https://vietnamnews.vn"
base_path = "./news/data/vietnamnews/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = _safe_get(quote(link, safe="/:"), headers=headers, timeout=30)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one("#abody")
        if not soup:
            return ""
        for element in soup.select("div, table, .picture"):
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run(link):
    data = util.history_posts(base_path)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = _safe_get(link, headers=headers, timeout=30)
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".l-content article h2 a")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 3:
                break
            a = items[index]
            link = a["href"].strip()
            title = a.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(index, {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "vietnamnews",
                    "kind": 1,
                    "language": "zh-HK",
                })
        if len(_articles) > 0 and insert:
            if len(_articles) > 20:
                _articles = _articles[:20]
            util.write_json_to_file(_articles, base_path)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run, "https://vietnamnews.vn/economy-business-beat")
