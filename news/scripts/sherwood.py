# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 原实现用 urllib.request：其一无 timeout，其二在 429 / 4xx 时抛 HTTPError 而非返回
# 响应，导致 `if response.status == 200` 的 else 分支永远走不到。站点对高频来源会回
# 429（正文仅 "Too Many Requests"），必须能识别而不是以异常收场，故改用 curl_cffi。
IMPERSONATE = "chrome136"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en;q=0.9",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
}

base_url = "https://sherwood.news"
list_url = "https://sherwood.news/markets/"
filename = "./news/data/sherwood/list.json"
util = SpiderUtil()

# 列表页有两个结构完全不同的区块，各取前 N 条：
#   FEATURED: 节点自身就是 <a>，内部没有嵌套 <a>，标题在 span.hover-highlight，
#             发布时间在 div[title]（形如 8/17/26 11:51AM），正文是唯一的 <p>
#   LATEST  : 节点是 <div>，文章链接是内部第一个包含 <h2> 的 <a>，另有若干
#             inline-stock / 外链 <a> 属于正文，无发布时间
FEATURED_SELECTOR = "a.css-naqlws"
LATEST_SELECTOR = "div.css-12fbs19"
MAX_PER_SECTION = 2

KEEP_POSTS = 20
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))


def _eastern_tz():
    """站点是美国财经媒体，div[title] 的时间无时区；"4:02PM" 对应美股收盘，
    据此按美东时间解析。zoneinfo 不可用时退回 EDT 固定偏移。"""
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/New_York")
    except Exception:
        return timezone(timedelta(hours=-4))


EASTERN_TZ = _eastern_tz()


def parse_pub_date(value):
    if not value:
        return util.current_time_string()
    try:
        parsed = datetime.strptime(value.strip(), "%m/%d/%y %I:%M%p")
    except ValueError:
        return util.current_time_string()
    return (
        parsed.replace(tzinfo=EASTERN_TZ)
        .astimezone(LOCAL_TZ)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def collect_body(node):
    """两个区块的正文都在 <p> 里。原实现「删掉所有 div」只对 LATEST 成立——
    FEATURED 的内容全部包在 div 中，那样做会留下一个空的 <a>。"""
    parts = []
    for paragraph in node.select("p"):
        for element in paragraph.select("script,style,iframe,noscript"):
            element.decompose()
        if paragraph.get_text(strip=True):
            parts.append(str(paragraph).strip())
    return "".join(parts)


def extract_featured(node):
    """节点自身即 <a>；内部无嵌套 <a>，故原 node.select("a")[0] 会 IndexError"""
    href = (node.get("href") or "").strip()
    title_node = node.select_one("span.hover-highlight")
    if not href or title_node is None:
        return None
    date_node = node.select_one("div[title]")
    return {
        "link": urljoin(base_url, href),
        "title": title_node.get_text(strip=True),
        "description": collect_body(node),
        "pub_date": parse_pub_date(date_node.get("title") if date_node else ""),
    }


def extract_latest(node):
    """文章链接是内部第一个包含 <h2> 的 <a>，其余 <a> 属于正文，不能当成文章链接"""
    link_node = node.select_one("a:has(h2)")
    if link_node is None:
        return None
    href = (link_node.get("href") or "").strip()
    title_node = link_node.select_one("h2")
    if not href or title_node is None:
        return None
    body_holder = BeautifulSoup(str(node), "lxml")
    for element in body_holder.select("a:has(h2)"):
        element.decompose()
    return {
        "link": urljoin(base_url, href),
        "title": title_node.get_text(strip=True),
        "description": collect_body(body_holder),
        "pub_date": util.current_time_string(),
    }


def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
        response = session.get(url, timeout=TIMEOUT)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return

    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}, body: {}".format(
                url, response.status_code, (response.text or "").strip()[:80]
            )
        )
        return

    soup = BeautifulSoup(response.text, "lxml")
    sections = (
        ("featured", soup.select(FEATURED_SELECTOR), extract_featured),
        ("latest", soup.select(LATEST_SELECTOR), extract_latest),
    )

    for name, nodes, extract in sections:
        util.info("{} nodes: {}".format(name, len(nodes)))
        if not nodes:
            util.error("no node matched for section: {}".format(name))
            continue

        taken = 0
        for node in nodes:
            if taken >= MAX_PER_SECTION:
                break
            item = extract(node)
            if item is None or not item["title"] or not item["description"]:
                continue
            taken += 1
            if item["link"] in links:
                util.info("exists link: {}".format(item["link"]))
                continue
            util.info("link: {}".format(item["link"]))
            links.add(item["link"])
            new_articles.append(
                {
                    "title": item["title"],
                    "description": item["description"],
                    "pub_date": item["pub_date"],
                    "link": item["link"],
                    "source": "sherwood",
                    "kind": 1,
                    "language": "en",
                }
            )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, list_url)
