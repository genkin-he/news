# -*- coding: UTF-8 -*-
import re
import json
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil

IMPERSONATE = "chrome120"
_session = None

util = SpiderUtil()


def _get_session():
    global _session
    if _session is None:
        _session = curl_requests.Session(impersonate=IMPERSONATE)
    return _session


headers = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.tipranks.com/",
}

base_url = "https://tipranks.com"
filename = "./news/data/tipranks/announcements.json"


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = _get_session().get(link, headers=headers, timeout=30)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    body = response.text
    items = body.split("document.querySelectorAll")
    if len(items) > 1:
        body = items[1]
    else:
        return ""
    result = re.findall(r".*window.__STATE__=JSON.parse\((.*)\);*", body)
    if len(result) > 0:
        resp = json.loads(result[0])
        result = re.findall(r'.*content":(.*),"date:*', resp)
        if len(result) > 0:
            result = eval(result[0])
            result = re.sub(r"(\n)\1+", "\n", result)
            result = re.sub(r'^<html><head></head><body>', '', result)
            result = re.sub(r'</body></html>$', '', result)
            promo_pattern = r'.*?Unlock powerful investing tools, advanced data, and expert analyst insights to help you invest with confidence\.\n</li></ul>'
            result = re.sub(promo_pattern, '', result, flags=re.DOTALL)
            see_more_pattern = r'\n<p></p><p><p>See more.*'
            result = re.sub(see_more_pattern, '', result, flags=re.DOTALL)
            for_detailed_pattern = r'\n<p></p><p>For detailed.*'
            result = re.sub(for_detailed_pattern, '', result, flags=re.DOTALL)
            result = re.sub(r'\n?</body></html>.*', '', result, flags=re.DOTALL)
            extra_content_pattern = r'\n<p></p><div class=\"tipranks-extra-content\"><a href=\"https://www\.tipranks\.com/.*'
            result = re.sub(extra_content_pattern, '', result, flags=re.DOTALL)
            trending_pattern = r'\n<div id=\"trending\" class=\"trending-posts\"><h2 class=\"fontWeightsemibold textDecorationunderline\">Trending Articles.*'
            result = re.sub(trending_pattern, '', result, flags=re.DOTALL)
            figure_pattern = r'\n<figure.*'
            result = re.sub(figure_pattern, '', result, flags=re.DOTALL)
            return result
    return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        response = _get_session().get(
            "https://www.tipranks.com/api/news/posts?per_page=5&category=company-announcements",
            headers=headers,
            timeout=30,
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        try:
            posts = response.json()["data"]
        except Exception as e:
            util.log_action_error("json parse error: {}".format(e))
            return
        for index in range(len(posts)):
            if index >= 1:
                break
            post = posts[index]
            id = post["_id"]
            title = post["title"]
            image = post["image"]["src"] if post.get("image") else ""
            link = post["link"]
            author = post["author"]["name"]
            pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(0, {
                    "id": id,
                    "title": title,
                    "description": description,
                    "image": image,
                    "link": link,
                    "author": author,
                    "pub_date": pub_date,
                    "source": "tipranks_announcements",
                    "kind": 1,
                    "language": "en",
                })
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
