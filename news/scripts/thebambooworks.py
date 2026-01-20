# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
from curl_cffi import requests

util = SpiderUtil()

# Chinese RSS feed for 快讯 category
rss_url = "https://thebambooworks.com/cn/category/%E5%BF%AB%E8%AE%AF/feed/"
filename = "./news/data/thebambooworks/list.json"


def extract_post_id(guid_or_link):
    """Extract post ID from guid like https://thebambooworks.com/?p=57303"""
    match = re.search(r"\?p=(\d+)", guid_or_link)
    if match:
        return int(match.group(1))
    return None


def make_request(url, timeout=15):
    """Make request with chrome110 impersonation and proxy"""
    try:
        return requests.get(
            url,
            impersonate="chrome110",
            timeout=timeout,
            proxies=util.get_random_proxy(),
        )
    except Exception as e:
        util.error("Request failed: {}".format(str(e)))
        return None


def get_detail(link):
    """Fetch full article content from link"""
    try:
        response = make_request(link)

        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            content_elem = soup.select_one("#entry-content-container, .entry-content")

            if content_elem:
                # Remove unwanted elements
                for element in content_elem.select(
                    ".addtoany_share_save_container, .post-tags, .leaky_paywall_message_wrap, "
                    ".umResizer, script, style, .related-posts, .author-box, .comments-area"
                ):
                    element.decompose()

                # Remove "欲订阅..." subscription text
                for p in content_elem.find_all("p"):
                    if p.get_text() and "欲订阅" in p.get_text():
                        p.decompose()

                # Get clean HTML
                content_html = str(content_elem)
                # Remove outer div wrapper
                content_html = re.sub(r"^<div[^>]*>", "", content_html)
                content_html = re.sub(r"</div>$", "", content_html)
                return content_html.strip()
        util.error("Detail request failed for {}".format(link))
        return ""
    except Exception as e:
        util.error("Error fetching detail: {}".format(str(e)))
        return ""


def parse_rss_xml(xml_content):
    """Parse RSS XML feed and extract items"""
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            guid_elem = item.find("guid")

            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""
                guid = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else ""

                if title and link:
                    items.append(
                        {
                            "title": title,
                            "link": link,
                            "guid": guid,
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
    post_count = 0

    try:
        # Use curl_cffi with browser impersonation to bypass Cloudflare
        response = make_request(rss_url)

        if response and response.status_code == 200:
            rss_items = parse_rss_xml(response.text)
            util.info("Parsed {} items from RSS feed".format(len(rss_items)))

            for item in rss_items:
                if post_count >= 2:
                    break

                link = item["link"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue

                title = item["title"]
                post_id = extract_post_id(item["guid"])

                # Get full content from article page
                description = get_detail(link)
                if not description:
                    util.info("skipping item with empty description: {}".format(link))
                    continue

                post_count += 1
                insert = True
                articles.insert(
                    0,
                    {
                        "id": post_id,
                        "title": util.fix_text(title),
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "bambooworks",
                        "kind": 1,
                        "language": "zh-CN",
                    },
                )
                util.info("added: {}".format(title[:50]))

            if len(articles) > 0 and insert:
                if len(articles) > 10:
                    articles = articles[:10]
                util.write_json_to_file(articles, filename)
        else:
            status = response.status_code if response else "no response"
            util.log_action_error("RSS request error: {}".format(status))
    except Exception as e:
        util.log_action_error("request error: {}".format(str(e)))


if __name__ == "__main__":
    # 403 Forbidden 2026-01-20
    util.info("403 Forbidden 2026-01-20")
    # util.execute_with_timeout(run)
