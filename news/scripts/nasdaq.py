# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from curl_cffi import requests
from util.spider_util import SpiderUtil

# 原先用 urllib + 写死的 Akamai cookie（bm_mi 等），cookie 过期后请求直接挂起到被强杀；
# 2026-11-19 改为 curl_cffi 模拟浏览器指纹，不再依赖 cookie
base_url = "https://www.nasdaq.com"
list_url = base_url + "/api/news/topic/latestnews?offset=0&limit=10"
filename = "./news/data/nasdaq/list.json"
util = SpiderUtil()

IMPERSONATE = "chrome"
KEEP_POSTS = 10
MAX_NEW_PER_RUN = 3
NOISE_SELECTOR = ".ads__inline, .body__disclaimerscript, .video__inline, .taboola-placeholder, script"


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, impersonate=IMPERSONATE, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("detail error: {}, link: {}".format(response.status_code, link))
        return ""
    content = BeautifulSoup(response.text, "lxml").select_one(".body__content")
    if content is None:
        util.log_action_error(".body__content not found: {}".format(link))
        return ""
    for element in content.select(NOISE_SELECTOR):
        element.decompose()
    return str(content)


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    response = requests.get(list_url, impersonate=IMPERSONATE, timeout=util.request_timeout(5))
    if response.status_code != 200:
        util.log_action_error("list error: {}".format(response.status_code))
        return

    for post in response.json()["data"]["rows"][:MAX_NEW_PER_RUN]:
        if util.out_of_time():
            break
        link = base_url + post["url"]
        if link in links:
            util.info("exists link: {}".format(link))
            break
        description = get_detail(link)
        if not description:
            continue
        links.add(link)
        new_articles.append(
            {
                "id": post["id"],
                "author": post.get("publisher", ""),
                "title": post["title"],
                "description": description,
                "link": link,
                "pub_date": util.current_time_string(),
                "source": "nasdaq",
                "kind": 1,
                "language": "en",
            }
        )

    util.info("new articles: {}".format(len(new_articles)))
    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    # 2026-11-19 仍停用：列表接口可用，但文章页被 Akamai 403（试过 chrome/safari/firefox/edge 指纹），
    # RSS 与 Feedly 也只有 100~300 字摘要，拿不到正文。站点放开后取消注释即可。
    # util.execute_with_timeout(run)
    util.info("detail pages blocked by Akamai (403)")
