# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 后面，规则只盯 Chromium 系指纹：chrome131 返回 403，而 safari18_0
# 返回 200。原实现用 urllib.request（无指纹伪装）并携带一串 2024-12 签发、早已过期的
# cf_clearance——该 cookie 绑定签发时的 IP 与 UA，硬编码对 CI 毫无作用；且 urllib 在
# 403 时抛 HTTPError 而非返回响应，故 CI 表现为 <HTTPError 403: 'Forbidden'> 后无产出。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari15_5")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

base_url = "https://simplywall.st"
list_url = "https://simplywall.st/news"
filename = "./news/data/simplywall/list.json"
util = SpiderUtil()

LIST_SELECTOR = 'div[data-cy-id="list-article"] > article'
CONTENT_SELECTOR = 'div[data-cy-id="article-content"]'
# 正文内的 div 是 Simply Wall St 的估值推广块（实测剥离损失 351 字符），应剥；
# 但个别文章可能整体嵌在 div 内，故留一个保守范围作为兜底
STRIP_SELECTOR = "figure,div,script,style,iframe,noscript"
STRIP_SELECTOR_SAFE = "figure,script,style,iframe,noscript"

MAX_POSTS = 5
KEEP_POSTS = 20
TIMEOUT = 15

_session = None


def request(url):
    """命中的 impersonate 档位缓存复用；被质询时自动降级到下一个档位"""
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
            "request url: {}, impersonate: {}, error: {}, cf-mitigated: {}".format(
                url, profile, response.status_code, response.headers.get("cf-mitigated")
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
        stripped = BeautifulSoup(str(soup), "lxml").select_one(CONTENT_SELECTOR)
        for element in stripped.select(STRIP_SELECTOR):
            element.decompose()
        after = len(stripped.get_text(" ", strip=True))

        if after == 0:
            # 该文正文整体嵌在 div 内，退回保守范围重剥一次
            stripped = soup
            for element in stripped.select(STRIP_SELECTOR_SAFE):
                element.decompose()
            after = len(stripped.get_text(" ", strip=True))
            if after == 0:
                util.error("article content empty after strip: {}".format(link))
                return ""
            util.info(
                "content text: {} -> {} chars (safe strip)".format(before, after)
            )
        else:
            util.info("content text: {} -> {} chars".format(before, after))

        # 末段是 Simply Wall St 的持仓免责声明，原实现即已剔除；此处补上越界保护
        paragraphs = stripped.find_all("p")
        if paragraphs:
            paragraphs[-1].decompose()
        return str(stripped).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

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
    nodes = soup.select(LIST_SELECTOR)
    if not nodes:
        util.log_action_error(
            "request url: {}, no article node parsed".format(list_url)
        )
        return
    util.info("{} nodes".format(len(nodes)))

    for node in nodes:
        if len(new_articles) >= MAX_POSTS:
            break

        link_el = node.select_one("a[href]")
        title_el = node.select_one("h2")
        if link_el is None or title_el is None or not link_el.get("href"):
            continue
        link = link_el["href"].strip()
        if link.startswith("/"):
            link = base_url + link
        title = title_el.get_text().strip()
        if not title:
            continue
        if link in links:
            util.info("exists link: {}".format(link))
            continue

        description = get_detail(link)
        if description == "":
            continue

        links.add(link)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "pub_date": util.current_time_string(),
                "link": link,
                "source": "simplywall",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
