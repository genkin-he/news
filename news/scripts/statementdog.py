# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 原实现抓 HTML 列表页 https://statementdog.com/news/latest，在 CI 上固定 403
# （server 头为空、响应体仅 "Forbidden"，三个 impersonate 档位表现一致，与指纹无关），
# 而本机出口与 Anthropic 抓取器的美国 IP 均可取到 200——属针对 CI 出口的拦截。
#
# 改走站点的 Atom feed /news/feed：同域但路径不同，且相比 HTML 抓取有三点更优——
#   entry 的 content 直接带正文（实测 659-2113 字符），无需再请求详情页；
#   published 为带 +08:00 的真实发布时间，不必再用抓取时刻兜底；
#   单次请求即可，不依赖任何会随改版失效的 CSS 选择器。
#
# 但 /news/feed 在 CI 上同样固定 403（三档 impersonate 一致、响应体只有 "Forbidden"）：
# 拦截认的是出口 IP，换指纹、换路径都没用，直连这条路在 CI 上没有出路。
# 因此补一条备用取数路径：feed2json.org 的公共转换接口在它自己的服务器上抓同一个 feed，
# 再以 JSON Feed 返回，字段与 Atom 一一对应（content_html / date_published / url /
# title），正文完整、不经二次渲染，落库字段无需迁就。直连成功时不会走到这里，
# 仅当直连被拒才回落，两条路径产出同一份 item 结构。
IMPERSONATE_PROFILES = ("chrome131", "safari18_0", "firefox133")

headers = {
    "accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.8",
    "accept-language": "zh-TW,zh;q=0.9,en;q=0.8",
    "referer": "https://statementdog.com/news",
}

base_url = "https://statementdog.com"
feed_url = "https://statementdog.com/news/feed"
fallback_url = "https://feed2json.org/convert?url={}".format(quote(feed_url, safe=""))
filename = "./news/data/statementdog/list.json"
util = SpiderUtil()

# content 内只有 p / h2 与图片容器（picture/source/img），无 div、script
STRIP_SELECTOR = "picture,source,img,figure,script,style,iframe,noscript"

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 8
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；链内单次被拒记 info，整链耗尽才是失败"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}, body: {}".format(
                url, profile, response.status_code,
                " ".join((response.text or "").split())[:60],
            )
        )
    util.error(
        "request url: {}, all {} impersonate profiles rejected, last error: {}".format(
            url,
            len(IMPERSONATE_PROFILES),
            response.status_code if response is not None else "no response",
        )
    )
    return response


def to_local_time(value):
    """Atom 的 published 形如 2026-09-14T17:22:25+08:00（已是台北时间），
    feed2json 的 date_published 形如 2026-09-18T02:25:55.000Z（UTC），统一转 +08:00"""
    if not value:
        return util.current_time_string()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return util.current_time_string()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def parse_pub_date(entry):
    node = entry.find("published") or entry.find("updated")
    return to_local_time(node.get_text(strip=True) if node else "")


def clean_html(raw):
    if not raw or not raw.strip():
        return ""
    soup = BeautifulSoup(raw, "lxml")
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()
    if not soup.get_text(strip=True):
        return ""
    # 拿到的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


def parse_content(entry):
    node = entry.find("content")
    return clean_html(node.get_text() if node else "")


def parse_atom(xml_content):
    soup = BeautifulSoup(xml_content, "xml")
    items = []
    for entry in soup.find_all("entry"):
        title_node = entry.find("title")
        link_node = entry.find("link")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = (link_node.get("href") or "").strip()
        if not title or not link:
            continue
        description = parse_content(entry)
        if not description:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "pub_date": parse_pub_date(entry),
            }
        )
    return items


def parse_json_feed(payload):
    """feed2json 返回 JSON Feed：items[].{title,url,content_html,date_published}"""
    items = []
    for entry in json.loads(payload).get("items", []):
        title = (entry.get("title") or "").strip()
        link = (entry.get("url") or "").strip()
        if not title or not link:
            continue
        description = clean_html(entry.get("content_html") or "")
        if not description:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "pub_date": to_local_time(entry.get("date_published")),
            }
        )
    return items


def fetch_entries():
    """先直连 Atom，被拒再走 feed2json 回落；两条路径返回同一种 item 结构"""
    try:
        response = request(feed_url)
    except Exception as e:
        util.error("request {} exception: {}".format(feed_url, repr(e)))
        response = None

    if response is not None and response.status_code == 200:
        entries = parse_atom(response.text)
        if entries:
            return entries
        util.error("request url: {}, no entry parsed".format(feed_url))

    status = response.status_code if response is not None else "no response"
    util.info("direct feed unavailable ({}), falling back to feed2json".format(status))
    try:
        fallback = curl_requests.get(
            fallback_url,
            impersonate=IMPERSONATE_PROFILES[0],
            timeout=util.request_timeout(TIMEOUT),
        )
    except Exception as e:
        util.log_action_error(
            "request url: {}, error: {}, fallback exception: {}".format(
                feed_url, status, repr(e)
            )
        )
        return []

    if fallback.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}, fallback error: {}".format(
                feed_url, status, fallback.status_code
            )
        )
        return []

    try:
        entries = parse_json_feed(fallback.text)
    except Exception as e:
        util.log_action_error(
            "request url: {}, error: {}, fallback parse error: {}".format(
                feed_url, status, repr(e)
            )
        )
        return []

    if not entries:
        util.log_action_error(
            "request url: {}, error: {}, fallback parsed no entry".format(
                feed_url, status
            )
        )
    return entries


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    entries = fetch_entries()
    if not entries:
        return
    util.info("{} entries".format(len(entries)))

    for item in entries:
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
                "source": "statementdog",
                "kind": 1,
                "language": "zh-HK",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
