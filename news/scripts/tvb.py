# -*- coding: UTF-8 -*-
import requests
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-TW,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://news.tvb.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

detail_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://news.tvb.com/",
}

list_url = "https://news.tvb.com/app/public/homepage?page=1&region_id=4&nav_id=4"
filename = "./news/data/tvb/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info(f"link: {link}")
    try:
        response = requests.get(link, headers=detail_headers)
        if response.status_code != 200:
            util.error(f"detail: {link} error: {response.status_code}")
            return ""

        # Extract __NUXT_DATA__ embedded SSR JSON
        match = re.search(r'id="__NUXT_DATA__">(.*?)</script>', response.text, re.DOTALL)
        if not match:
            return ""

        data = json.loads(match.group(1))

        # data[3] = {"article-detail-{id}-{lang}": article_idx}
        # data[article_idx] = {"content": content_idx, ...}
        # data[content_idx] = HTML string
        article_map = data[3]
        if not article_map:
            return ""

        article_idx = next(iter(article_map.values()))
        article = data[article_idx]
        content_idx = article.get("content")
        if content_idx is None:
            return ""

        content = data[content_idx]
        return content if isinstance(content, str) else ""
    except Exception as e:
        util.error(f"detail: {link} exception: {str(e)}")
        return ""


def run():
    saved = util.history_posts(filename)
    articles = saved["articles"]
    links = saved["links"]
    insert = False

    response = requests.get(list_url, headers=headers)
    if response.status_code != 200:
        util.log_action_error(f"list error: {response.status_code}")
        return

    body = response.json()
    items = body.get("data", {}).get("content", [])

    count = 0
    for item in items:
        if count >= 4:
            break
        if item.get("type") != "article":
            continue

        post = item["data"]
        article_id = post["id"]
        title = post.get("title_hk") or post.get("title", "")
        title = title.strip()
        if not title:
            continue

        link = f"https://news.tvb.com/tc/{article_id}"
        if link in ",".join(links):
            util.info(f"exists link: {link}")
            continue

        description = get_detail(link)
        if description:
            insert = True
            articles.insert(
                0,
                {
                    "id": article_id,
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "tvb",
                    "kind": 1,
                    "language": "zh-TW",
                },
            )
            count += 1

    if articles and insert:
        if len(articles) > 10:
            articles = articles[:10]
        util.write_json_to_file(articles, filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
    # detail = get_detail("https://news.tvb.com/tc/1179633")
    # util.info(detail)
