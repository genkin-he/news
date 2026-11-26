# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 2026-01 底站点改版：首页变成创业公司目录，原选择器 h2.post-title a 一条都匹配不到，
# 脚本静默零产出近 10 个月（只在请求异常时才告警）。现改为：
#   - 列表：全站 RSS /feed/（50 条，只有摘要），按 pubDate 倒序；
#   - 正文：详情页 div.article-content-prose。正文由 React 渲染，段落嵌在多层 div 里，
#     原来「剥掉所有 div」的做法会把正文一起剥掉，故改为按文档顺序抽取正文块再拼接。
#     少数文章只有一张 Visual TL;DR 交互图、没有成段正文，抽不到正文块即跳过。
# 另去掉了 util.get_random_proxy()：代理池已全部失效。
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}
FEED_URL = "https://www.startuphub.ai/feed/"
filename = "./news/data/startuphub/list.json"
util = SpiderUtil()

CONTENT_SELECTOR = "div.article-content-prose"
BLOCK_TAGS = ["p", "h2", "h3", "h4", "ul", "ol", "blockquote", "table"]
MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 5


def extract_blocks(container):
    """按文档顺序取最外层的正文块，嵌在其它正文块里的（如 li 里的 p）随外层一起带出"""
    blocks = []
    for element in container.find_all(BLOCK_TAGS):
        if element.find_parent(BLOCK_TAGS) is not None:
            continue
        for junk in element.select("script,style,input,button,svg"):
            junk.decompose()
        if element.get_text(strip=True):
            blocks.append(str(element))
    return "\n".join(blocks)


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
    container = BeautifulSoup(response.text, "lxml").select_one(CONTENT_SELECTOR)
    if container is None:
        # 正文容器整体消失说明又改版了，进告警通道
        util.log_action_error("article content not found: {}".format(link))
        return ""
    description = extract_blocks(container)
    if not description:
        util.info("no prose blocks (visual-only article), skipped: {}".format(link))
    return description


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])

    try:
        response = requests.get(
            FEED_URL, headers=headers, timeout=util.request_timeout(TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(FEED_URL, str(e)))
        return
    if response.status_code != 200:
        util.log_action_error(
            "request {} error: {}".format(FEED_URL, response.status_code)
        )
        return

    items = BeautifulSoup(response.content, "xml").find_all("item")
    if not items:
        util.log_action_error("request {}, no rss item parsed".format(FEED_URL))
        return

    new_articles = []
    for item in items:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        link = item.link.get_text(strip=True) if item.link else ""
        title = item.title.get_text(strip=True) if item.title else ""
        if not link or not title:
            continue
        if link in links:
            util.info("exists link: {}".format(link))
            break
        description = get_detail(link)
        if not description:
            continue
        links.add(link)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
                "pub_date": util.current_time_string(),
                "source": "startuphub",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
