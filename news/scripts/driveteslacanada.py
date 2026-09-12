# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 托管质询后面，按 TLS/JA3 指纹判定：
# Chrome / Edge 档位一律 403 + cf-mitigated: challenge，Safari / Firefox 档位可直接 200。
# 不再自带 User-Agent 与 sec-ch-ua，交给 curl_cffi 下发与所选档位自洽的整套请求头，
# 避免出现「Safari 指纹配 Chrome UA」这种自相矛盾的组合。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari15_5")

base_url = "https://driveteslacanada.ca/"
filename = "./news/data/driveteslacanada/list.json"
util = SpiderUtil(notify=False)

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；被质询时自动降级到下一个档位"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile)
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            _session = session
            return response
        util.error(
            "request url: {}, impersonate: {}, error: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
            )
        )
    return response


def parse_pub_date(node):
    """列表项自带 <time datetime="2026-09-03T14:36:35-07:00">，比抓取时刻准确"""
    time_node = node.select_one("time")
    value = time_node.get("datetime") if time_node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            datetime.fromisoformat(value)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except ValueError:
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(".entry-content")
        if soup is None:
            util.error("request: {} error: no .entry-content".format(link))
            return ""

        for element in soup.select("style,script,.code-block,.twitter-tweet"):
            element.decompose()
        return str(soup).strip()
    except Exception as e:
        util.error("request failed: {}".format(str(e)))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    try:
        response = request(link)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(link, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request error: {}".format(status))
        return

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select(".entry-content article")
    if not items:
        util.log_action_error("request {}, no article node parsed".format(link))
        return

    for item in items[:MAX_POSTS]:
        title_node = item.select_one(".entry-title > a")
        if title_node is None or not title_node.get("href"):
            continue
        article_link = title_node["href"].strip()
        if article_link in _links:
            util.info("exists link: {}".format(article_link))
            continue

        description = get_detail(article_link)
        if description == "":
            continue

        _links.add(article_link)
        _new_articles.append(
            {
                "title": title_node.text.strip(),
                "description": description,
                "link": article_link,
                "pub_date": parse_pub_date(item),
                "source": "driveteslacanada",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
