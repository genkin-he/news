# -*- coding: UTF-8 -*-
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

IMPERSONATE = "chrome120"
_session = None

def _get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


util = SpiderUtil()


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
