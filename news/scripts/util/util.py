# -*- coding: UTF-8 -*-
import json

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
    