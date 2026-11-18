from util import history_posts, md5
from save import all_posts_uuids, close_pg_connection, insert_posts_to_db
import os
import subprocess
from datetime import datetime, timedelta
import glob


def save_posts():
    # 获取当前文件所在目录的上级目录
    current_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # 拼接数据目录路径
    data_dir = os.path.join(current_dir, "data")
    # 获取所有json文件路径
    filepaths = glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True)
    uuids = all_posts_uuids()
    insert_posts = []
    for filepath in filepaths:
        data = history_posts(filepath)
        if len(data["articles"]) > 0:
            for article in data["articles"]:
                if "kind" not in article:
                    print("file: ", filepath, "article: ", article, "kind not in article")
                    article["kind"] = 1
                if not isinstance(article["kind"], (int)):
                    article["kind"] = 1

                insert_post = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "link": article.get("link", ""),
                    "pub_date": article.get("pub_date", ""),
                    "source": article.get("source", ""),
                    "kind": article.get("kind", 1),
                    "language": article.get("language", ""),
                }

                # 可选字段
                if "id" in article:
                    insert_post["external_id"] = article["id"]
                if "image" in article:
                    insert_post["image"] = article["image"]
                if "author" in article:
                    insert_post["author"] = article["author"]
                if article["link"]:
                    insert_post["uuid"] = md5(article["link"])
                    
                if insert_post["uuid"] not in uuids:
                    insert_posts.append(insert_post)
        else:
            print("filepath: ", filepath, "articles: ", data["articles"])

    if len(insert_posts) > 0:
        insert_posts_to_db(insert_posts)
    close_pg_connection()

save_posts()
