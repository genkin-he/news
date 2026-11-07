# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 原实现请求 sg.news.yahoo.com/fp_ms/_rcv/remote?ctrl=StreamGrid&...&rid=05tvio9j77jvq
# 这个私有端点已 404（去掉写死的 rid 亦然），且 Yahoo 已重构 SG 新闻前端——首页中
# _rcv/remote、StreamGrid、caas/content、wafer 等旧标记全部为 0 次出现，因此 CI 表现为
# <HTTPError 404: 'Not Found'>。改走官方 RSS，稳定且不依赖私有接口。
base_url = "https://sg.news.yahoo.com/rss"
filename = "./news/data/yahoo/list_sg.json"

headers = {
    "accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "accept-language": "en-SG,en;q=0.9",
}

IMPERSONATE = "chrome131"

# RSS 只给 title / link / pubDate / source / guid，content 与 credit 均为空，正文须回详情页。
# 文章分布在 sg.news.yahoo.com 与 sg.finance.yahoo.com / finance.yahoo.com 上。
CONTENT_SELECTORS = (".body", "article")
# 实测 .body 内有 19 个 div 承载正文段落，剥 div 会把 8664 字符正文清成 0，故不剥 div
STRIP_SELECTOR = "figure,script,style,iframe,noscript,button"

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
    return _session


def request(url):
    return get_session().get(url, timeout=TIMEOUT, allow_redirects=True)


def parse_pub_date(item):
    """RSS 的 pubDate 形如 2026-09-06T23:30:00Z"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except ValueError:
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return "", ""

        body = BeautifulSoup(response.text, "lxml")
        soup = None
        for selector in CONTENT_SELECTORS:
            soup = body.select_one(selector)
            if soup is not None:
                break
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""

        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return "", ""
        util.info("content text: {} -> {} chars".format(before, after))

        first = soup.find("p")
        summary = first.get_text(" ", strip=True)[:200] if first else ""
        return str(soup).strip(), summary
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return "", ""


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
        guid_node = item.find("guid")
        source_node = item.find("source")
        items.append(
            {
                "id": guid_node.get_text(strip=True) if guid_node else "",
                "title": title,
                "link": link,
                "author": source_node.get_text(strip=True) if source_node else "",
                "pub_date": parse_pub_date(item),
            }
        )
    return items


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(base_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(base_url, str(e)))
        return

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(base_url, response.status_code)
        )
        return

    rss_items = parse_rss_xml(response.text)
    if not rss_items:
        util.log_action_error("request url: {}, no rss item parsed".format(base_url))
        return

    for item in rss_items:
        if len(new_articles) >= MAX_POSTS:
            break
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description, summary = get_detail(item["link"])
        if description == "":
            continue

        links.add(item["link"])
        new_articles.append(
            {
                "id": item["id"],
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "summary": summary,
                "author": item["author"],
                "pub_date": item["pub_date"],
                "source": "yahoo_sg",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
