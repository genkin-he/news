# -*- coding: UTF-8 -*-
import re
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 托管质询后面（cf-mitigated: challenge）。已验证 chrome131、
# chrome136、safari17_0、safari18_0、firefox133、edge101 六个档位表现一致，与 TLS
# 指纹无关，故单档位不做降级。同类站点（ambcrypto、invezz）在 GitHub Actions 的出口
# IP 上均可通过质询，本采集器预期同样可用；被拦时日志会带上 cf-mitigated。
IMPERSONATE = "chrome131"

# curl_cffi 的 chrome 档位默认不发扩展 client hints，而 Cloudflare 的规则会看它们的完整性。
# 以下取自真实浏览器请求（document 导航 + 完整 hints），均不绑定会话，可安全固化。
# 刻意不含 cf_clearance（绑定 IP 与 UA、数小时即过期）与 if-none-match / if-modified-since
# （ETag 命中会返回 304 空响应体，反而使抓取失败）。
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"152.0.7977.65"',
    "sec-ch-ua-full-version-list": '"Chromium";v="152.0.7977.65", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.65"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}

# 六个分类 feed 每个各取前 MAX_PER_CATEGORY 条。同一篇文章可能同时出现在多个分类里，
# 已入库的链接集合在整轮内共享，因此跨 feed 也不会重复收录。
# feed 只用来拿链接、标题与发布时间；正文回详情页取 .posts__single__content div.content。
CATEGORIES = (
    "automobile",
    "utility-vehicles",
    "energy-infrastructure",
    "battery-fuel-cell",
    "fleets",
    "short-circuit",
)
FEED_TEMPLATE = "https://www.electrive.com/category/{}/feed/"

filename = "./news/data/electrive/list.json"
util = SpiderUtil()

MAX_PER_CATEGORY = 2
KEEP_POSTS = 20
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

# CI 实测：feed 可通行，但文章详情页返回 403 且 cf-mitigated 为空、响应体是 Cloudflare
# 的 1xxx 错误页模板（<!--[if lt IE 7]> <html class="no-js ie6 oldie"）——与本地遇到的
# "Just a moment..." 质询是两种不同拦截。错误码用于区分成因：
# 1020 防火墙规则、1015 限流、1010 浏览器完整性检查。
CF_ERROR_CODE = re.compile(r"error code:\s*(\d+)|Error\s+(\d{4})", re.IGNORECASE)


def cf_error_code(text):
    matched = CF_ERROR_CODE.search(text or "")
    if not matched:
        return None
    return matched.group(1) or matched.group(2)


_session = None


def get_session():
    """六个 feed 共用一个 session，Cloudflare 下发的 cookie 才能复用"""
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
    return _session


def request(url):
    response = get_session().get(url, timeout=TIMEOUT)
    if response.status_code != 200:
        util.error(
            "request url: {}, error: {}, cf-mitigated: {}, cf-code: {}, "
            "body: {}".format(
                url,
                response.status_code,
                response.headers.get("cf-mitigated"),
                cf_error_code(response.text),
                " ".join((response.text or "").split())[:160],
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


CONTENT_SELECTOR = ".posts__single__content div.content"
# 目标容器自身是 div.content，剥离时只清它内部的 div（配图说明、广告位、相关阅读等）
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript"


def parse_feed_description(item):
    """详情页被拦时的兜底：feed 自带的 content:encoded（全文）或 description（摘要）"""
    for tag in ("encoded", "description"):
        node = item.find(tag)
        if node is None:
            continue
        raw = node.get_text()
        if not raw or not raw.strip():
            continue
        soup = BeautifulSoup(raw, "lxml")
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        if not soup.get_text(strip=True):
            continue
        # RSS 里给的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
        return (soup.body.decode_contents() if soup.body else str(soup)).strip()
    return ""


def get_detail(link):
    """feed 里的 description 只是摘要，正文回详情页取 .posts__single__content div.content"""
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        if not soup.get_text(strip=True):
            util.error("article content empty: {}".format(link))
            return ""
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


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
            {
                "title": title,
                "link": link,
                "pub_date": parse_pub_date(item),
                "feed_description": parse_feed_description(item),
            }
        )
    return items


def collect(category, links, new_articles):
    url = FEED_TEMPLATE.format(category)
    try:
        response = request(url)
    except Exception as e:
        util.error("request {} exception: {}".format(url, str(e)))
        return

    if response.status_code != 200:
        return

    rss_items = parse_rss_xml(response.text)
    if not rss_items:
        util.error("request url: {}, no rss item parsed".format(url))
        return

    util.info("{}: {} items".format(category, len(rss_items)))
    for item in rss_items[:MAX_PER_CATEGORY]:
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description = get_detail(item["link"])
        source = "detail"
        if description == "":
            # CI 上详情页会被 Cloudflare 规则拦掉，退回 feed 自带正文，
            # 否则整个采集器颗粒无收。日志标明来源便于判断正文质量。
            description = item["feed_description"]
            source = "feed"
        if description == "":
            continue
        util.info("content from {}: {} chars".format(source, len(description)))

        links.add(item["link"])
        new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "electrive",
                "kind": 1,
                "language": "en",
            }
        )


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    for category in CATEGORIES:
        collect(category, links, new_articles)

    if not new_articles:
        return

    # 六个 feed 各自有序，合并后按发布时间倒序，保证最新的排在最前
    new_articles.sort(key=lambda item: item["pub_date"], reverse=True)
    util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
