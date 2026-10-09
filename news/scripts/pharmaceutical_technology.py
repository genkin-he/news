# -*- coding: UTF-8 -*-
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 站点全站挂在 Fastly Bot Management 的 Client Challenge 后面：首页、/news/、/feed 均返回
# 200 但正文是约 3KB 的 "Client Challenge" 页（下发 _fs_ch_st_* cookie，需执行
# /_fs-ch-*/script.js 才能放行，直接请求该脚本返回 400）。本机出口与 Anthropic 抓取器的美国
# 数据中心 IP 均被挑战，safari18_0 / firefox133 / safari15_5 / chrome131 表现一致。
# 同一出版商的 worldpharmaceuticals.net 在同一出口下正常，说明是本站单独开启的防护。
# 此前 ambcrypto / invezz 亦是「本机与美国数据中心 IP 均被拦、GitHub Actions 可通过」，
# 故照常采集；被挑战时明确识别并告警，而不是把挑战页当成空 feed 静默跳过。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "chrome131")

feed_url = "https://www.pharmaceutical-technology.com/feed/"
filename = "./news/data/pharmaceutical_technology/list.json"

# 详情页正文容器（GlobalData 模板，与 worldpharmaceuticals.net 同一套）。
# 正文 <p> 是 .main-content 的直接子节点；内层 div 为分享按钮、配图、订阅横幅、相关公司、
# 广告位等。以同模板真实页面验证：剥离内层 div 后 13 段正文全部保留（2713 -> 2344 字符）。
CONTENT_SELECTOR = ".main-content"
STRIP_SELECTOR = "div,figure,script,style,iframe,noscript"
# analyst-comment 等栏目是付费墙文章：.main-content 下没有直接的 <p>，只有
# div.pmpro_content_message（Paid Memberships Pro 插件的 "Unlock FREE Access to Premium
# Content" 推广文案）与一张注册表单，并无正文。此类页面直接跳过。
# 注意这里刻意不做「剥 div 后为空就退回不剥 div」的兜底：在本模板上那样做会把约 4.5KB 的
# 付费墙文案与表单当成正文入库（实测 china-manufacturing-biopharmas-new-drugs 即如此）。
# 本模板的免费文章正文 <p> 都是 .main-content 的直接子节点，剥 div 后为空即说明不是可读正文。
PAYWALL_SELECTOR = ".pmpro_content_message"

MAX_POSTS = 3
KEEP_POSTS = 10
TIMEOUT = 6
LOCAL_TZ = timezone(timedelta(hours=8))

_session = None


def is_challenge(response):
    return "Client Challenge" in (response.text or "")[:3000]


def request(url):
    """命中的档位缓存复用；链内单次被拒记 info，整链耗尽才记 error"""
    global _session

    if _session is not None:
        response = _session.get(url, timeout=TIMEOUT)
        if response.status_code == 200 and not is_challenge(response):
            return response
        _session = None

    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile)
        response = session.get(url, timeout=TIMEOUT)
        if response.status_code == 200 and not is_challenge(response):
            _session = session
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}{}".format(
                url,
                profile,
                response.status_code,
                " (fastly client challenge)" if is_challenge(response) else "",
            )
        )
    util.error(
        "request url: {}, all {} impersonate profiles rejected".format(
            url, len(IMPERSONATE_PROFILES)
        )
    )
    return response


def parse_pub_date(item):
    """RSS pubDate 为 RFC 822，交给 email.utils 解析以容忍 +0000 与 GMT 等写法差异"""
    node = item.find("pubDate")
    value = node.get_text(strip=True) if node else ""
    if not value:
        return util.current_time_string()
    try:
        return (
            parsedate_to_datetime(value)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    except (TypeError, ValueError):
        return util.current_time_string()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = request(link)
        if response is None or response.status_code != 200 or is_challenge(response):
            return ""

        body = BeautifulSoup(response.text, "lxml")
        soup = body.select_one(CONTENT_SELECTOR)
        if soup is None:
            util.error("article content not found: {}".format(link))
            return ""
        if soup.select_one(PAYWALL_SELECTOR) is not None:
            util.info("skip paywalled article: {}".format(link))
            return ""

        before = len(soup.get_text(" ", strip=True))
        for element in soup.select(STRIP_SELECTOR):
            element.decompose()
        after = len(soup.get_text(" ", strip=True))
        if after == 0:
            util.error("article has no free body after strip: {}".format(link))
            return ""
        util.info("content text: {} -> {} chars".format(before, after))
        return str(soup).strip()
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def parse_rss_xml(xml_content):
    soup = BeautifulSoup(xml_content, "xml")
    items = []
    for item in soup.find_all("item"):
        title_node = item.find("title")
        link_node = item.find("link")
        if title_node is None or link_node is None:
            continue
        title = title_node.get_text(strip=True)
        link = link_node.get_text(strip=True)
        if not title or not link:
            continue
        items.append({"title": title, "link": link, "pub_date": parse_pub_date(item)})
    return items


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = set(data["links"])
    new_articles = []

    try:
        response = request(feed_url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(feed_url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error("request url: {}, error: {}".format(feed_url, status))
        return

    if is_challenge(response):
        # 挑战页状态码是 200，若不专门识别，会被当成「feed 里没有 item」静默跳过
        util.log_action_error(
            "request url: {}, blocked by fastly client challenge".format(feed_url)
        )
        return

    items = parse_rss_xml(response.text)
    if not items:
        util.log_action_error("request url: {}, no rss item parsed".format(feed_url))
        return
    util.info("{} items".format(len(items)))

    for item in items:
        if len(new_articles) >= MAX_POSTS or util.out_of_time():
            break
        if item["link"] in links:
            util.info("exists link: {}".format(item["link"]))
            continue

        description = get_detail(item["link"])
        if description == "":
            continue

        links.add(item["link"])
        new_articles.append(
            {
                "title": item["title"],
                "description": description,
                "link": item["link"],
                "pub_date": item["pub_date"],
                "source": "pharmaceutical_technology",
                "kind": 1,
                "language": "en",
            }
        )

    if new_articles:
        util.write_json_to_file((new_articles + articles)[:KEEP_POSTS], filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
