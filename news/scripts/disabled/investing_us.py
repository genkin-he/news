# -*- coding: UTF-8 -*-
#
# 【已停用】2026-11-20 起移入 disabled/，不再随 CI 执行（news.yml 只跑 news/scripts/*.py）。
#
# 停用原因：investing.com 全部 RSS（news.rss、news_*.rss 等）的 item 已不再带 description，本脚本只用
#   RSS 描述当正文，自 2026-05-18 起一条都没入库（且没有告警，静默零产出）。详情页受 Cloudflare
#   托管质询保护，curl_cffi 各指纹一律 403 cf-mitigated: challenge，抓不到正文。
#
# 恢复方法：RSS 恢复 description，或详情页可以直接抓取后，把本文件移回 news/scripts/；
#   届时 RSS 无正文时应抓详情页并在取不到时走 log_action_error。
#
import urllib.request
from lxml import etree
from email.utils import parsedate_to_datetime
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}
base_url = "https://www.investing.com"
filename = "./news/data/investing/list_us.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    request = urllib.request.Request(
        "https://www.investing.com/rss/news.rss",
        None,
        headers,
    )
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read()
        tree = etree.fromstring(body)
        channel = tree.find("channel")
        items = channel.findall("item") if channel is not None else []

        for index, item in enumerate(items):
            if index >= 10:
                break
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            pub_date_str = item.findtext("pubDate") or ""

            if not link or not title:
                continue
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break

            pub_date = util.current_time_string()
            if pub_date_str:
                try:
                    dt = parsedate_to_datetime(pub_date_str)
                    pub_date = util.convert_utc_to_local(dt.timestamp())
                except Exception:
                    pass

            if description:
                description = "<div>{}</div>".format(description)
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                        "source": "investing_us",
                        "kind": 1,
                        "language": "en",
                    },
                )

        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
