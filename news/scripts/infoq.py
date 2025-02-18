# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-geek-req-id": "3d622c8a2ed44145a2a7d794b41aaa25@1@web",
    "cookie": "sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22191d5eccb9d2cd-003879ad7f96f7-18525637-2073600-191d5eccb9e11d7%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.infoq.cn%2Ftopic%2Fcloud-computing%22%7D%2C%22%24device_id%22%3A%22191d5eccb9d2cd-003879ad7f96f7-18525637-2073600-191d5eccb9e11d7%22%7D; Hm_lvt_094d2af1d9a57fd9249b3fa259428445=1725870951; HMACCOUNT=9DDE48DEBE88D1EC; _ga=GA1.2.336841458.1725870951; _gid=GA1.2.1620166244.1725870951; _gat=1; GRID=a2ff26e-d95f1b0-d98efe0-b873825; LF_ID=a2ff26e-d95f1b0-d98efe0-b873825; Hm_lpvt_094d2af1d9a57fd9249b3fa259428445=1725870983; _ga_TN7V5ES6HZ=GS1.2.1725870952.1.1.1725870983.0.0.0; __tea_cache_tokens_20000743={%22web_id%22:%227412559300251457037%22%2C%22user_unique_id%22:%227412559300251457037%22%2C%22timestamp%22:1725870984322%2C%22_type_%22:%22default%22}; SERVERID=3431a294a18c59fc8f5805662e2bd51e|1725870984|1725870950",
    "Referer": "https://www.infoq.cn/topic/cloud-computing",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://www.infoq.cn"
filename = "./news/data/infoq/list.json"
current_links = []
util = SpiderUtil()

def get_detail(id):
    if id in current_links:
        return ""
    print("infoq id: ", id)
    current_links.append(id)
    data = {"uuid": id}
    request = urllib.request.Request(
        "https://www.infoq.cn/public/v1/article/getDetail",
        data=bytes(json.dumps(data), encoding="utf8"),
        headers=headers,
        method="POST",
    )
    response = urllib.request.urlopen(request)
    if response.status == 200:
        article_body = ""
        body = response.read().decode("utf-8")
        url = json.loads(body)["data"]["content_url"]
        if url == "":
            return ""
        request = urllib.request.Request(url, None, headers=headers)
        resp = urllib.request.urlopen(request)
        article_body = ""
        if resp.status == 200:
            resp = resp.read().decode("utf-8")
            paragraphs = json.loads(resp)["content"]
            for paragraph in paragraphs:
                if paragraph["type"] == "paragraph":
                    if "content" in paragraph and len(paragraph["content"]) > 0:
                        text = ""
                        for content in paragraph["content"]:
                            if content["type"] == "text" and content["text"] != "":
                                if "marks" in content and len(content["marks"]) > 0:
                                    type = content["marks"][0]["type"]
                                    text = text + "<{}>{}</{}>".format(
                                        type, content["text"], type
                                    )
                                else:
                                    text = text + content["text"]
                        if text != "":
                            article_body = article_body + "<p>{}</p>".format(text)
                    else:
                        article_body = article_body + "<p></p>"
                elif paragraph["type"] == "heading":
                    if "content" in paragraph and len(paragraph["content"]) > 0:
                        for content in paragraph["content"]:
                            if content["type"] == "text" and content["text"] != "":
                                article_body = article_body + "<h2>{}</h2>".format(content["text"])
                elif paragraph["type"] == "image":
                    text = ""
                    if "attrs" in paragraph:
                        if paragraph["attrs"]["src"] != "":
                            text = "<img>{}<img>".format(paragraph["attrs"]["src"])
                        if text != "":
                            article_body = article_body + "<p>{}</p>".format(text)
                elif paragraph["type"] == "bulletedlist":
                    for item in paragraph["content"]:
                        if item["type"] == "listitem":
                            list_item_content = ""
                            for content in item["content"]:
                                if content["type"] == "paragraph":
                                    paragraph_content = ""
                                    if "content" in content:
                                        for text_content in content["content"]:
                                            if text_content["type"] == "text":
                                                text = text_content["text"]
                                                if "marks" in text_content:
                                                    for mark in text_content["marks"]:
                                                        if mark["type"] == "color":
                                                            color = mark["attrs"]["color"]
                                                            text = f'<span style="color:{color}">{text}</span>'
                                                        elif mark["type"] == "strong":
                                                            text = f'<strong>{text}</strong>'
                                                paragraph_content += text
                                            elif text_content["type"] == "link":
                                                link = text_content["attrs"]["href"]
                                                link_text = text_content["content"][0]["text"]
                                                paragraph_content += f'<a href="{link}">{link_text}</a>'
                                    list_item_content += f'<p>{paragraph_content}</p>'
                            article_body += f'<ul><li>{list_item_content}</li></ul>'
                else:
                    print("no this paragraph type", paragraph["type"])

            if article_body != "":
                article_body = "<div>{}</div>".format(article_body)
        return article_body
    else:
        print("infoq request: {} error: ".format(id), response)
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    data = {"type": 1, "ptype": 0, "size": 5, "id": 11}

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.infoq.cn/public/v1/article/getList",
        bytes(json.dumps(data), encoding="utf8"),
        headers,
        method="POST",
    )

    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["uuid"]
                title = post["article_title"]
                image = post["article_cover"]
                _type = "article"
                if post["sub_type"] == 4:
                    _type = "news"
                link = "https://www.infoq.cn/{}/{}".format(_type, id)
                if link in ",".join(links):
                    print("infoq exists link: ", link)
                    break
                
                pub_date = datetime.fromtimestamp(
                    post["publish_time"] / 1000.0
                ).strftime("%Y-%m-%d %H:%M:%S")
                
                description = get_detail(id)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "image": image,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "infoq",
                            "kind": 1,
                            "language": "zh-CN",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("infoq request error: {}".format(response))


util.execute_with_timeout(run)
