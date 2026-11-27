# -*- coding: UTF-8 -*-
import urllib.request
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}

filename = "./news/data/yahoo/list_us.json"
util = SpiderUtil()

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底：1 次 RSS + 最多 2 次
# 站外详情页，单次超时须按剩余预算收敛，否则慢站点一个就吃掉整轮。
REQUEST_TIMEOUT = 4


def get_detail(link):
    """取不到正文时返回空串，由调用方跳过该条

    RSS 里的条目大多指向站外媒体（politico、reuters 等），其中一部分对 CI 出口直接
    403。原实现让异常一路抛到 execute_with_timeout，一条外链被拒就中断整轮采集，
    后面还没抓的条目全部丢失——日志里的 "<HTTPError 403: 'Forbidden'>" 即此。
    """
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.info("skipped: {} error: {}".format(link, repr(e)))
        return ["", ""]
    if response.status == 200:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")
        soup = BeautifulSoup(html, "lxml")
        art = soup.find("article")
        if not art:
            return ["", ""]
        for ad in art.find_all("div", class_=lambda c: c and "ad-container" in c):
            parent = ad.parent
            while parent and parent != art:
                if parent.get("class") and "bg-accent/2" in " ".join(parent.get("class", [])):
                    parent.decompose()
                    break
                parent = parent.parent
            else:
                ad.decompose()
        time_tag = soup.find("time")
        pub_date = time_tag.get("datetime", "") if time_tag else ""
        return [str(art), pub_date]
    else:
        util.error("request: {} error: {}".format(link, response))
        return ["", ""]


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    request = urllib.request.Request(
        "https://news.yahoo.com/rss/topstories",
        None,
        headers,
    )
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(repr(e)))
        return
    if response.status == 200:
        body = response.read()
        tree = etree.fromstring(body)
        channel = tree.find("channel")
        items = channel.findall("item") if channel is not None else []

        inserted = 0
        for item in items:
            if inserted >= 2 or util.out_of_time():
                break
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()

            if not link or not title:
                continue
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break

            detail = get_detail(link)
            description = detail[0]
            if not description:
                continue

            pub_date = util.current_time_string()
            if detail[1]:
                try:
                    dt = datetime.fromisoformat(detail[1].replace("Z", "+00:00"))
                    pub_date = dt.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass

            insert = True
            inserted += 1
            articles.insert(0, {
                "title": title,
                "description": description,
                "link": link,
                "pub_date": pub_date,
                "source": "yahoo_us",
                "kind": 1,
                "language": "en",
            })

        if articles and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run)
