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


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request, timeout=5)
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
    response = urllib.request.urlopen(request, timeout=10)
    if response.status == 200:
        body = response.read()
        tree = etree.fromstring(body)
        channel = tree.find("channel")
        items = channel.findall("item") if channel is not None else []

        inserted = 0
        for item in items:
            if inserted >= 2:
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
