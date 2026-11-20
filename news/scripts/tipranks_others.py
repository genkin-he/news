# -*- coding: UTF-8 -*-
from util.spider_util import SpiderUtil
from util import tipranks_util

util = SpiderUtil()

base_path = "./news/data/tipranks/{}.json"


def get_detail(link):
    util.info("link: {}".format(link))
    response = tipranks_util.get(link, spider=util)
    if response.status_code != 200:
        util.log_action_error("detail {} status: {}".format(link, response.status_code))
        return ""
    result = tipranks_util.parse_detail(response.text)
    if result == "":
        util.log_action_error("detail {} parse failed".format(link))
    return result


def collect_first_post(url, filename):
    """收集每个栏目的第一条新文章，不获取详情"""
    filepath = base_path.format(filename)
    data = util.history_posts(filepath)
    links = data["links"]

    response = tipranks_util.get(url, spider=util)
    if response.status_code == 200:
        posts = response.json()["data"]
        for post in posts:
            link = post["link"]
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue

            # 找到第一条新文章，返回文章信息和文件信息
            id = post["_id"]
            title = post["title"]
            image = ""
            if post.get("image") and post["image"]:
                image = post["image"]["src"]
            author = post["author"]["name"]
            pub_date = util.parse_time(post["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            
            return {
                "id": id,
                "title": title,
                "image": image,
                "link": link,
                "author": author,
                "pub_date": pub_date,
                "filename": filename,
                "filepath": filepath,
            }
    else:
        util.log_action_error("request error: {}".format(response.status_code))
    return None


def save_article(article_info, description):
    """保存文章到对应的文件"""
    filepath = article_info["filepath"]
    data = util.history_posts(filepath)
    articles = data["articles"]

    articles.insert(
        0,
        {
            "id": article_info["id"],
            "title": article_info["title"],
            "description": description,
            "image": article_info["image"],
            "link": article_info["link"],
            "author": article_info["author"],
            "pub_date": article_info["pub_date"],
            "source": "tipranks_others",
            "kind": 1,
            "language": "en",
        },
    )

    filename = article_info["filename"]
    if len(articles) > 20:
        articles = articles[:20]
    util.write_json_to_file(articles, filepath)

# 各栏目列表接口 + 详情页
CATEGORIES = [
    ("https://www.tipranks.com/api/news/posts?per_page=10&category=article", "others"),
    ("https://www.tipranks.com/api/news/posts?per_page=10&category=global-markets", "category_global_markets"),
    ("https://www.tipranks.com/api/news/posts?per_page=10&topic=dividend-stocks", "topic_dividend_stocks"),
    ("https://www.tipranks.com/api/news/posts?per_page=20&author=tipranks-auto-generated-intelligence-newsdesk", "author_tipranks_auto_generated_intelligence_newsdesk"),
    ("https://www.tipranks.com/api/news/posts?per_page=20&author=tipranksnewsdesk", "author_tipranks_newsdesk"),
    ("https://www.tipranks.com/api/news/posts?per_page=20&author=tiprankshongkongnewsdesk", "author_tipranks_hongkong_newsdesk"),
]


def run():
    # 第一步：收集所有栏目的第一条新文章
    articles_to_process = []
    for url, filename in CATEGORIES:
        article_info = collect_first_post(url, filename)
        if article_info:
            articles_to_process.append(article_info)

    # 第二步：循环获取详情并保存
    for article_info in articles_to_process:
        if util.out_of_time():
            util.info("out of time, skip: {}".format(article_info["link"]))
            break
        description = get_detail(article_info["link"])
        if description != "":
            save_article(article_info, description)


if __name__ == "__main__":
    # 必须经 execute_with_timeout 运行：它在开头注册健康结算钩子，一轮成功才会清掉
    # 失败计时。原先裸跑 main，只有出错时才注册钩子，成功轮次从不写 last_success，
    # 失败计时从 2026-11-10 起累积不清，30 分钟宽限形同虚设，每失败一轮就告警一次。
    util.execute_with_timeout(run)
