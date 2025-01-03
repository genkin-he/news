# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timezone, timedelta
import hashlib
import os

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

def current_time():
    # 获取当前时间(北京时间)
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def md5(string):
    return hashlib.md5(string.encode()).hexdigest()

def current_time_string():
    return current_time().strftime("%Y-%m-%d %H:%M:%S")

def append_to_env_var(var_name, data):
    """
    往指定环境变量追加数据
    :param var_name: 环境变量名称
    :param data: 需要追加的数据
    """
    if var_name in os.environ:
        current_value = os.environ.get(var_name, '')
        new_value = current_value + data
        os.environ[var_name] = new_value
    else:
        os.environ[var_name] = data
    return

def log_action_error(error_message):
    """
    记录操作错误信息到环境变量 ACTION_ERRORS
    :param error_message: 错误信息
    """
    append_to_env_var('ACTION_ERRORS', error_message)
    return
