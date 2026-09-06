# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点前面是 Varnish，对部分指纹有规则：chrome131 返回 403（server: Varnish），
# 而 safari18_0 / firefox133 均返回 200，故档位降级在此有实据。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "chrome136")

base_url = "https://www.worldpharmaceuticals.net/feed/"
filename = "./news/data/worldpharmaceuticals/list.json"
util = SpiderUtil()

# feed 里 description 与 content:encoded 内容完全相同，且仅 117-243 字符的一句话摘要，
# 不能当正文用，必须回详情页。
#
# 正文容器取 .article-content .main-content：正文的 13 个 <p> 全在这里。
# 注意不能剥离 div——正文段落嵌套在 grid-x / cell large-8 main-content 这些版式 div 内，
# 实测剥掉所有 div 会把 2864 字符正文清成 0。故改为按 class 精确剥离噪声块。
CONTENT_SELECTOR = ".article-content .main-content"
STRIP_SELECTOR = (
    "script,style,iframe,noscript,figure,"
    ".gdm-article-actions,.share-and-save,.gdm-article-share-button__container,"
    ".article-image,.gdm-newsletter-banner__wrapper-container,"
    ".related-company-profiles,.dmpu_adslot,.sidebar"
)

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；被拒时自动降级到下一个档位"""
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
            "request url: {}, impersonate: {}, error: {}, server: {}".format(
                url, profile, response.status_code, response.headers.get("server")
            )
        )
    return response


def parse_pub_date_from_item(item):
    """优先用 feed 的 pubDate（RFC 822），省去解析详情页"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return ""
    try:
        from email.utils import parsedate_to_datetime

        return (
            parsedate_to_datetime(value)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except (TypeError, ValueError):
        return ""


def parse_pub_date_from_page(soup):
    node = soup.select_one('meta[property="article:published_time"]')
    value = (node.get("content") or "").strip() if node else ""
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
        if response is None or response.status_code != 200:
            return "", ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", ""

        # 记录剥离前后的文本量：本站正文段落嵌在版式 div 内，剥离范围一旦扩大到 div
        # 就会把正文清空，日志可及时暴露这类回退
        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return "", ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip(), parse_pub_date_from_page(body)
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
        items.append(
            {"title": title, "link": link, "pub_date": parse_pub_date_from_item(item)}
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

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(link, status))
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

        description, page_pub_date = get_detail(item["link"])
        if description == "":
            continue

        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": item["pub_date"] or page_pub_date,
                "source": "worldpharmaceuticals",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
