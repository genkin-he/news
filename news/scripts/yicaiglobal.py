# -*- coding: UTF-8 -*-
import hashlib
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.yicaiglobal.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}

base_url = "https://www.yicaiglobal.com"
api_url = "https://www.yicaiglobal.com/api/getNewsList"
filename = "./news/data/yicaiglobal/list.json"

# 403 的响应体是 {"status":-1,"msg":"invalid sign"}——不是反爬拦截，而是接口新增了请求签名。
# 所有 impersonate 档位（chrome131/136、safari17_0/18_0、firefox133、edge101）表现完全一致，
# 因为这是应用层校验而非指纹判定；裸 requests 带上正确签名即可通行，无需 curl_cffi。
#
# 算法取自站点 /js/common.js（模块内 a 为密钥、o 为需签名的路径前缀）：
#   calcSign(params) = sha1( "_".join(按 key 排序后的各 value + SALT) )
#   其中 key 与 value 均转小写、剔除 sign 本身，并在签名前注入 timestamp（秒）
# 该模块导出 {sha1, calcSign, buildSignParams}，由 axios 拦截器与 window.fetch 包装统一注入。
SIGN_SALT = "ycglobal_ajax_2026"

CATEGORY_IDS = (3, 4, 5)
PAGE_SIZE = 10
MAX_PER_CATEGORY = 2
KEEP_POSTS = 20
TIMEOUT = 15

CONTENT_SELECTOR = "#news-body"
# 实测正文只有 p / strong / span，无 div 与 script；以下为防御性剥离
STRIP_SELECTOR = "script,style,iframe,noscript"


def calc_sign(params):
    normalized = {
        key.lower(): str(value).lower()
        for key, value in params.items()
        if key != "sign"
    }
    values = [normalized[key] for key in sorted(normalized)]
    values.append(SIGN_SALT)
    return hashlib.sha1("_".join(values).encode()).hexdigest()


def signed_get(url, params):
    """/api 前缀的接口必须带 timestamp 与 sign，否则返回 403 invalid sign"""
    payload = dict(params)
    payload["timestamp"] = int(time.time())
    payload["sign"] = calc_sign(payload)
    return requests.get(url, params=payload, headers=headers, timeout=TIMEOUT)


def parse_pub_date(news_item):
    """接口的 LocalTime 已是北京时间且格式与仓库一致，无需再做时区换算"""
    value = (news_item.get("LocalTime") or "").strip()
    if len(value) == 19:
        return value
    value = (news_item.get("Time") or "").strip()
    if len(value) == 19 and "T" in value:
        return value.replace("T", " ")
    return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers, timeout=TIMEOUT)
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""

        # 记录剥离前后的文本量，正文若因剥离而缩水可从日志直接看出
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


def collect_category(category_id, links, new_articles):
    try:
        response = signed_get(
            api_url,
            {"type": "", "id": category_id, "pagesize": PAGE_SIZE, "page": 1},
        )
    except Exception as e:
        util.error("request category {} exception: {}".format(category_id, str(e)))
        return

    if response.status_code != 200:
        util.error(
            "request url: {}, id: {}, error: {}, body: {}".format(
                api_url, category_id, response.status_code, (response.text or "")[:80]
            )
        )
        return

    try:
        result = response.json()
    except ValueError as e:
        util.error("category {} bad payload: {}".format(category_id, str(e)))
        return

    news_list = result if isinstance(result, list) else result.get("data", [])
    util.info("category {}: {} items".format(category_id, len(news_list)))

    taken = 0
    for news_item in news_list:
        if taken >= MAX_PER_CATEGORY:
            break
        title = (news_item.get("NewsTitle") or "").strip()
        news_url = (news_item.get("NewsUrl") or "").strip()
        if not title or not news_url:
            continue

        full_url = urljoin(base_url, news_url)
        taken += 1
        if full_url in links:
            util.info("exists link: {}".format(full_url))
            continue

        description = get_detail(full_url)
        if not description:
            continue

        links.add(full_url)
        new_articles.append(
            {
                "title": title,
                "description": description,
                "link": full_url,
                "pub_date": parse_pub_date(news_item),
                "source": "yicaiglobal",
                "kind": 1,
                "language": "en",
            }
        )


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    for category_id in CATEGORY_IDS:
        collect_category(category_id, links, new_articles)

    if not new_articles:
        return

    # 三个栏目各自有序，合并后按发布时间倒序，保证最新的排最前
    new_articles.sort(key=lambda item: item["pub_date"], reverse=True)
    util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
