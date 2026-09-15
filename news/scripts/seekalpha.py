# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# 站点规则只盯 Chromium 系指纹：chrome120 / chrome131 / chrome136 对 API 一律 403
# （响应体 413 字节的 JSON），而 safari17_0 / safari18_0 / firefox133 均返回 200。
# 原实现固定 chrome120，恰是被拦的一档。与 seekalpha_articles 为同一问题。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "safari17_0")
_session = None

util = SpiderUtil()


def _get_session(profile=None):
    global _session
    if _session is None:
        _session = curl_requests.Session(
            impersonate=profile or IMPERSONATE_PROFILES[0]
        )
    return _session


def _safe_get(url, **kwargs):
    # 原实现先经 util.get_random_proxy() 试一次再回落直连。该代理池可用性从未验证，
    # 命中失效代理时多为超时而非报错，实测使单轮耗时从约 1 秒升至 5.9 秒；
    # statementdog 上更直接表现为 403（直连同一地址即 200）。故直接直连。
    return _get_session().get(url, verify=False, **kwargs)


headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://seekingalpha.com/market-news",
}

cookie = util.get_env_variable("seekingalpha", "")
if cookie:
    headers["cookie"] = cookie

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/list.json"


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    url = "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=6&page[number]=1"
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
            image = post["links"]["uriImage"]
            link = base_url + post["links"]["self"]
            if link in ",".join(links):
                util.info(f"exists link: {link}")
                break
            soup = BeautifulSoup(post["attributes"]["content"], "lxml")
            for element in soup.select("#more-links, .signup_widget_placeholder"):
                element.decompose()
            description = str(soup).strip()
            if description != "":
                insert = True
                articles.insert(0, {
                    "id": id,
                    "title": title,
                    "description": description,
                    "image": image,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "seekalpha",
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
