# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点（TechForge 旗下）在 Cloudflare 后面，用 curl_cffi 走指纹伪装；被拒时逐档降级，
# 命中的档位在本轮内缓存复用。chrome120 对 feed 与 REST 均 403，故放到末位。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "chrome120")

headers = {
    "accept": "application/json, */*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}

base_url = "https://www.cloudcomputing-news.net"
# 2026-09-28 起 /feed/、/feed、?feed=rss2 一律 200 返回首页 HTML（RSS 被关），
# 旧实现因此报 "no item parsed"。WP REST 仍开放，且 content.rendered 就是全文
# （与原先详情页 elementor 容器里的正文一致），不必再逐篇回详情页。
# 作者只给了用户 id（/users 接口 404），名字从 yoast_head_json.author 取。
list_url = (
    base_url
    + "/wp-json/wp/v2/posts?per_page=10"
    + "&_fields=id,link,date_gmt,title,content,yoast_head_json.author"
)
filename = "./news/data/cloudcomputing_news/list.json"

STRIP_SELECTOR = "figure,script,style,iframe,noscript,img,picture,source,form"
# 正文末尾固定三段推广：See also 链接、Cyber Security & Cloud Expo 的招商、
# "powered by TechForge Media"。段落数多于这个数量时才剥，避免把短稿清空。
TRAILING_PARAGRAPHS = 3

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 6
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


def parse_pub_date(value):
    """REST 的 date_gmt 形如 2026-09-25T09:00:00，为 UTC 且不带时区后缀"""
    try:
        parsed = datetime.strptime(value or "", "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return util.current_time_string()
    return (
        parsed.replace(tzinfo=timezone.utc)
        .astimezone(LOCAL_TZ)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def parse_content(html, link):
    """content.rendered 即全文：剥图与脚本，去掉末尾推广段"""
    soup = BeautifulSoup(html or "", "lxml")
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()

    paragraphs = soup.select("p")
    if len(paragraphs) > TRAILING_PARAGRAPHS:
        for paragraph in paragraphs[-TRAILING_PARAGRAPHS:]:
            paragraph.decompose()
    else:
        util.info(
            "only {} paragraphs, trailing promos kept: {}".format(
                len(paragraphs), link
            )
        )

    if not soup.get_text(strip=True):
        util.info("content empty after strip, skipped: {}".format(link))
        return ""
    util.info("content: {} chars".format(len(soup.get_text(" ", strip=True))))
    # 给的是 HTML 片段，lxml 会补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


def parse_posts(payload):
    if not isinstance(payload, list):
        return []
    items = []
    for post in payload:
        title = BeautifulSoup(
            (post.get("title") or {}).get("rendered") or "", "lxml"
        ).get_text(strip=True)
        link = (post.get("link") or "").strip()
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "content": (post.get("content") or {}).get("rendered") or "",
                "author": ((post.get("yoast_head_json") or {}).get("author") or "")
                .strip(),
                "pub_date": parse_pub_date(post.get("date_gmt")),
            }
        )
    return items


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(list_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(list_url, repr(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(list_url, status))
        return

    try:
        entries = parse_posts(response.json())
    except ValueError as e:
        util.log_action_error("request url: {}, bad json: {}".format(list_url, e))
        return
    if not entries:
        util.log_action_error("request url: {}, no item parsed".format(list_url))
        return
    util.info("{} items".format(len(entries)))

    for item in entries:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue
        description = parse_content(item["content"], item["link"])
        if not description:
            continue
        links.add(item["link"])
        new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "author": item["author"] or "cloudcomputing_news",
                "pub_date": item["pub_date"],
                "source": "cloudcomputing_news",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
