# -*- coding: UTF-8 -*-
from util.spider_util import SpiderUtil
from util import tipranks_util

util = SpiderUtil()

base_path = "./news/data/tipranks/{}.json"


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


def collect_first_post(url, filename):
    """收集每个栏目的第一条新文章，不获取详情"""
    filepath = base_path.format(filename)
    data = util.history_posts(filepath)
    links = data["links"]

    response = tipranks_util.get(url)
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

if __name__ == "__main__":
    # 定义所有栏目配置
    categories = [
        ("https://www.tipranks.com/api/news/posts?per_page=10&category=article", "others"),
        ("https://www.tipranks.com/api/news/posts?per_page=10&category=global-markets", "category_global_markets"),
        ("https://www.tipranks.com/api/news/posts?per_page=10&topic=dividend-stocks", "topic_dividend_stocks"),
        ("https://www.tipranks.com/api/news/posts?per_page=20&author=tipranks-auto-generated-intelligence-newsdesk", "author_tipranks_auto_generated_intelligence_newsdesk"),
        ("https://www.tipranks.com/api/news/posts?per_page=20&author=tipranksnewsdesk", "author_tipranks_newsdesk"),
        ("https://www.tipranks.com/api/news/posts?per_page=20&author=tiprankshongkongnewsdesk", "author_tipranks_hongkong_newsdesk"),
    ]

    # 第一步：收集所有栏目的第一条新文章
    articles_to_process = []
    for url, filename in categories:
        article_info = collect_first_post(url, filename)
        if article_info:
            articles_to_process.append(article_info)

    # 第二步：循环获取详情并保存
    for article_info in articles_to_process:
        description = get_detail(article_info["link"])
        if description != "":
            save_article(article_info, description)

