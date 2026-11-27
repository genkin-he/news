# -*- coding: UTF-8 -*-
#
# 【已停用】2026-11-20 起移入 disabled/，不再随 CI 执行（news.yml 只跑 news/scripts/*.py）。
#
# 停用原因：站点在 GitHub Actions 美国 runner 上自 2026-11-17 18:00（北京时间）起每轮 connect 超时，
#   同期 quanshangcn（www.stcn.com）同样开始读超时；本机（香港出口）访问正常、原脚本可正常入库，
#   代码无问题，是 CI 境外出口到该站的网络不通。util/proxy_pool.json 的代理均已失效。
#
# 恢复方法：CI 能访问该站（或接入可用的境内代理）后，把本文件移回 news/scripts/。
#
import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 证券时报·e公司。原先由 news-crawler（prod-hk-ack-1）直连采集，2026-10-21 起该集群出口
# 到 www.egsea.com 的 TCP 连接被对方丢弃（SYN 无响应），其他出口可正常访问，故迁到这里。
#
# 两个栏目都是 JSON 列表接口：
# - list.html（推荐新闻）不带 X-Requested-With 也返回 JSON；
# - analysis.html（解读）不带 X-Requested-With 会返回整页 HTML，必须带上。
# pageTime 是翻页游标，传当前时间戳即取最新一页；列表项的 pageTime 即发布时间（秒）。
base_url = "https://www.egsea.com"
FEEDS = (
    base_url + "/news/list.html?page=1&pageTime={ts}&per-page=10",
    base_url + "/news/analysis.html?page=1&pageTime={ts}&per-page=10",
)
filename = "./news/data/egsea/list.json"
util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "referer": base_url + "/news/index.html",
}

# 详情页正文容器。2026-10 前后站点改版，旧的 .article-content-detail 已不存在。
CONTENT_SELECTORS = (".detail-content", ".article-content-detail")
STRIP_SELECTOR = "script,style,iframe,noscript"
# 预算 10 秒：2 次列表 + 最多 MAX_POSTS 次详情，单次请求 (connect, read) 按剩余预算收敛
REQUEST_TIMEOUT = (2, 3)
MAX_POSTS = 4
KEEP_POSTS = 20


def get_json(url):
    response = requests.get(
        url, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
    )
    if response.status_code != 200:
        raise RuntimeError("status {}".format(response.status_code))
    data = response.json()
    if str(data.get("state")) != "1" or not isinstance(data.get("data"), list):
        raise RuntimeError("unexpected payload: {}".format(response.text[:200]))
    return data["data"]


def get_detail(link):
    util.info("link: {}".format(link))
    detail_headers = dict(headers)
    detail_headers.pop("x-requested-with")
    detail_headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    try:
        response = requests.get(
            link, headers=detail_headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
        body = BeautifulSoup(response.text, "lxml")
        soup = None
        for selector in CONTENT_SELECTORS:
            soup = body.select_one(selector)
            if soup is not None:
                break
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        if soup.get_text(strip=True) == "":
            util.error("article content empty: {}".format(link))
            return ""
        return str(soup).strip()
    except Exception as e:
        util.error("request: {} exception: {}".format(link, str(e)))
        return ""


def cover_of(item):
    image = item.get("image")
    if isinstance(image, dict):
        return image.get("url") or ""
    return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])

    ts = int(util.current_time().timestamp())
    items = []
    errors = []
    for feed in FEEDS:
        url = feed.format(ts=ts)
        try:
            items.extend(get_json(url))
        except Exception as e:
            errors.append("{}: {}".format(url, str(e)))
    if not items:
        util.log_action_error("all feeds failed: {}".format("; ".join(errors)))
        return
    for error in errors:
        util.error("feed failed: {}".format(error))

    # 两个栏目会有重叠，按链接去重后由新到旧处理
    seen = set()
    candidates = []
    for item in items:
        path = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        if not path or not title or path in seen:
            continue
        seen.add(path)
        candidates.append(item)
    candidates.sort(key=lambda x: int(x.get("pageTime") or 0), reverse=True)

    _new_articles = []
    for item in candidates:
        if len(_new_articles) >= MAX_POSTS or util.out_of_time():
            break
        link = base_url + item["url"].strip()
        if link in _links:
            continue
        description = get_detail(link)
        if description == "":
            continue
        _links.add(link)
        page_time = int(item.get("pageTime") or 0)
        _new_articles.append(
            {
                "title": item["title"].strip(),
                "description": description,
                "summary": (item.get("content_full") or item.get("content") or "").strip(),
                "link": link,
                "image": cover_of(item),
                "author": (item.get("author") or "").strip(),
                "pub_time": page_time,
                "pub_date": util.convert_utc_to_local(page_time)
                if page_time
                else util.current_time_string(),
                "source": "egsea",
                "kind": 1,
                "language": "zh-CN",
            }
        )

    if _new_articles:
        # 每轮只补 MAX_POSTS 篇，补进来的可能比已有的旧，按发布时间重排后再截断
        merged = sorted(
            _new_articles + _articles,
            key=lambda x: int(x.get("pub_time") or 0),
            reverse=True,
        )
        util.write_json_to_file(merged[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
