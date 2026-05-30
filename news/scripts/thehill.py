# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil
import requests

util = SpiderUtil()

headers = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

rss_url = "https://thehill.com/feed/"
api_base = "https://thehill.com/wp-json/wp/v2/posts/"
filename = "./news/data/thehill/list.json"

session = requests.Session()
session.headers.update(headers)


def extract_post_id(link):
    """Extract WordPress post ID from URL like /5696134-trump-greenland/"""
    match = re.search(r"/(\d+)-[^/]+/?$", link)
    if match:
        return match.group(1)
    return None


def get_detail_via_api(link):
    """Fetch article content via WordPress REST API, returns (post_id, content)"""
    post_id = extract_post_id(link)
    if not post_id:
        util.error("Cannot extract post ID from: {}".format(link))
        return None, ""

    util.info("Fetching post ID: {} from API".format(post_id))
    try:
        api_url = api_base + post_id
        response = session.get(
            api_url,
            headers=headers,
            proxies=util.get_random_proxy(),
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("content", {}).get("rendered", "")
            if content:
                soup = BeautifulSoup(content, "html.parser")
                ad_elements = soup.select(".ad-unit, .hardwall, style, script, aside, .wp-block-embed")
                for element in ad_elements:
                    element.decompose()
                return int(post_id), str(soup).strip()
            return int(post_id), ""
        else:
            util.error("API request error: {} for post {}".format(response.status_code, post_id))
            return None, ""
    except Exception as e:
        util.error("Error fetching from API: {}".format(str(e)))
        return None, ""


def clean_html_content(html_content):
    """Clean HTML content from description"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_rss_xml(xml_content):
    """Parse RSS XML feed and extract items"""
    try:
        root = ET.fromstring(xml_content)
        namespaces = {
            "content": "http://purl.org/rss/1.0/modules/content/",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        items = []
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            description_elem = item.find("description")
            pub_date_elem = item.find("pubDate")
            creator_elem = item.find("dc:creator", namespaces)

            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""
                description = ""
                if description_elem is not None and description_elem.text:
                    description = clean_html_content(description_elem.text)
                pub_date = (
                    pub_date_elem.text.strip()
                    if pub_date_elem is not None and pub_date_elem.text
                    else ""
                )
                creator = (
                    creator_elem.text.strip()
                    if creator_elem is not None and creator_elem.text
                    else ""
                )

                if title and link:
                    items.append(
                        {
                            "title": title,
                            "link": link,
                            "description": description,
                            "pub_date": pub_date,
                            "creator": creator,
                        }
                    )
        return items
    except ET.ParseError as e:
        util.error("XML parse error: {}".format(str(e)))
        return []
    except Exception as e:
        util.error("RSS parse error: {}".format(str(e)))
        return []


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        response = session.get(
            rss_url,
            headers={**headers, "accept": "application/xml"},
            proxies=util.get_random_proxy(),
            timeout=15,
            allow_redirects=True,
        )

        if response.status_code == 200:
            rss_items = parse_rss_xml(response.text)
            util.info("Parsed {} items from RSS feed".format(len(rss_items)))

            for index, item in enumerate(rss_items):
                if index >= 3:
                    break

                link = item["link"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue

                title = item["title"]
                rss_description = item["description"]

                post_id, description = get_detail_via_api(link)
                if not description:
                    if rss_description:
                        description = f"<p>{util.fix_text(rss_description)}</p>"
                        util.info("fallback to RSS description")
                    else:
                        util.info("skipping item with empty description: {}".format(link))
                        continue

                if not post_id:
                    post_id = extract_post_id(link)
                    if post_id:
                        post_id = int(post_id)

                insert = True
                articles.insert(
                    0,
                    {
                        "id": post_id,
                        "title": util.fix_text(title),
                        "description": description,
                        "kind": 1,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "thehill",
                        "language": "en",
                    },
                )
                util.info("added: {}".format(title[:50]))

            if len(articles) > 0 and insert:
                if len(articles) > 10:
                    articles = articles[:10]
                util.write_json_to_file(articles, filename)
        else:
            util.log_action_error(
                "RSS feed request error: {}".format(response.status_code)
            )
    except Exception as e:
        util.log_action_error("request error: {}".format(str(e)))


if __name__ == "__main__":
    util.execute_with_timeout(run)
