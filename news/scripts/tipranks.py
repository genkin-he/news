# -*- coding: UTF-8 -*-
from util.spider_util import SpiderUtil
from util import tipranks_util

util = SpiderUtil()

base_url = "https://www.tipranks.com"
filename = "./news/data/tipranks/list.json"


def get_detail(link):
    util.info("link: {}".format(link))
    response = tipranks_util.get(link)
    if response.status_code != 200:
        util.log_action_error("detail {} status: {}".format(link, response.status_code))
        return ""
    result = tipranks_util.parse_detail(response.text)
    if result == "":
        util.log_action_error("detail {} parse failed".format(link))
    return result


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = tipranks_util.get("https://tr-cdn.tipranks.com/bff/prod/header/payload.json")
    if response.status_code == 200:
        posts = response.json()["posts"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["_id"]
                title = post["title"]
                image = ""
                if "image" in post and post["image"]:
                    image = post["image"]["src"]
                link = base_url + post["link"]
                author = ""
                if "author" in post and post["author"] and "name" in post["author"]:
                    author = post["author"]["name"]
                pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": util.fix_text(title),
                            "description": util.fix_text(description),
                            "image": image,
                            "link": link,
                            "author": author,
                            "pub_date": pub_date,
                            "source": "tipranks",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run)
