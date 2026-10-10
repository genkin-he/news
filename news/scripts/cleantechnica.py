# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点在 Cloudflare 后面。原实现用裸 urllib，且带着一串 2025-09-17 签发的硬编码 cookie
# （含 cf_clearance / __cf_bm）：这类 cookie 绑定签发时的 IP 与 UA，过期后 Cloudflare
# 直接 403，CI 上自 10-05 起每轮必现。改用 curl_cffi 做指纹伪装，整链被拒时在预算内
# 再轮一遍——Cloudflare 的质询按请求概率下发，换一次请求也可能放行（同 apnews）。
IMPERSONATE_PROFILES = ("chrome120", "safari18_0", "firefox133", "safari17_0")
REQUEST_ROUNDS = 2

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

base_url = "https://cleantechnica.com"
list_url = "https://cleantechnica.com/category/clean-transport-2/electric-vehicles/"
# 列表页被质询时退回同一分类的 RSS：路径不同，Cloudflare 规则常按路径区分，
# 且只需要从中拿标题与链接，正文仍去详情页取
feed_url = list_url + "feed/"
base_path = "./news/data/cleantechnica/list.json"
current_links = []

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 5

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
    for profile in IMPERSONATE_PROFILES * REQUEST_ROUNDS:
        if response is not None and util.out_of_time():
            util.info("out of time, stop retrying: {}".format(url))
            break
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
            )
        )
    util.error(
        "request url: {}, all impersonate attempts rejected, last error: {}".format(
            url, response.status_code if response is not None else "no response"
        )
    )
    return response


def list_from_page():
    response = request(list_url)
    if response is None or response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "lxml")
    return [
        ((a.get("href") or "").strip(), a.get_text(strip=True))
        for a in soup.select("article h2 a")
    ]


def list_from_feed():
    response = request(feed_url)
    if response is None or response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "xml")
    items = []
    for item in soup.find_all("item"):
        link_node, title_node = item.find("link"), item.find("title")
        if link_node is None or title_node is None:
            continue
        items.append((link_node.get_text(strip=True), title_node.get_text(strip=True)))
    return items


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        response = request(link)
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response is None or response.status_code != 200:
        return ""

    body = BeautifulSoup(response.text, "lxml")
    soup = body.select_one(".cm-entry-summary")
    if not soup:
        util.info("content not found, skipped: {}".format(link))
        return ""
    ad_elements = soup.select("hr, div, figure")
    # 移除这些元素
    for element in ad_elements:
        element.decompose()
    # 删除包含 "Support CleanTechnica's work through" 的 em 元素
    em_elements = soup.find_all("em")
    for em in em_elements:
        if em.get_text() and "Support CleanTechnica's work through" in em.get_text():
            util.info("删除 em 元素：{}".format(em.get_text()[:50]))
            em.decompose()
            break
    return str(soup).strip()


def run():
    data = util.history_posts(base_path)
    _articles = data["articles"]
    _links = data["links"]
    new_articles = []

    try:
        items = list_from_page()
        if items is None:
            util.info("list page unavailable, falling back to feed")
            items = list_from_feed()
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if items is None:
        util.log_action_error("request url: {}, list page and feed both rejected".format(list_url))
        return
    util.info("items length: {}".format(len(items)))

    for link, title in items:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        if not link or not title:
            continue
        if link in ",".join(_links):
            util.info("exists link: {}".format(link))
            continue
        description = get_detail(link)
        if description != "":
            new_articles.append(
                {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "vietnamnews",
                    "kind": 1,
                    "language": "zh-HK",
                }
            )

    # 原实现 insert(index, ...) 会把新稿插到列表中间，改为整体拼在旧列表前面
    if new_articles:
        util.write_json_to_file((new_articles + _articles)[:KEEP_POSTS], base_path)


if __name__ == "__main__":
    util.execute_with_timeout(run)
