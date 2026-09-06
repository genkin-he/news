# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# https://dailyhodl.com/news/ 的 HTML 页面被 Cloudflare 拦（403），/wp-json 亦然；
# 而站点主 RSS /feed/ 放行。实测 chrome131 / chrome136 / safari18_0 / firefox133 /
# edge101 对 /feed/ 全部返回 200，与指纹无关，故单档位不做降级。
# 注意 /news/feed/ 是该页面的**评论** feed（channel title 为 "Comments on: News"，0 条），
# 不可用；栏目对应关系改由主 feed 的 category 标签实现。
IMPERSONATE = "chrome131"

base_url = "https://dailyhodl.com/feed/"
filename = "./news/data/dailyhodl/list.json"
util = SpiderUtil(notify=False)

# 只收 category 含 News 的条目，对应 /news/ 栏目；这样也天然排除了
# Press Releases / sponsored 那类推广条目（实测 10 条中有 2 条）。
REQUIRED_CATEGORY = "news"

# content:encoded 内含前置大图与 <div class="hideinamp"> 免责声明套话
# （实测每篇固定约 539 字符），均需剥离
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript,img"

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))


def request(url):
    session = curl_requests.Session(impersonate=IMPERSONATE)
    response = session.get(url, timeout=TIMEOUT)
    if response.status_code != 200:
        util.error(
            "request url: {}, error: {}, cf-mitigated: {}, body: {}".format(
                url,
                response.status_code,
                response.headers.get("cf-mitigated"),
                " ".join((response.text or "").split())[:120],
            )
        )
    return response


def parse_pub_date(item):
    """RSS pubDate 为 RFC 822，交给 email.utils 解析以容忍 +0000 与 GMT 等写法差异"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            parsedate_to_datetime(value)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except (TypeError, ValueError):
        return util.current_time_string()


def has_required_category(item):
    for node in item.find_all("category"):
        if node.get_text(strip=True).lower() == REQUIRED_CATEGORY:
            return True
    return False


def parse_description(item):
    """只取 content:encoded（全文）；description 是更短的版本，不作回落"""
    node = item.find("encoded")
    if node is None:
        return ""
    raw = node.get_text()
    if not raw or not raw.strip():
        return ""
    soup = BeautifulSoup(raw, "lxml")
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()
    if not soup.get_text(strip=True):
        return ""
    # RSS 里给的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


def parse_rss_xml(xml_content):
    soup = BeautifulSoup(xml_content, "xml")
    items = []
    for item in soup.find_all("item"):
        title_node = item.find("title")
        link_node = item.find("link")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = link_node.get_text(strip=True)
        if not title or not link:
            continue
        if not has_required_category(item):
            util.info("skip non-news: {}".format(title[:60]))
            continue
        description = parse_description(item)
        if not description:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "pub_date": parse_pub_date(item),
            }
        )
    return items


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

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(link, response.status_code)
        )
        return

    rss_items = parse_rss_xml(response.text)
    if not rss_items:
        util.log_action_error("request url: {}, no rss item parsed".format(link))
        return

    for item in rss_items:
        if len(_new_articles) >= MAX_POSTS:
            break
        if item["link"] in _links:
            util.info("exists link: {}".format(item["link"]))
            continue
        util.info("link: {}".format(item["link"]))
        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": item["description"],
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "dailyhodl",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
