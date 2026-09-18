# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re

from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

headers = {
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Origin": "https://www.channelnewsasia.com",
    "Referer": "https://www.channelnewsasia.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

base_url = "https://www.channelnewsasia.com/"
filename = "./news/data/channelnewsasia/list.json"
util = SpiderUtil()

# Algolia API configuration
algolia_url = "https://kkwfbq38xf-2.algolianet.com/1/indexes/*/queries"
algolia_params = {
    "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser (lite); instantsearch.js (4.0.0); JS Helper (0.0.0-5a0352a)",
    "x-algolia-application-id": "KKWFBQ38XF",
    "x-algolia-api-key": "e5eb600a29d13097eef3f8da05bf93c1"
}

# Request payload for Algolia API
algolia_payload = {
    "requests": [
        {
            "indexName": "cnarevamp-ezrqv5hx",
            "params": "query=&maxValuesPerFacet=40&page=0&hitsPerPage=15&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&facets=%5B%22categories%22%2C%22type%22%5D&tagFilters=&facetFilters=%5B%5B%22categories%3ABusiness%22%5D%2C%5B%22type%3Aarticle%22%5D%5D"
        },
        {
            "indexName": "cnarevamp-ezrqv5hx",
            "params": "query=&maxValuesPerFacet=40&page=0&hitsPerPage=1&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=categories&facetFilters=%5B%5B%22type%3Aarticle%22%5D%5D"
        },
        {
            "indexName": "cnarevamp-ezrqv5hx",
            "params": "query=&maxValuesPerFacet=40&page=0&hitsPerPage=1&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=type&facetFilters=%5B%5B%22categories%3ABusiness%22%5D%5D"
        }
    ]
}

def run():
    """Main function to fetch and process CNA articles"""
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        # Make request to Algolia API
        response = requests.post(
            algolia_url,
            headers={**headers, **algolia_params},
            data=json.dumps(algolia_payload),
            timeout=10
        )
        
        if response.status_code == 200:
            body = response.text
            algolia_data = json.loads(body)
            
            # Extract articles from the first request (index 0)
            if "results" in algolia_data and len(algolia_data["results"]) > 0:
                hits = algolia_data["results"][0].get("hits", [])
                
                for index, hit in enumerate(hits):
                    if index < 10:  # Limit to 10 articles
                        # Extract article data
                        title = hit.get("title", "")
                        link_absolute = hit.get("link_absolute", "")
                        
                        if not link_absolute:
                            # Try alternative link fields
                            link_absolute = hit.get("url", "") or hit.get("link", "")
                        
                        if not link_absolute or link_absolute in ",".join(links):
                            util.info("exists link or no link: {}".format(link_absolute))
                            continue
                        
                        # Get paragraph_text as description
                        paragraph_text = ""
                        paragraph = hit.get("paragraph_text", "")
                        if type(paragraph) == list:
                            for item in paragraph:
                                paragraph_text += item
                        else:
                            paragraph_text = paragraph
                        # Extract publication date
                        pub_date = ""
                        if "published_at" in hit:
                            pub_date = util.parse_time(hit["published_at"], "%Y-%m-%dT%H:%M:%SZ")
                        elif "created_at" in hit:
                            pub_date = util.parse_time(hit["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                        elif "date" in hit:
                            pub_date = util.parse_time(hit["date"], "%Y-%m-%dT%H:%M:%SZ")
                        # Get image if available
                        image = hit.get("image", "") or hit.get("thumbnail", "") or hit.get("featured_image", "")
                        # Generate unique ID
                        article_id = hit.get("objectID", "") or str(hash(link_absolute))

                        if paragraph_text and paragraph_text.strip():
                            insert = True
                            articles.insert(
                                0,
                                {
                                    "id": article_id,
                                    "title": title,
                                    "description": paragraph_text,
                                    "image": image,
                                    "link": link_absolute,
                                    "pub_date": pub_date,
                                    "source": "channelnewsasia",
                                    "kind": 1,
                                    "language": "en",
                                },
                            )
                            util.info("Added article: {}".format(title[:50]))
            
            # Save articles if any were added
            if len(articles) > 0 and insert:
                if len(articles) > 15:  # Keep only latest 15 articles
                    articles = articles[:15]
                util.write_json_to_file(articles, filename)
                util.info("Saved {} articles to {}".format(len(articles), filename))
            else:
                util.info("No new articles found")
        else:
            util.log_action_error("Algolia API request error: {}".format(response.status_code))
            
    except Exception as e:
        util.log_action_error("Error in channelnewsasia.py: {}".format(str(e)))
        util.log_action_error("Traceback: {}".format(traceback.format_exc()))


if __name__ == "__main__":
    util.execute_with_timeout(run)
