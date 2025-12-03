# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,zh-CN,zh;q=0.8",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Referer": "https://www.businesstoday.com.my/",
}

base_url = "https://www.businesstoday.com.my"
filename = "./news/data/businesstoday/list.json"
current_links = []
util = SpiderUtil(notify=False)

# Create a session to maintain cookie state and connection
session = requests.Session()
session.headers.update(headers)

def get_detail(link):
    util.info("link: {}".format(link))
    try:
        detail_headers = headers.copy()
        detail_headers["Referer"] = "https://www.businesstoday.com.my/category/marketing/"
        detail_headers["sec-fetch-site"] = "same-origin"
        response = session.get(link, headers=detail_headers, timeout=8, proxies=util.get_random_proxy(), allow_redirects=True)
        if response.status_code == 200:
            body = response.text
            if "Access Restricted" in body or "Forbidden" in body or "403" in body:
                util.error("Anti-crawler protection detected for link: {}".format(link))
                return ""
            lxml = BeautifulSoup(body, "lxml")
            soup = lxml.select_one("#tdi_40 div[data-td-block-uid= tdi_61] .tdb-block-inner")
            if soup is None:
                util.error("Content not found for link: {}".format(link))
                return ""

            ad_elements = soup.select("div")
            for element in ad_elements:
                element.decompose()

            return str(soup).strip()
        elif response.status_code == 403:
            util.error("403 Forbidden for link: {}".format(link))
            return ""
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except requests.RequestException as e:
        util.error("request exception for link {}: {}".format(link, str(e)))
        return ""

def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        # First visit homepage to establish session and get cookies
        homepage_headers = headers.copy()
        homepage_headers["sec-fetch-site"] = "none"
        homepage_headers["Referer"] = ""
        try:
            homepage_response = session.get(
                base_url, headers=homepage_headers, timeout=8, 
                proxies=util.get_random_proxy(), allow_redirects=True
            )
            if homepage_response.status_code == 200:
                util.info("Homepage visited successfully, session established")
        except Exception as e:
            util.error("Failed to visit homepage: {}".format(str(e)))

        # Now visit the target page
        list_headers = headers.copy()
        list_headers["sec-fetch-site"] = "same-origin"
        list_headers["Referer"] = base_url
        response = session.get(
            link, headers=list_headers, timeout=8, 
            proxies=util.get_random_proxy(), allow_redirects=True
        )
        if response.status_code == 200:
            body = response.text
            if "Access Restricted" in body or "Forbidden" in body or "403" in body:
                util.log_action_error("businesstoday anti-crawler protection detected")
                return
            lxml = BeautifulSoup(body, "lxml")
            items = lxml.select("h3.entry-title a")
            if not items:
                util.error("No articles found on page")
                return
            data_index = 0
            for item in items:
                if data_index > 2:
                    break
                article_link = str(item.get("href", ""))
                if not article_link:
                    continue
                title = str(item.text).strip()
                if not title:
                    continue
                description = get_detail(article_link)
                if article_link in ",".join(_links):
                    util.info("exists link: {}".format(article_link))
                    continue
                if description != "":
                    insert = True
                    data_index += 1
                    _articles.insert(
                        data_index,
                        {
                            "title": title,
                            "description": description,
                            "link": article_link,
                            "pub_date": util.current_time_string(),
                            "source": "businesstoday",
                            "kind": 1,
                            "language": "en",
                        },
                    )

            if len(_articles) > 0 and insert:
                if len(_articles) > 20:
                    _articles = _articles[:20]
                util.write_json_to_file(_articles, filename)
        elif response.status_code == 403:
            util.log_action_error("businesstoday 403 Forbidden - anti-crawler protection")
        else:
            util.log_action_error("businesstoday request error: {}".format(response.status_code))
    except requests.RequestException as e:
        util.log_action_error("request error: {}".format(str(e)))
    except Exception as e:
        util.log_action_error("unexpected error: {}".format(str(e)))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.businesstoday.com.my/category/marketing/")