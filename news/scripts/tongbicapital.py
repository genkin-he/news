# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}

# 使用 curl_cffi 模拟 Chrome 以绕过 TLS/JA3 指纹校验
IMPERSONATE = "chrome120"

base_url = "https://tongbicapital.com/api/rss"
filename = "./news/data/tongbicapital/list.json"
util = SpiderUtil()

_curl_session = None


def _get_session():
    global _curl_session
    if _curl_session is None:
        _curl_session = curl_requests.Session(impersonate=IMPERSONATE, headers=headers)
    return _curl_session


def _describe_block(response):
    """源站在阿里云 ESA/ENS 边缘后面，拒绝时的判据都在响应头与响应体里"""
    marks = []
    for key in ("server", "via", "eagleid", "x-site-cache-status"):
        value = response.headers.get(key)
        if value:
            marks.append("{}={}".format(key, value))
    body = (response.text or "").replace("\n", " ")[:200]
    return "headers[{}] body[{}]".format(", ".join(marks), body)


def element_text(item, tag):
    elem = item.find(tag)
    if elem is None or not elem.text:
        return ""
    return elem.text.strip()


def parse_pub_date(pub_date):
    if not pub_date:
        return util.current_time_string()
    try:
        return util.parse_time(pub_date, "%a, %d %b %Y %H:%M:%S GMT")
    except Exception as e:
        util.error("parse pub_date: {}, error: {}".format(pub_date, str(e)))
        return util.current_time_string()


def parse_rss_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall(".//item"):
            title = element_text(item, "title")
            link = element_text(item, "link")
            content = element_text(item, "content")
            if not title or not link or not content:
                continue
            items.append(
                {
                    "title": title,
                    "link": link,
                    "content": content,
                    "pub_date": parse_pub_date(element_text(item, "pubDate")),
                }
            )
        return items
    except ET.ParseError as e:
        util.error("XML parse error: {}".format(str(e)))
        return []


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    _new_articles = []

    try:
        response = _get_session().get(link, timeout=30)
        if response.status_code != 200:
            util.log_action_error(
                "request url: {}, error: {}, {}".format(
                    link, response.status_code, _describe_block(response)
                )
            )
            return

        response.encoding = "utf-8"
        # 触发限流时源站会以 HTTP 200 返回 {"code":429,...}，必须显式识别
        if '"code":429' in response.text:
            util.log_action_error("request url: {}, rate limited".format(link))
            return

        rss_items = parse_rss_xml(response.text)
        if not rss_items:
            util.log_action_error("request url: {}, no rss item parsed".format(link))
            return
        for index in range(len(rss_items)):
            if index > 9:
                break
            item = rss_items[index]
            if item["link"] in _links:
                util.info("exists link: {}".format(item["link"]))
                continue
            _new_articles.append(
                {
                    "title": item["title"],
                    "description": item["content"],
                    "link": item["link"],
                    "pub_date": item["pub_date"],
                    "source": "tongbicapital",
                    "kind": 1,
                    "language": "zh-CN",
                }
            )

        if len(_new_articles) > 0:
            _articles = (_new_articles + _articles)[:20]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run, base_url)
