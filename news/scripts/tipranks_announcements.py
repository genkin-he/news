# -*- coding: UTF-8 -*-
from util.spider_util import SpiderUtil
from util import tipranks_util

util = SpiderUtil()
# 详情页被 Cloudflare 按 runner 出口 IP 拦截，2026-11-19 实测约 90% 的轮次被拦，但各栏目
# 仍持续入库（漏掉的文章下一轮换到能通的 runner 时补抓）。30 分钟宽限会频繁误报，
# 放宽到 3 小时：真正全站封死时仍会告警。
util.health_grace_seconds = 3 * 60 * 60

filename = "./news/data/tipranks/announcements.json"


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = tipranks_util.get(link, spider=util)
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
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

    try:
        response = tipranks_util.get(
            "https://www.tipranks.com/api/news/posts?per_page=5&category=company-announcements",
            spider=util,
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code == 200:
        try:
            posts = response.json()["data"]
        except Exception as e:
            util.log_action_error("json parse error: {}".format(e))
            return
        for index in range(len(posts)):
            if index >= 1:
                break
            post = posts[index]
            id = post["_id"]
            title = post["title"]
            image = post["image"]["src"] if post.get("image") else ""
            link = post["link"]
            author = post["author"]["name"]
            pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(0, {
                    "id": id,
                    "title": title,
                    "description": description,
                    "image": image,
                    "link": link,
                    "author": author,
                    "pub_date": pub_date,
                    "source": "tipranks_announcements",
                    "kind": 1,
                    "language": "en",
                })
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
