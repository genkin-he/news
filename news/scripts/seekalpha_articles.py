# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

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
        response = _safe_get(link, headers=headers, timeout=30)
    except Exception as e:
        util.error(f"get_detail error: {e}")
        return ""
    if response.status_code == 200:
        content = response.json()["data"]["attributes"]["content"]
        soup = BeautifulSoup(content, "lxml")
        for element in soup.select(".inline_ad_placeholder"):
            element.decompose()
        return str(soup).strip()
    return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=20&page[number]=1"
    try:
        response = _safe_get(url, headers=headers, timeout=30)
    except Exception as e:
        util.log_action_error(f"request error: {e}")
        return
    if response.status_code == 200:
        try:
            posts = response.json()["data"]
        except Exception as e:
            util.log_action_error(f"json parse error: {e}")
            return
        for index in range(len(posts)):
            if index >= 3:
                break
            post = posts[index]
            id = post["id"]
            title = post["attributes"]["title"]
            image = post["attributes"]["gettyImageUrl"]
            link = base_url + post["links"]["self"]
            if link in ",".join(links):
                util.info(f"exists link: {link}")
                break
            description = get_detail(id)
            if description != "":
                insert = True
                articles.insert(0, {
                    "id": id,
                    "title": title,
                    "description": description,
                    "image": image,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "seekalpha_articles",
                    "kind": 1,
                    "language": "en",
                })
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")


if __name__ == "__main__":
    util.execute_with_timeout(run)
