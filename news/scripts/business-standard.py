# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import requests  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re
from datetime import datetime

class RealListDataGenerator:
    def __init__(self):
        # 从 JavaScript 代码中提取的编码字符集
        self.encoding_chars = "95867qrstuvwxyzabcdefghijklmnop01234JKLMNOPQRSTUVWXYZABCDEFGHI"

        if len(self.encoding_chars) < 62:
            raise ValueError("编码字符集必须至少包含 62 个唯一字符")

        self.chars_length = len(self.encoding_chars)

    def get_char(self, index):
        return self.encoding_chars[index % self.chars_length]

    def encode_string(self, input_string):
        if not input_string:
            raise ValueError("输入字符串不能为空")

        if len(input_string) > 99:
            raise ValueError("输入字符串过长（最大 99 字符）")

        # 获取当前日期（两位数）
        current_date = datetime.now().day
        date_str = str(current_date).zfill(2)

        # 获取输入字符串长度（两位数）
        length_str = str(len(input_string)).zfill(2)

        # 构建完整字符串
        full_string = f"{date_str}{length_str}{input_string}bs255T"

        # 编码每个字符
        encoded = ""
        for char in full_string:
            char_code = ord(char)
            high_part = char_code // 62
            low_part = char_code % 62
            encoded += self.get_char(high_part) + self.get_char(low_part)

        return encoded

    def generate_list_data(self, category_creation_id=None, page=0, limit=21, offset=0, **additional_params):
        # 构建查询参数
        query_params = {
            "page": page,
            "limit": limit,
            "offset": offset
        }

        if category_creation_id is not None:
            query_params["categoryCreationId"] = category_creation_id

        query_params.update(additional_params)

        # 转换为 JSON 字符串（紧凑格式）
        json_string = json.dumps(query_params, separators=(',', ':'))

        # 编码
        encoded_data = self.encode_string(json_string)

        return encoded_data

    def generate_list_data_from_dict(self, params):
        json_string = json.dumps(params, separators=(',', ':'))
        return self.encode_string(json_string)

    def build_api_url(self, base_url, list_data):
        return f"{base_url}?listData={list_data}"



headers_2 = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "expires": "0",
    "origin": "https://www.business-standard.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.business-standard.com/",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-access-token": "",
}

base_url = "https://www.business-standard.com"
filename = "./news/data/businessstandard/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers_2)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        # Check if the target element exists before accessing it
        parent_div = lxml.select("#parent_top_div")
        if not parent_div:
            util.error("Element #parent_top_div not found for link: {}".format(link))
            return ""
        soup = parent_div[0]

        ad_elements = soup.select(".storyadsprg,.recommendsection, .mb-20 > style")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run():
    # 读取保存的文件
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用 requests 发送请求
    url = "https://apibs.business-standard.com/article/latest-news"

    generator = RealListDataGenerator()
    test_params = {"page": 0, "limit": 10, "offset": 0}
    json_str = json.dumps(test_params, separators=(',', ':'))
    encoded = generator.encode_string(json_str)
    url = generator.build_api_url(url, encoded)
    response = requests.get(url, headers=headers_2)

    if response.status_code == 200:
        result = response.json()["data"]
        date_index = 0
        for index in range(len(result)):
            if date_index < 3:
                id = result[index]["article_id"]
                article_url = result[index]["article_url"]
                link = "https://www.business-standard.com{}".format(article_url)
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                title = result[index]["heading1"]
                image = ""
                pub_date = result[index]["published_date"]
                # 将时间戳转换为日期格式
                if isinstance(pub_date, (int, str)):
                    try:
                        pub_date = int(pub_date)
                        from datetime import datetime
                        pub_date = datetime.fromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pub_date = str(pub_date)
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "id": id,
                            "description": description,
                            "link": link,
                            "image": image,
                            "pub_date": pub_date,
                            "source": "business-standard",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                    date_index += 1
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    # util.execute_with_timeout(run)
    util.info("403 Forbidden")
