# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# CI 上固定 403，但同一地址从本机出口与 Anthropic 抓取器的美国数据中心 IP 均返回 200，
# 故不是国家级地理封锁；本机侧再测「无 cookie / 带过期 session / 带损坏 session /
# 带 if-none-match」四种组合也全部 200，无法在本地复现，说明规则只作用于 GitHub Actions
# 所在 IP 段。此前曾把 403 归因于 util.get_random_proxy()——移除代理后耗时确实从超时降到
# 0.5 秒，但 403 仍在，那个归因是错的。
#
# 目前唯一可操作的方向是请求形态：原实现用裸 requests，无任何 TLS 指纹伪装，而该 IP 段
# 上可能套了更严的规则。改用 curl_cffi 并在非 200 时记录响应体，下一轮 CI 即可判定
# 是指纹问题还是纯 IP 段封锁。
IMPERSONATE_PROFILES = ("chrome131", "safari18_0", "firefox133")

# 原 headers 里有两处隐患，一并清掉：
#   if-none-match 写死了 ETag，一旦命中服务端会返回 304 空响应体，脚本直接判为失败；
#   cookie 里带 2025-10-31 签发的 Rails 会话（_statementdog_session_v2 等），早已失效。
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-TW,zh;q=0.9,en;q=0.8",
    "referer": "https://statementdog.com/news",
    "upgrade-insecure-requests": "1",
}

base_url = "https://www.statementdog.com/"
list_url = "https://statementdog.com/news/latest"
filename = "./news/data/statementdog/list.json"
util = SpiderUtil(notify=False)

LIST_SELECTOR = ".statementdog-news-list-item-link"
CONTENT_SELECTOR = ".main-news-content"
STRIP_SELECTOR = (
    ".main-news-title,.main-news-time,.main-news-tag-section,"
    ".main-news-editors,script,style,iframe,noscript,picture"
)

MAX_POSTS = 5
KEEP_POSTS = 10
TIMEOUT = 15

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
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            _session = session
            return response
        util.error(
            "request url: {}, impersonate: {}, error: {}, server: {}, body: {}".format(
                url,
                profile,
                response.status_code,
                response.headers.get("server"),
                " ".join((response.text or "").split())[:140],
            )
        )
    return response


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200:
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article content empty after strip: {}".format(link))
            return ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])
    _new_articles = []

    try:
        response = request(list_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(list_url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(list_url, status))
        return

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select(LIST_SELECTOR)
    if not items:
        util.log_action_error(
            "request url: {}, no article node parsed".format(list_url)
        )
        return
    # 该选择器会命中重复节点（实测 20 篇文章对应 40 个节点，桌面与移动两套版式），
    # 先在列表层按 href 保序去重，避免同一篇在日志里重复出现
    candidates = []
    seen = set()
    for item in items:
        link = (item.get("href") or "").strip()
        title = (item.get("data-title") or "").strip()
        if not link or not title or link in seen:
            continue
        seen.add(link)
        candidates.append((link, title))
    util.info("{} nodes, {} unique".format(len(items), len(candidates)))

    for link, title in candidates:
        if len(_new_articles) >= MAX_POSTS:
            break
        if link in _links:
            util.info("exists link: {}".format(link))
            continue

        description = get_detail(link)
        if description == "":
            continue

        _links.add(link)
        _new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "pub_date": util.current_time_string(),
                "source": "statementdog",
                "kind": 1,
                "language": "zh-HK",
            }
        )

    if _new_articles:
        util.write_json_to_file((_new_articles + _articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
