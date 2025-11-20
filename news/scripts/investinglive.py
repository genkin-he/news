# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import time
import re
from util.spider_util import SpiderUtil

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US",
    "deviceid": "3ce4567a-57c6-42f3-a917-03d57a872390-1761725708133",
    "origin": "https://investinglive.com",
    "page": "/live-feed/",
    "priority": "u=1, i",
    "referer": "https://investinglive.com/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

detail_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US",
    "Connection": "keep-alive",
    "DeviceId": "3ce4567a-57c6-42f3-a917-03d57a872390-1761725708133",
    "Origin": "https://investinglive.com",
    "Referer": "https://investinglive.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

base_url = "https://investinglive.com"
filename = "./news/data/investinglive/list.json"
util = SpiderUtil()

def fetch_article_detail(article_id):
    """
    获取文章详细内容
    """
    try:
        # 构建详细内容 URL
        detail_url = f"https://fmpedia-forexlive-prod.s3.amazonaws.com/investing-articles/{article_id}.json?date={int(time.time() * 1000)}"
        
        # 添加 Page 头信息
        detail_headers_with_page = detail_headers.copy()
        detail_headers_with_page["Page"] = f"/news/{article_id}/"
        
        request = urllib.request.Request(detail_url, None, detail_headers_with_page)
        response = urllib.request.urlopen(request)
        
        if response.status == 200:
            body = response.read().decode("utf-8")
            detail_data = json.loads(body)
            bodyHtml = detail_data.get("Body", "")
            
            # 删除 figure 标签及其内容
            bodyHtml = re.sub(r'<figure[^>]*>.*?</figure>', '', bodyHtml, flags=re.DOTALL)
    
            return bodyHtml
        else:
            util.error(f"Failed to fetch detail for article {article_id}: {response.status}")
            return ""
    except Exception as e:
        util.error(f"Error fetching detail for article {article_id}: {str(e)}")
        return ""

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(
        "https://api.investinglive.com/api/articles/get-all-news?take=12&page=0",
        None,
        headers,
    )

    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["Articles"]
        data_index = 0
        for index in range(len(posts)):
            if data_index < 5:
                post = posts[index]
                slug = post['Slug']
                category = post['Category']["Slug"]
                link = f"{base_url}/{category}/{slug}"
                util.info("link: {}".format(link))
                title = post["Title"]
                id = post["Id"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                description = fetch_article_detail(id)
                if not description:
                    continue
                pub_date = util.current_time_string()
                if post.get("PublishedOn"):
                    pub_date = util.parse_time(post["PublishedOn"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "investinglive",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    data_index += 1
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
