# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点在 Cloudflare 后面。原实现用裸 urllib，且带着一串 2024-08 签发的硬编码 cookie
# （含 cf_clearance / XSRF-TOKEN / 会话）：这类 cookie 绑定签发时的 IP 与 UA，过期后
# 站点会把请求打回登录/校验页再跳回原地址，urllib 不持久化 Set-Cookie，于是每跳一次
# 都重来一遍，最终抛 "HTTPError 302: ... would lead to an infinite loop"（CI 每轮必现）。
# 改用 curl_cffi：指纹伪装过 Cloudflare，且 Session 自己持有 cookie jar，
# 跳转链里发下来的 cookie 会被带上，重定向能正常收敛。
IMPERSONATE_PROFILES = ("chrome120", "safari18_0", "firefox133")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

base_url = "https://stockinvest.us"
filename = "./news/data/stockinvest/list.json"
current_links = []

MAX_POSTS = 2
KEEP_POSTS = 10
TIMEOUT = 5
RUN_TIMEOUT = 6  # 本脚本连跑两轮，而 CI 的 gtimeout 只给整个进程 15 秒

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
        if response is not None and util.out_of_time():
            util.info("out of time, stop retrying: {}".format(url))
            break
        session = curl_requests.Session(impersonate=profile, headers=headers)
        response = session.get(url, timeout=util.request_timeout(TIMEOUT))
        if response.status_code == 200:
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}".format(
                url, profile, response.status_code
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
        status = response.status_code if response is not None else "no response"
        util.error("request: {} error: {}".format(link, status))
        return ""

    body = BeautifulSoup(response.text, "lxml")
    # 正文容器缺失时跳过该条，原实现直接取 [0] 会抛 IndexError 并中断整轮
    nodes = body.select(".digest-article-content")
    if not nodes:
        util.info("content not found, skipped: {}".format(link))
        return ""
    soup = nodes[0]

    ad_elements = soup.select(".caas-da")
    # 移除这些元素
    for element in ad_elements:
        element.decompose()
    return str(soup).strip()


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = request(link)
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if response is not None and response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".digest-grid > div > .btn-header")
        for index in range(len(items)):
            if index >= MAX_POSTS or util.out_of_time():
                break
            anchors = items[index].select(".font-size-16 > a")
            if not anchors:
                continue
            link = anchors[0]["href"].strip()
            title = anchors[0].text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                break
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "stockinvest",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(_articles) > 0 and insert:
            util.write_json_to_file(_articles[:KEEP_POSTS], filename)
    else:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(link, status))


if __name__ == "__main__":
    util.execute_with_timeout(
        run,
        "https://stockinvest.us/digest/category/latest-stock-market-news?page=1",
        timeout=RUN_TIMEOUT,
    )
    util.execute_with_timeout(
        run,
        "https://stockinvest.us/digest/category/analysis-and-ideas",
        timeout=RUN_TIMEOUT,
    )
