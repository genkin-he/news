# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil
import xml.etree.ElementTree as ET

# 站点规则只盯 Chromium 系指纹：chrome120 / chrome131 / chrome136 对 API 一律 403，
# 而 safari17_0 / safari18_0 / firefox133 均返回 200。原实现固定 chrome120，恰是被拦的一档，
# 故 CI 表现为 "request error: 403"。改为按实测可用的档位降级。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari17_0")
_session = None


def _get_session(profile=None):
    global _session
    if _session is None:
        _session = curl_requests.Session(
            impersonate=profile or IMPERSONATE_PROFILES[0]
        )
    return _session


util = SpiderUtil()


def _safe_get(url, **kwargs):
    # 原实现先经 util.get_random_proxy() 试一次再回落直连。该代理池可用性从未验证，
    # 命中失效代理时多为超时而非报错，实测使单轮耗时从约 1 秒升至 5.9 秒；
    # 故直接直连。
    #
    # 另：news.yml 注入 seekingalpha 这个 secret 作为 cookie。/api/v3/articles 是付费内容
    # 端点，会话过期时更容易被拒——CI 上 seekalpha.py（/api/v3/news，同一 cookie）正常而
    # 本脚本固定 403，而本机不带 cookie 时该端点返回 200，故先按原样请求，若非 200 再去掉
    # cookie 重试一次；日志标明走的哪条路径。
    response = _get_session().get(url, verify=False, **kwargs)
    if response.status_code == 200 or "cookie" not in headers:
        return response

    util.error(
        "request url: {}, error: {}, retrying without the injected cookie".format(
            url, response.status_code
        )
    )
    retry_headers = {k: v for k, v in kwargs.pop("headers", headers).items()
                     if k.lower() != "cookie"}
    retry = curl_requests.Session(
        impersonate=IMPERSONATE_PROFILES[0]
    ).get(url, verify=False, headers=retry_headers, **kwargs)
    util.info("retry without cookie -> {}".format(retry.status_code))
    return retry

headers = {
    "accept": "application/json",
    "Referer": "https://seekingalpha.com/latest-articles",
}

cookie = util.get_env_variable("seekingalpha", "")
if cookie:
    headers["cookie"] = cookie

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"


def get_detail(id):
    link = f"https://seekingalpha.com/api/v3/articles/{id}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cauthor.userBioTags%2Cco_authors%2CpromotedService%2Csentiments"
    try:
        response = _safe_get(link, headers=headers, timeout=util.request_timeout(10))
    except Exception as e:
        util.error(f"get_detail error: {e}")
        return ""
    if response.status_code == 200:
        content = response.json()["data"]["attributes"]["content"]
        soup = BeautifulSoup(content, "lxml")
        for element in soup.select(".inline_ad_placeholder"):
            element.decompose()
        return str(soup).strip()
    util.info(f"detail api {id} rejected: {response.status_code}")
    return ""


LIST_URL = "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=20&page[number]=1"
# 2026-11-18 起列表端点被 PerimeterX 验证码拦截（带 / 不带 cookie、各指纹一律 403，
# 响应体是 px-captcha），而同一 cookie 下 seekalpha.py 的 /api/v3/news 仍可用。
# 全站 RSS 不经 PX，列表接口被拒时改由 RSS 取文章 id，正文仍走详情 API。
FEED_URL = "https://seekingalpha.com/feed.xml"
# RSS 混有大量财报电话会纪要 / 幻灯片，列表接口的 latest-articles 不含这些
FEED_SKIP_AUTHORS = ("SA Transcripts",)


def list_from_api():
    response = _safe_get(LIST_URL, headers=headers, timeout=util.request_timeout(10))
    if response.status_code != 200:
        util.info(f"list api rejected: {response.status_code}, falling back to rss")
        return None
    posts = []
    for post in response.json()["data"]:
        posts.append({
            "id": post["id"],
            "title": post["attributes"]["title"],
            "image": post["attributes"]["gettyImageUrl"],
            "link": base_url + post["links"]["self"],
        })
    return posts


def list_from_feed():
    response = _get_session().get(FEED_URL, timeout=util.request_timeout(10))
    if response.status_code != 200:
        util.log_action_error(f"list api and rss both failed, rss: {response.status_code}")
        return None
    posts = []
    for item in ET.fromstring(response.content).iter("item"):
        authors = [c.text for c in item.findall("category") if c.get("type") == "author"]
        if any(a in FEED_SKIP_AUTHORS for a in authors):
            continue
        posts.append({
            "id": (item.findtext("guid") or "").strip(),
            "title": (item.findtext("title") or "").strip(),
            "image": "",
            "link": (item.findtext("link") or "").split("?")[0].strip(),
        })
    return posts


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        posts = list_from_api()
        if posts is None:
            posts = list_from_feed()
    except Exception as e:
        util.log_action_error(f"request error: {e}")
        return
    if posts is None:
        return

    for post in posts[:3]:
        if post["link"] in ",".join(links):
            util.info(f"exists link: {post['link']}")
            break
        description = get_detail(post["id"])
        if description == "":
            util.log_action_error(f"detail {post['link']} failed")
            continue
        insert = True
        articles.insert(0, {
            "id": post["id"],
            "title": post["title"],
            "description": description,
            "image": post["image"],
            "link": post["link"],
            "pub_date": util.current_time_string(),
            "source": "seekalpha_articles",
            "kind": 1,
            "language": "en",
        })
    if len(articles) > 0 and insert:
        if len(articles) > 10:
            articles = articles[:10]
        util.write_json_to_file(articles, filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
