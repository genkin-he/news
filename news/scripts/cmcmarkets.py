# -*- coding: UTF-8 -*-
import html
import json
import re

import requests
from util.spider_util import SpiderUtil

# 2025-12 起站点换成 Next.js（Contentful 内容）：
#   - 列表页的新闻卡片改为浏览器端请求 /api/neptune/contentful/news-articles 渲染，
#     HTML 里不再有 .article-feature，原选择器一条都匹配不到，静默零产出近一年；
#   - 详情页 HTML 里也没有正文，正文在 __NEXT_DATA__ 的 fields.articleBody，
#     是 Contentful 富文本 JSON，这里自行渲染成 HTML。
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept-language": "en-GB,en;q=0.9",
}

base_url = "https://www.cmcmarkets.com/en-gb/"
LIST_API = "https://www.cmcmarkets.com/api/neptune/contentful/news-articles"
LIST_PARAMS = {"include": "6", "locale": "en-GB", "contentfulEnv": "published"}
NEXT_DATA_PATTERN = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL
)
filename = "./news/data/cmcmarkets/list.json"
util = SpiderUtil()

MAX_POSTS = 2
KEEP_POSTS = 10
TIMEOUT = 5

BLOCK_TAGS = {
    "paragraph": "p",
    "heading-1": "h1",
    "heading-2": "h2",
    "heading-3": "h3",
    "heading-4": "h4",
    "heading-5": "h5",
    "heading-6": "h6",
    "unordered-list": "ul",
    "ordered-list": "ol",
    "list-item": "li",
    "blockquote": "blockquote",
}
MARK_TAGS = {"bold": "strong", "italic": "em", "underline": "u", "code": "code"}


def render_rich_text(node):
    """Contentful 富文本 → HTML；嵌入的图片 / 条目不保留（与其它源剥离配图的做法一致）"""
    node_type = node.get("nodeType")
    if node_type == "text":
        value = html.escape(node.get("value", ""))
        for mark in node.get("marks", []):
            tag = MARK_TAGS.get(mark.get("type"))
            if tag:
                value = "<{0}>{1}</{0}>".format(tag, value)
        return value
    inner = "".join(render_rich_text(child) for child in node.get("content", []))
    if node_type == "document":
        return inner
    if node_type == "hyperlink":
        uri = html.escape(node.get("data", {}).get("uri", ""), quote=True)
        return '<a href="{}">{}</a>'.format(uri, inner)
    if node_type == "hr":
        return "<hr/>"
    tag = BLOCK_TAGS.get(node_type)
    if tag is None:
        # embedded-asset-block / embedded-entry-* 等
        return ""
    if tag in ("p", "li") or tag.startswith("h") or tag == "blockquote":
        if not re.sub(r"<[^>]+>", "", inner).strip():
            return ""
    return "<{0}>{1}</{0}>\n".format(tag, inner)


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(
            link, headers=headers, timeout=util.request_timeout(TIMEOUT)
        )
    except Exception as e:
        util.error("request {} exception: {}".format(link, str(e)))
        return ""
    if response.status_code != 200:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""
    match = NEXT_DATA_PATTERN.search(response.text)
    try:
        body = json.loads(match.group(1))["props"]["pageProps"]["data"]["fields"][
            "articleBody"
        ]
    except (AttributeError, KeyError, TypeError, ValueError):
        util.log_action_error("articleBody not found: {}".format(link))
        return ""
    description = render_rich_text(body).strip()
    if not description:
        util.log_action_error("articleBody empty: {}".format(link))
    return description


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])

    try:
        response = requests.get(
            LIST_API,
            params=LIST_PARAMS,
            headers=headers,
            timeout=util.request_timeout(TIMEOUT),
        )
        posts = response.json().get("articles") or []
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(LIST_API, str(e)))
        return
    if response.status_code != 200 or not posts:
        util.log_action_error(
            "request {} error: {}, articles: {}".format(
                LIST_API, response.status_code, len(posts)
            )
        )
        return

    new_articles = []
    for post in posts:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        if not post or not post.get("url") or not post.get("title"):
            continue
        link = base_url + post["url"].lstrip("/")
        if link in links:
            util.info("exists link: {}".format(link))
            break
        description = get_detail(link)
        if not description:
            continue
        links.add(link)
        new_articles.append(
            {
                "title": post["title"].strip(),
                "description": description,
                "link": link,
                "pub_date": util.current_time_string(),
                "source": "cmcmarkets",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
