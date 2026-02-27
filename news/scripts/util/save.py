# 通过pg包链接 supabase
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# 初始化连接，只执行一次
_pg_connection = None

def get_pg_connection():
    global _pg_connection
    if _pg_connection is None:
        try:
            _pg_connection = psycopg2.connect(
                dbname=os.getenv("SUPABASE_DBNAME"),
                user=os.getenv("SUPABASE_USER"),
                password=os.getenv("SUPABASE_PASSWORD"),
                host=os.getenv("SUPABASE_HOST"),
                port=os.getenv("SUPABASE_PORT")
            )
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            _pg_connection = None
    return _pg_connection

def insert_posts_to_db(posts_data):
    conn = get_pg_connection()
    try:
        with conn.cursor() as cursor:
            insert_query = sql.SQL(
                """
                INSERT INTO posts (title, content, link, pub_date, image, author, source, external_id, uuid, kind, language) 
                VALUES %s
                ON CONFLICT (uuid) 
                DO NOTHING
                """
            )
            values = [
                (
                    post.get("title", ""), 
                    post.get("content", ""), 
                    post.get("link", ""), 
                    post.get("pub_date", ""), 
                    post.get("image", ""), 
                    post.get("author", ""), 
                    post.get("source", ""), 
                    post.get("external_id", ""), 
                    post.get("uuid", ""), 
                    post.get("kind", 1),
                    post.get("language", "zh-CN")
                )
                for post in posts_data
            ]
            execute_values(cursor, insert_query, values)
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data into PostgreSQL: {e}")

def all_posts_uuids():
    conn = get_pg_connection()
    try:
        with conn.cursor() as cursor:
            select_query = sql.SQL("SELECT uuid FROM posts")
            cursor.execute(select_query)
            result = cursor.fetchall()
            # 将结果转换为一维列表
            uuids = [row[0] for row in result]
            return uuids
    except Exception as e:
        print(f"Error selecting uuids from PostgreSQL: {e}")
        return []

def close_pg_connection():
    global _pg_connection
    if _pg_connection is not None:
        _pg_connection.close()
        _pg_connection = None
        print("close pg connection success")
