# -*- coding: UTF-8 -*-
#
# 【已停用】2026-11-20 起移入 disabled/，不再随 CI 执行（news.yml 只跑 news/scripts/*.py）。
#
# 停用原因：www.stcn.com 在 GitHub Actions 美国 runner 上自 2026-11-17 18:00（北京时间）起每轮读超时，
#   同期 egsea 同样开始 connect 超时；本机（香港出口）访问正常、原脚本可正常入库，
#   代码无问题，是 CI 境外出口到该站的网络不通。util/proxy_pool.json 的代理均已失效。
#
# 恢复方法：CI 能访问该站（或接入可用的境内代理）后，把本文件移回 news/scripts/。
#
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 券商中国（证券时报网 stcn.com 的微信栏目）。原先由 news-crawler（prod-hk-ack-1）直连采集，
# 2026-10-22 起该集群出口到 www.stcn.com 的连接超时（同属证券时报的 egsea.com 同期被封），
# 其他出口可正常访问，故迁到这里。
base_url = "https://www.stcn.com"
list_url = base_url + "/article/wx/qszg.html"
filename = "./news/data/quanshangcn/list.json"
util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": base_url + "/",
}

# 正文里会内嵌 echarts 的 <script>，需剥掉
STRIP_SELECTOR = "script,style,iframe,noscript"
# .detail-info 形如「来源：证券时报网 作者：胡飞军 2026-11-17 17:54 字号 …」，时间为北京时间
TIME_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
LOCAL_TZ = timezone(timedelta(hours=8))
# 预算 10 秒：1 次列表 + 最多 MAX_POSTS 次详情
REQUEST_TIMEOUT = (2, 3)
MAX_POSTS = 4
KEEP_POSTS = 20


def get_detail(link):
    """返回 (正文 HTML, 发布时间戳)，失败时正文为空串"""
    util.info("link: {}".format(link))
    try:
        response = requests.get(
            link, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
        if response.status_code != 200:
            util.error("request: {} error: {}".format(link, response.status_code))
            return "", 0
        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(".detail-content")
        if soup is None:
            util.error("article content not found: {}".format(link))
            return "", 0
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        if soup.get_text(strip=True) == "" and soup.find("img") is None:
            util.error("article content empty: {}".format(link))
            return "", 0
        pub_time = 0
        info = body.select_one(".detail-info")
        matched = TIME_PATTERN.search(info.get_text(" ", strip=True)) if info else None
        if matched:
            pub_time = int(
                datetime.strptime(matched.group(1), "%Y-%m-%d %H:%M")
                .replace(tzinfo=LOCAL_TZ)
                .timestamp()
            )
        return str(soup).strip(), pub_time
    except Exception as e:
        util.error("request: {} exception: {}".format(link, str(e)))
        return "", 0


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = set(data["links"])

    try:
        response = requests.get(
            list_url, headers=headers, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(list_url, str(e)))
        return
    if response.status_code != 200:
        util.log_action_error(
            "request url: {}, error: {}".format(list_url, response.status_code)
        )
        return
    items = BeautifulSoup(response.text, "lxml").select(".infinite-list li")
    if not items:
        util.log_action_error("request url: {}, no article node parsed".format(list_url))
        return

    _new_articles = []
    for item in items:
        if len(_new_articles) >= MAX_POSTS or util.out_of_time():
            break
        anchor = item.select_one(".tt a")
        if anchor is None:
            continue
        href = (anchor.get("href") or "").strip()
        title = anchor.get_text(strip=True)
        if not href or not title:
            continue
        link = href if href.startswith("http") else base_url + href
        if link in _links:
            continue
        description, pub_time = get_detail(link)
        if description == "":
            continue
        _links.add(link)
        summary = item.select_one(".text")
        cover = item.select_one(".side img")
        _new_articles.append(
            {
                "title": title,
                "description": description,
                "summary": summary.get_text(strip=True) if summary else "",
                "link": link,
                "image": (cover.get("src") or "").strip() if cover else "",
                "pub_time": pub_time,
                "pub_date": util.convert_utc_to_local(pub_time)
                if pub_time
                else util.current_time_string(),
                "source": "quanshangcn",
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
