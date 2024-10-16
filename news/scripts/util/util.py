# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timedelta

path = "./news/scripts/util/urls.json"

def exists(link):
    with open(path) as user_file:
        urls = json.load(user_file)
        if urls.has_key(link):
            return True
        else:
            urls[link] = 1
            with open(path,'w') as f:
                f.write(json.dumps(urls))
                
                
def history_posts(filepath):
    try:
        with open(filepath) as user_file:
            articles = json.load(user_file)["data"]
            links = []
            for article in articles:
                links.append(article["link"])
            return {'articles': articles, 'links': links}
    except:
        return {'articles': [], 'links': []}
    
def parse_time(time_str, format):
    # utc = "2021-03-08T08:28:47.776Z"
    # UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    timeObj = datetime.strptime(time_str, format)
    local_time = timeObj + timedelta(hours=8)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")

def has_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
 
    return False
