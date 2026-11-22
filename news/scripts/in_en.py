# -*- coding: UTF-8 -*-
import re
from datetime import timedelta

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点对境外来源走严格路径：首次请求回 403，响应体是
#   <script> window.location.href ="/corp/"; </script>
# 同时在该响应里 Set-Cookie 下发会话 cookie，要求客户端带上它重新请求同一地址，
# 第二次才给 200。国内出口首请求即 200，不触发这个握手。
# curl_cffi 的 Session 会自动保存 cookie，因此在同一 session 内原地重试即可完成握手；
# 整个脚本共用一个 session，握手结果才能复用到后续的详情页请求上。
# CI 日志已证实 chrome131 / safari18_0 / firefox133 三档行为完全一致，说明与 TLS
# 指纹无关，故不做档位降级——那只会让被拒时的请求数翻三倍。
IMPERSONATE = "chrome131"
MAX_ATTEMPTS = 3

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
}

base_url = "https://newenergy.in-en.com"
list_url = "https://newenergy.in-en.com/corp/"
filename = "./news/data/in_en/list.json"
util = SpiderUtil()

MAX_POSTS = 3
KEEP_POSTS = 20
TIMEOUT = 15

RELATIVE_TIME = re.compile(r"^(\d+)\s*(分钟|小时|天)前$")
ABSOLUTE_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

_session = None


def fetch(session, url):
    """同一 session 内原地重试，让 403 响应下发的会话 cookie 在下一次请求时带上"""
    response = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response
        util.error(
            "request url: {}, attempt: {}/{}, error: {}, cookies: {}, body: {}".format(
                url,
                attempt,
                MAX_ATTEMPTS,
                response.status_code,
                sorted(session.cookies.keys()),
                (response.text or "").replace("\n", " ")[:120],
            )
        )
    return response


def request(url):
    """整个脚本复用一个 session，握手拿到的 cookie 才能用在后续的详情页请求上"""
    global _session

    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
    return fetch(_session, url)


def parse_pub_date(item):
    """列表时间有三种写法：N分钟前 / N小时前 / YYYY-MM-DD"""
    node = item.select_one(".prompt i")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()

    matched = RELATIVE_TIME.match(value)
    if matched:
        amount = int(matched.group(1))
        unit = matched.group(2)
        delta = {
            "分钟": timedelta(minutes=amount),
            "小时": timedelta(hours=amount),
            "天": timedelta(days=amount),
        }[unit]
        return (util.current_time() - delta).strftime("%Y-%m-%d %H:%M:%S")

    matched = ABSOLUTE_DATE.match(value)
    if matched:
        return "{} 00:00:00".format(value)

    return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one("div#article")
        if soup is None:
            util.error("request: {} error: no div#article".format(link))
            return ""

        for element in soup.select("img,script,style"):
            element.decompose()
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
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
        util.log_action_error("request url: {}, error: {}".format(link, status))
        return

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select("ul.infoList li")
    util.info("items length: {}".format(len(items)))
    if not items:
        util.log_action_error("request url: {}, no article node parsed".format(link))
        return

    for item in items:
        if len(_new_articles) >= MAX_POSTS:
            break

        title_node = item.select_one(".listTxt h5 a")
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
                "source": "in_en",
                "kind": 1,
                "language": "zh-CN",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, list_url)
