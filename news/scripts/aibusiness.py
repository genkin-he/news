# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
import time
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
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
    # "cookie": "_gcl_au=1.1.1528930114.1762740330; localZipcode=50036-50036; feathr_session_id=6911486d9748bbcd913f43ef; _cb=DzDIcLBYzZ1WCQLMMb; sa-user-id=s%253A0-775d5a6d-efbb-5373-72d3-d156bc9bfbda.mrFKXUkZHKDIksutQ7T0NXlwodgNeabzJjFy0JexuNY; sa-user-id-v2=s%253Ad11abe-7U3Ny09FWvJv72gjfFx8.2h00d17V4cmqzkUeM18EZmDL5FoNYVvUfnn%252BGdbfIac; sa-user-id-v3=s%253AAQAKIK7Ss-GAF28_jJze_vtDhCUz_-oo7bnWKkfTIc71SVRIEAMYAyDruOjDBjABOgQz5Ny5QgSPZ32J.bQDA11mYpqJ6s3alo6sBlO5fNTSnDSGZZAbA%252FBzFDtM; _ga=GA1.1.567475996.1762740334; _hjSessionUser_3226445=eyJpZCI6ImYyOTkyNGM4LTBmM2ItNWJjNS04MzdiLTM2NjkyMGIyMmFiZSIsImNyZWF0ZWQiOjE3NjI3NDAzMzM5NTcsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_3226445=eyJpZCI6ImZjMzcxNDQyLTNmODEtNGI2My05MjFlLTRkYmI0ZmJiOWY0OSIsImMiOjE3NjI3NDAzMzM5NTcsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _sp_ses.d30d=*; _clck=14kg647%5E2%5Eg0w%5E0%5E2140; dpm_sid=019a6b82-f34b-76be-98d2-67901b585774; dpm_uid=019a6b82-f34b-7177-8f31-c6118ecd93f3; sp=d026f912-3536-425e-b3da-5263ed4ec74d; _iris_duid=4ca675cf-a569-4f81-b51a-a7a4c5c1a1e8; tcm={\"purposes\":{\"GcmAdvanced\":\"Auto\",\"Advertising\":true,\"Functional\":true,\"SaleOfInfo\":\"Auto\",\"Analytics\":true},\"timestamp\":\"2025-11-10T02:05:56.685Z\",\"confirmed\":true,\"prompted\":true,\"updated\":true}; _chartbeat5=458|920|%2Flatest-news|https%3A%2F%2Faibusiness.com%2Fagentic-ai%2Fgoogle-readies-purpose-built-ai-chip|BMmb3MCBu0RcLYnswCdgoJ3B-fwkI||r|BMmb3MCBu0RcLYnswCdgoJ3B-fwkI|aibusiness.com||; cf_clearance=bZcEqppUqOfdA.qJRXwMR6jrcG3rZ8vDiQFe71nTPyM-1762740384-1.2.1.1-bIkRMmBl5SCi849PuL9BVsTjjgF8xSVvoCGjLkTDPJDBCqhE_3pG4K9baPWzqckxzxlXO0zc55q9F10eO4FQmtUR1mFGW34SOH9Yfzr5aQgWq0gvuTRQ8z8zntOZa1w3KwLvhDDYlDjNJ9JGHVMAo1oUlCXJ8mEfIcLFF3D_qPahRFeriPHh2yi3w.XAEWQHQuG0FX5_BE79LReLwSlTfFqpIm6z2N_CDX2bFDvphz4; _ga_7F5ECFZYNN=GS2.1.s1762740333$o1$g1$t1762740384$j16$l0$h0; _chartbeat2=.1762740333426.1762740384690.1.BEmsCXp7zVQCF0-hLDR7OSlDrunhu.1; _cb_svref=external; sailthru_pageviews=3; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%228af7a648-1aef-4338-8a9f-3c82c603cce1%5C%22%2C%5B1762740332%2C214000000%5D%5D%22%5D%5D%5D; _sp_id.d30d=4ca675cf-a569-4f81-b51a-a7a4c5c1a1e8.1762740334.1.1762740385..a694df41-d054-463d-9675-d6664a9d6387..3426132c-33c8-4ef7-a30c-841df1cce426.1762740334195.7; dpm_url_count=3; sailthru_visitor=f856fdb3-6b76-41d5-ada0-e0ed9dc83058; FCNEC=%5B%5B%22AKsRol9vyWf22YXNLcvIU6hGMOXK2IwxfXSQwkCXNcbn2dQhFiFbDx1OBwdUUr6UOn5ddbaBLAEDrfpNA0S8GRk3nNqUGHnGQ1zdI5addXZCBoQJr5nd9WVk-oMV6HkDxBcJiRXE0xLxhuiXmmRp87IE8fPmEyPKpw%3D%3D%22%5D%5D; _clsk=1thlwpj%5E1762740386399%5E3%5E1%5Ek.clarity.ms%2Fcollect; dpm_time_site=51.002",
}

base_url = "https://aibusiness.com"
list_url = "https://aibusiness.com/latest-news"
filename = "./news/data/aibusiness/list.json"
current_links = []
util = SpiderUtil(notify=False)

# Create a session to maintain cookie state
session = requests.Session()
session.headers.update(headers)


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    try:
        # First visit the article page to establish session and get cookies
        article_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": list_url,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        }
        article_visited = False
        try:
            article_response = session.get(
                link, headers=article_headers, timeout=5, 
                proxies=util.get_random_proxy(), allow_redirects=True
            )
            if article_response.status_code in [200, 304]:
                article_visited = True
                util.info("Article page visited successfully, cookies established")
                # Small delay to ensure cookies are set
                time.sleep(0.5)
            else:
                util.error("Article page returned status: {}".format(article_response.status_code))
        except Exception as e:
            util.error("Failed to visit article page: {}".format(str(e)))

        if not article_visited:
            util.error("Skipping .data request because article page visit failed")
            return ""

        data_url = link
        if not data_url.endswith(".data"):
            if data_url.endswith("/"):
                data_url = data_url.rstrip("/") + ".data"
            else:
                data_url = data_url + ".data"

        detail_headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
            "referer": list_url,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        }

        response = session.get(
            data_url, headers=detail_headers, timeout=5, 
            proxies=util.get_random_proxy(), allow_redirects=True
        )
        if response.status_code == 200:
            try:
                data = response.json()
                if not isinstance(data, list) or len(data) == 0:
                    util.error("invalid data format: {}".format(data_url))
                    return ""
                body_json_indices = None
                for item in data:
                    if isinstance(item, dict) and "bodyJson" in item:
                        body_json_indices = item["bodyJson"]
                        break
                if not body_json_indices or not isinstance(body_json_indices, list):
                    util.error("bodyJson not found: {}".format(data_url))
                    return ""
                def get_item_by_index(idx):
                    if isinstance(idx, int) and 0 <= idx < len(data):
                        return data[idx]
                    return None
                def extract_text_from_item(item):
                    if isinstance(item, str):
                        return item
                    if isinstance(item, dict):
                        text = item.get("_931") or item.get("text") or item.get("_177")
                        if isinstance(text, str):
                            return text
                        if isinstance(text, dict):
                            return extract_text_from_item(text)
                    return None
                paragraphs = []
                for idx in body_json_indices:
                    item = get_item_by_index(idx)
                    if not item or not isinstance(item, dict):
                        continue
                    item_type = item.get("_177")
                    if item_type == "paragraph" or (isinstance(item_type, str) and "paragraph" in item_type.lower()):
                        content = item.get("content", [])
                        if isinstance(content, list):
                            text_parts = []
                            for content_idx in content:
                                if isinstance(content_idx, int):
                                    content_item = get_item_by_index(content_idx)
                                    text = extract_text_from_item(content_item)
                                    if text:
                                        text_parts.append(text)
                                elif isinstance(content_idx, dict):
                                    text = extract_text_from_item(content_idx)
                                    if text:
                                        text_parts.append(text)
                            if text_parts:
                                paragraphs.append(" ".join(text_parts))
                if not paragraphs:
                    util.error("no paragraphs found: {}".format(data_url))
                    return ""
                html_content = "<div class=\"article-content\">\n"
                for para in paragraphs:
                    html_content += "<p>{}</p>\n".format(para)
                html_content += "</div>"
                return html_content.strip()
            except json.JSONDecodeError as e:
                util.error("JSON decode error: {} - {}".format(data_url, str(e)))
                return ""
            except Exception as e:
                util.error("parse error: {} - {}".format(data_url, str(e)))
                return ""
        elif response.status_code == 403:
            util.error("403 Forbidden for: {}. Cookies may be missing or expired.".format(data_url))
            return ""
        else:
            util.error("request: {} error: {}".format(data_url, response.status_code))
            return ""
    except Exception as e:
        util.error("request exception: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        # First visit homepage to establish session and get cookies
        homepage_headers = headers.copy()
        homepage_headers["sec-fetch-site"] = "none"
        homepage_headers["referer"] = ""
        try:
            homepage_response = session.get(
                base_url, headers=homepage_headers, timeout=5, 
                proxies=util.get_random_proxy(), allow_redirects=True
            )
            if homepage_response.status_code in [200, 304]:
                util.info("Homepage visited successfully, session established")
        except Exception as e:
            util.error("Failed to visit homepage: {}".format(str(e)))

        # Now visit the list page
        list_headers = headers.copy()
        list_headers["sec-fetch-site"] = "same-origin"
        list_headers["referer"] = base_url
        response = session.get(
            list_url, headers=list_headers, timeout=5, 
            proxies=util.get_random_proxy(), allow_redirects=True
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            all_items = []
            seen_links = set()
            selectors = [
                "a.ArticlePreview-Title",
                "a.ContentCard-Title",
                "a.ListPreview-Title"
            ]
            for selector in selectors:
                items = soup.select(selector)
                for item in items:
                    href = item.get("href", "").strip()
                    title = item.get_text().strip()
                    if href and title:
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = base_url + href
                            else:
                                href = base_url + "/" + href
                        if href not in seen_links:
                            seen_links.add(href)
                            all_items.append({"link": href, "title": title})
            util.info("Found {} unique items total, taking first 8".format(len(all_items)))
            items_to_process = all_items[:8]
            data_index = 0
            for index, item in enumerate(items_to_process):
                if data_index >= 8:
                    break
                link = item["link"]
                title = item["title"]
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description != "":
                    insert = True
                    _articles.insert(
                        index,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "aibusiness",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1

        else:
            util.error("request url: {}, error: {}, response: {}".format(list_url, response.status_code, response))

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    except Exception as e:
        util.log_action_error("request exception: {}".format(str(e)))


if __name__ == "__main__":
    # 403 Forbidden 
    util.info("403 Forbidden")
    # util.execute_with_timeout(run)

