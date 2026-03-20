# -*- coding: UTF-8 -*-
from curl_cffi import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

base_url = "https://www.businesstoday.com.my"
filename = "./news/data/businesstoday/list.json"
util = SpiderUtil(notify=False)


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, impersonate="chrome", timeout=10)
        if response.status_code == 200:
            body = response.text
            lxml = BeautifulSoup(body, "lxml")
            soup = lxml.select_one("#tdi_40 div[data-td-block-uid=tdi_61] .tdb-block-inner")
            if soup is None:
                # Try alternative selector
                soup = lxml.select_one(".td-post-content, .tdb-block-inner, article .entry-content")
            if soup is None:
                util.error("Content not found for link: {}".format(link))
                return ""

            # Remove unwanted elements
            for element in soup.select("div.td-a-rec, script, style, .sharedaddy, .jp-relatedposts"):
                element.decompose()

            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception for link {}: {}".format(link, str(e)))
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(link, impersonate="chrome", timeout=10)
        if response.status_code == 200:
            body = response.text
            lxml = BeautifulSoup(body, "lxml")
            items = lxml.select("h3.entry-title a")
            if not items:
                util.error("No articles found on page")
                return
            data_index = 0
            for item in items:
                if data_index >= 2:
                    break
                article_link = str(item.get("href", ""))
                if not article_link:
                    continue
                title = str(item.text).strip()
                if not title:
                    continue
                if article_link in ",".join(_links):
                    util.info("exists link: {}".format(article_link))
                    continue
                description = get_detail(article_link)
                if description:
                    insert = True
                    data_index += 1
                    _articles.insert(
                        0,
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
                    util.info("added: {}".format(title[:50]))

            if len(_articles) > 0 and insert:
                if len(_articles) > 20:
                    _articles = _articles[:20]
                util.write_json_to_file(_articles, filename)
        else:
            util.log_action_error("businesstoday request error: {}".format(response.status_code))
    except Exception as e:
        util.log_action_error("request error: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.businesstoday.com.my/category/marketing/")
