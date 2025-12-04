# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib
import json
import re
import time
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}

base_url = "https://thehill.com"
api_url = "https://thehill.com/wp-json/lakana/v1/template-variables/"
filename = "./news/data/thehill/list.json"

# Create a session to maintain cookie state
session = requests.Session()
session.headers.update(headers)


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        detail_headers = headers.copy()
        detail_headers["sec-fetch-site"] = "same-origin"
        detail_headers["sec-fetch-dest"] = "document"
        detail_headers["sec-fetch-mode"] = "navigate"
        detail_headers["referer"] = base_url
        
        response = session.get(
            link, 
            headers=detail_headers, 
            proxies=util.get_random_proxy(),
            timeout=10,
            allow_redirects=True
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            article_text = body.select(".article__text")
            if not article_text:
                util.error("Article text not found for: {}".format(link))
                return ""
            
            soup = article_text[0]
            ad_elements = soup.select(".ad-unit,.hardwall, style, script, div, aside ")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        elif response.status_code == 403:
            util.error("403 Forbidden for: {}. Session may have expired.".format(link))
            return ""
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error(f"Error fetching detail for {link}: {str(e)}")
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        # First visit homepage to establish session and get cookies
        homepage_headers = headers.copy()
        homepage_headers["sec-fetch-site"] = "none"
        homepage_headers["referer"] = ""
        
        try:
            homepage_response = session.get(
                base_url, 
                headers=homepage_headers, 
                timeout=10,
                proxies=util.get_random_proxy(), 
                allow_redirects=True
            )
            if homepage_response.status_code in [200, 304]:
                util.info("Homepage visited successfully, session established")
                # Small delay to ensure cookies are set
                time.sleep(0.5)
            else:
                util.error("Homepage visit failed with status: {}".format(homepage_response.status_code))
        except Exception as e:
            util.error("Failed to visit homepage: {}".format(str(e)))

        # Now visit the API endpoint
        api_headers = headers.copy()
        api_headers["accept"] = "application/json, */*;q=0.1"
        api_headers["sec-fetch-dest"] = "empty"
        api_headers["sec-fetch-mode"] = "cors"
        api_headers["sec-fetch-site"] = "same-origin"
        api_headers["referer"] = base_url
        
        response = session.get(
            api_url,
            headers=api_headers,
            proxies=util.get_random_proxy(),
            timeout=10,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            try:
                data_json = response.json()
                if "sidebar" not in data_json or "just_in" not in data_json["sidebar"]:
                    util.error("Invalid API response structure")
                    return
                
                posts = data_json["sidebar"]["just_in"]
                for index in range(len(posts)):
                    if index < 2:
                        post = posts[index]
                        kind = post["post_type"]
                        id = post["id"]
                        title = post["title"]
                        link = post["link"]
                        if link in ",".join(links):
                            util.info("exists link: {}".format(link))
                            break

                        description = get_detail(link)
                        if description != "":
                            insert = True
                            articles.insert(
                                0,
                                {
                                    "id": id,
                                    "title": title,
                                    "description": description,
                                    "kind": kind,
                                    "link": link,
                                    "pub_date": util.current_time_string(),
                                    "source": "thehill",
                                    "language": "en",
                                },
                            )
                            # Small delay between article fetches
                            time.sleep(0.3)
                
                if len(articles) > 0 and insert:
                    if len(articles) > 10:
                        articles = articles[:10]
                    util.write_json_to_file(articles, filename)
            except json.JSONDecodeError as e:
                util.log_action_error(f"JSON decode error: {str(e)}")
            except KeyError as e:
                util.log_action_error(f"Missing key in API response: {str(e)}")
        elif response.status_code == 403:
            util.log_action_error(f"403 Forbidden: Session expired or blocked. Cookies may need refresh.")
        else:
            util.log_action_error(f"request error: {response.status_code}")
    except Exception as e:
        util.log_action_error(f"request error: {str(e)}")

if __name__ == "__main__":
    if util.should_run_by_minute(divisor=10):
        util.execute_with_timeout(run)
