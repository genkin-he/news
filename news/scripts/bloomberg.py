# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "exp_pref=APAC; country_code=HK; seen_uk=1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

base_url = "https://www.bloomberg.com"
filename = "./news/data/bloomberg/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("news: " + link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split('<script id="__NEXT_DATA__" type="application/json">')[1]
        .split("</script></body></html>")[0]
    )
    elements = json.loads(body)["props"]["pageProps"]
    if "story" not in elements:
        return ""
    elements = elements["story"]["body"]["content"]
    html = "<div>"
    for element in elements:
        paragraph = ""
        text_count = 0
        if element["type"] == "paragraph":
            for sentence in element["content"]:
                if sentence["type"] == "text" and (
                    sentence["value"].startswith("Read more")
                    or sentence["value"].startswith("Read More")
                    or sentence["value"].startswith("More From ")
                    or "Want more Bloomberg" in sentence["value"]
                    or "You can follow Bloomberg" in sentence["value"]
                ):
                    break
                elif sentence["type"] == "text" and sentence["value"].lstrip() != "":
                    paragraph = paragraph + sentence["value"]
                    text_count = text_count + 1
                elif sentence["type"] == "link":
                    for ele in sentence["content"]:
                        if ele["type"] == "text" and ele["value"].lstrip() != "":
                            paragraph = paragraph + ele["value"]
                elif sentence["type"] == "entity" and sentence["subType"] == "security":
                    for ele in sentence["content"]:
                        if ele["type"] == "text" and ele["value"].lstrip() != "":
                            text_count = text_count + 1
                            paragraph = paragraph + ele["value"]
                elif sentence["type"] == "br":
                    paragraph = paragraph + "<br />"
        if paragraph.lstrip() != "" and text_count > 0:
            html = html + "<p>" + paragraph + "</p>"
    return html + "</div>"


def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    urls = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.bloomberg.com/lineup-next/api/paginate?id=archive_story_list&page=phx-markets&variation=archive&type=lineup_content",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        items = json.loads(body)["archive_story_list"]["items"]
        posts = []
        for index in range(len(items)):
            link = base_url + items[index]["url"]
            if "/news/articles/" in link:
                posts.append({"title": items[index]["headline"], "link": link})

        for index in range(len(posts)):
            if index < 3:
                link = posts[index]["link"]
                if link in ",".join(urls):
                    util.info("exists link: " + link)
                    break

                title = posts[index]["title"]
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "bloomberg",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(util.info, "机器人点击验证无法通过 stop bloomberg")
