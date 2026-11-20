# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    "cookie": 'Hm_lvt_094d2af1d9a57fd9249b3fa259428445=1757664864; HMACCOUNT=3D0D96D90A2577B0; _ga=GA1.2.317563989.1757664864; _gid=GA1.2.1739741892.1757664864; GRID=def0d1a-1d0a9c6-64ebc15-4a78556; LF_ID=def0d1a-1d0a9c6-64ebc15-4a78556; mantis5539=84ef1fee7d8a491ba58a67e8494e4bd0@5539; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221993d04173710f4-03b78b27ab1a918-1f525631-2073600-1993d0417381c4b%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fs.geekbang.org%2F%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.infoq.cn%2Farticle%2FfHo3b4wRMmbaajc67Moh%3Futm_campaign%3Dgeek_search%26utm_content%3Dgeek_search%26utm_medium%3Dgeek_search%26utm_source%3Dgeek_search%26utm_term%3Dgeek_search%22%2C%22%24latest_utm_source%22%3A%22geek_search%22%2C%22%24latest_utm_medium%22%3A%22geek_search%22%2C%22%24latest_utm_campaign%22%3A%22geek_search%22%2C%22%24latest_utm_content%22%3A%22geek_search%22%2C%22%24latest_utm_term%22%3A%22geek_search%22%7D%2C%22%24device_id%22%3A%221993d04173710f4-03b78b27ab1a918-1f525631-2073600-1993d0417381c4b%22%7D; _tea_utm_cache_20000743={%22utm_source%22:%22geek_search%22%2C%22utm_medium%22:%22geek_search%22%2C%22utm_campaign%22:%22geek_search%22%2C%22utm_term%22:%22geek_search%22%2C%22utm_content%22:%22geek_search%22}; _r_c=1; _gat=1; Hm_lpvt_094d2af1d9a57fd9249b3fa259428445=1757665348; _ga_TN7V5ES6HZ=GS2.2.s1757664865$o1$g1$t1757665348$j48$l0$h0; SERVERID=1fa1f330efedec1559b3abbcb6e30f50|1757665349|1757664862; __tea_cache_tokens_20000743={%22web_id%22:%227549113112503409927%22%2C%22user_unique_id%22:%227549113112503409927%22%2C%22timestamp%22:1757665349620%2C%22_type_%22:%22default%22}',
    'Origin': 'https://www.infoq.cn',
    'Referer': 'https://www.infoq.cn/topic/%20industrynews',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'X-GEEK-REQ-ID': '5c2c91c5fbb24202aceb4dcde0340413@1@web',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

base_url = "https://www.infoq.cn"
filename = "./news/data/infoq/list.json"
current_links = []
util = SpiderUtil()

def get_detail(id):
    if id in current_links:
        return ""
    util.info("id: {}".format(id))
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
                    util.error("no this paragraph type {}".format(paragraph["type"]))

            if article_body != "":
                article_body = "<div>{}</div>".format(article_body)
        return article_body
    else:
        util.error("request: {} error: {}".format(id, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    data = {"type": 1, "ptype": 0, "size": 5, "id": 11}

    # request 中放入参数，请求头信息
    request = urllib.request.Request(
        "https://www.infoq.cn/public/v1/article/getList",
        bytes(json.dumps(data), encoding="utf8"),
        headers,
        method="POST",
    )

    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            post = posts[index]
            id = post["uuid"]
            title = post["article_title"]
            image = post["article_cover"]
            _type = "article"
            if post["sub_type"] == 4:
                _type = "news"
            link = "https://www.infoq.cn/{}/{}".format(_type, id)
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            
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
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
