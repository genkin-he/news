# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

IMPERSONATE = "chrome131"
util = SpiderUtil()

base_url = "https://vietnamnews.vn"
base_path = "./news/data/vietnamnews/list.json"

# 原实现取 https://vietnamnews.vn/economy-business-beat（连字符），而历史入库的文章链接
# 都是 https://vietnamnews.vn/economy/business-beat/{id}/{slug}.html（斜杠）——站点已把
# 栏目路径改成斜杠形式，旧地址仍返回 200 但页面里没有文章，因此 CI 日志表现为
# "items length: 0" 且不报错。此处按新旧两个地址依次尝试。
LIST_URLS = (
    "https://vietnamnews.vn/economy/business-beat",
    "https://vietnamnews.vn/economy-business-beat",
)

# 不再依赖 .l-content article h2 a 这类随主题变动的 class，改按文章 URL 模式提取：
# 该模式由历史入库数据反推得出，主题改版不会影响它。
ARTICLE_PATTERN = re.compile(
    r"^https?://vietnamnews\.vn/economy/business-beat/\d+/[^/]+\.html$"
)

CONTENT_SELECTOR = "#abody"
# 沿用原实现意图：正文里的 div / table / .picture 是版式与配图容器
STRIP_SELECTOR = "div,table,.picture,script,style,iframe,noscript"

MAX_POSTS = 4
KEEP_POSTS = 20
TIMEOUT = 30
LOCAL_TZ = timezone(timedelta(hours=8))

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
}

cookie = util.get_env_variable("vietnamnews", "")
if cookie:
    headers["cookie"] = cookie

_session = None


def get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
    return _session


def request(url):
    return get_session().get(url, timeout=TIMEOUT, verify=False)


def collect_links(html):
    """按 URL 模式收集文章链接，保序去重"""
    soup = BeautifulSoup(html, "lxml")
    found = []
    seen = set()
    for anchor in soup.select("a[href]"):
        link = urljoin(base_url, (anchor.get("href") or "").strip())
        if not ARTICLE_PATTERN.match(link) or link in seen:
            continue
        title = anchor.get_text(strip=True) or (anchor.get("title") or "").strip()
        if not title:
            continue
        seen.add(link)
        found.append({"link": link, "title": title})
    return found, soup


def describe_page(soup, html):
    """列表页取不到文章时，把足以定位新结构的线索打进日志，避免又一次静默失败"""
    title = soup.title.get_text(strip=True) if soup.title else None
    counts = {
        sel: len(soup.select(sel))
        for sel in (
            "a[href]",
            "article",
            "article h2 a",
            "h2 a",
            "h3 a",
            ".l-content article h2 a",
        )
    }
    samples = [
        (a.get("href") or "")[:70]
        for a in soup.select('a[href*="business-beat"]')[:5]
    ]
    util.error(
        "no article link matched, len={}, title={}, counts={}, business-beat hrefs={}".format(
            len(html), title, counts, samples
        )
    )


def parse_pub_date(soup):
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
        response = request(quote(link, safe="/:"))
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return "", ""

    if response.status_code != 200:
        util.error("request: {} error: {}".format(link, response.status_code))
        return "", ""

    body = BeautifulSoup(response.text, "lxml")
    soup = body.select_one(CONTENT_SELECTOR)
    if soup is None:
        util.error("article content not found: {}".format(link))
        return "", ""

    # 记录剥离前后的文本量：剥离范围含 div 与 table，若正文段落被包在其中会大幅缩水，
    # 从日志即可发现，而不是等到入库后才察觉正文残缺。
    before = len(soup.get_text(" ", strip=True))
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()
    after = len(soup.get_text(" ", strip=True))
    if after == 0:
        util.error("article content empty after strip: {}".format(link))
        return "", ""
    util.info("content text: {} -> {} chars".format(before, after))
    return str(soup).strip(), parse_pub_date(body)


def run():
    data = util.history_posts(base_path)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    items = []
    for list_url in LIST_URLS:
        try:
            response = request(list_url)
        except Exception as e:
            util.error("request {} exception: {}".format(list_url, str(e)))
            continue

        if response.status_code != 200:
            util.error(
                "request url: {}, error: {}".format(list_url, response.status_code)
            )
            continue

        items, soup = collect_links(response.text)
        util.info("{}: {} items".format(list_url, len(items)))
        if items:
            break
        describe_page(soup, response.text)

    if not items:
        util.log_action_error("no article link matched on any list url")
        return

    for item in items:
        if len(_new_articles) >= MAX_POSTS:
            break
        if item["link"] in _links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description, pub_date = get_detail(item["link"])
        if description == "":
            continue

        _links.add(item["link"])
        _new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": pub_date,
                "source": "vietnamnews",
                "kind": 1,
                "language": "en",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], base_path)


if __name__ == "__main__":
    util.execute_with_timeout(run)
