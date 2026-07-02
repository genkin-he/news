# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

IMPERSONATE = "chrome120"
_session = None

util = SpiderUtil()


def _get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


def _proxies():
    proxy = util.get_random_proxy()
    url = proxy.get("http") if proxy else None
    return {"http": url, "https": url} if url else {}


def _safe_get(url, **kwargs):
    proxy = _proxies()
    if proxy:
        try:
            resp = _get_session().get(url, proxies=proxy, verify=False, **kwargs)
            ct = resp.headers.get("content-type", "")
            if resp.status_code == 200 and "html" in ct:
                raise ValueError("proxy returned HTML error page")
            return resp
        except Exception:
            pass
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
