# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

# 站点在 Cloudflare 后面，规则只盯 Chromium 系指纹：chrome131 / chrome136 / edge101 一律
# 403 + cf-mitigated: challenge，而 safari15_5 / safari17_0 / safari18_0 / firefox133
# 均返回 200。原实现硬编码 impersonate="chrome136"，恰好是被拦的那一档，故整个采集器失效。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari15_5")

# 更关键的是：文章详情页对所有档位都被质询（分类列表页却放行），是路径级规则，换指纹无解。
# 改走 WordPress REST API——它与列表页同样放行，且 content.rendered 直接是全文，
# 一个请求即可，彻底不必碰被拦的详情页。
# category 3676 的 slug 是历史遗留的 "marketing"，实际分类名为 Markets，
# 与原 /category/marketing/ 完全对应。
# 站点 RSS 不可用：/category/marketing/feed/ 的 description 仅约 330 字符摘要，以 […] 截断。
base_url = "https://www.businesstoday.com.my"
CATEGORY_ID = 3676
list_url = (
    "https://www.businesstoday.com.my/wp-json/wp/v2/posts"
    "?per_page=10&categories={}".format(CATEGORY_ID)
)
filename = "./news/data/businesstoday/list.json"
util = SpiderUtil(notify=False)

# content.rendered 内是 p / strong / em 与外汇牌价表格（table/tr/td，属正文须保留），
# 无 div 与 script；以下选择器沿用原实现的意图，作为防御性剥离。
STRIP_SELECTOR = "script,style,iframe,noscript,div.td-a-rec,.sharedaddy,.jp-relatedposts"

MAX_POSTS = 2
KEEP_POSTS = 20
TIMEOUT = 15
LOCAL_TZ = timezone(timedelta(hours=8))

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
        session = curl_requests.Session(
            impersonate=profile, headers={"Referer": base_url}
        )
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


def parse_pub_date(value):
    """date_gmt 形如 2026-09-04T09:25:23，无时区后缀，按 UTC 处理"""
    if not value:
        return util.current_time_string()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", ""))
    except ValueError:
        return util.current_time_string()
    return (
        parsed.replace(tzinfo=timezone.utc)
        .astimezone(LOCAL_TZ)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def rendered_text(field):
    if not isinstance(field, dict):
        return ""
    return BeautifulSoup(field.get("rendered") or "", "lxml").get_text(strip=True)


def clean_content(field):
    if not isinstance(field, dict):
        return ""
    raw = field.get("rendered") or ""
    if not raw.strip():
        return ""
    soup = BeautifulSoup(raw, "lxml")
    for element in soup.select(STRIP_SELECTOR):
        element.decompose()
    if not soup.get_text(strip=True):
        return ""
    # lxml 会为 HTML 片段补出 <html><body> 外壳，只取内容部分
    return (soup.body.decode_contents() if soup.body else str(soup)).strip()


def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(url, status))
        return

    try:
        posts = json.loads(response.text)
    except ValueError as e:
        util.log_action_error("request url: {}, bad payload: {}".format(url, str(e)))
        return

    if not isinstance(posts, list) or not posts:
        util.log_action_error("request url: {}, no post in payload".format(url))
        return

    for post in posts:
        if len(new_articles) >= MAX_POSTS:
            break

        link = (post.get("link") or "").strip()
        title = rendered_text(post.get("title"))
        if not link or not title:
            continue
        if link in links:
            util.info("exists link: {}".format(link))
            continue

        description = clean_content(post.get("content"))
        if description == "":
            util.error("empty content: {}".format(link))
            continue

        util.info("link: {}".format(link))
        links.add(link)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "pub_date": parse_pub_date(post.get("date_gmt")),
                "source": "businesstoday",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run, list_url)
