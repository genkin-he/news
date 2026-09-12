# -*- coding: UTF-8 -*-
import logging
import traceback
import json
import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "referer": "https://www.scmp.com/",
}

base_url = "https://www.scmp.com"
filename = "./news/data/scmp/list.json"
util = SpiderUtil()

# 三个栏目的 URL 配置
section_urls = [
    {
        "name": "business_companies",
        "url": "https://www.scmp.com/business/companies?module=Companies&pgtype=section",
        "category": "business"
    },
    {
        "name": "tech",
        "url": "https://www.scmp.com/tech?module=oneline_menu_section_int&pgtype=section",
        "category": "tech"
    },
    {
        "name": "hong_kong",
        "url": "https://www.scmp.com/news/hong-kong?module=oneline_menu_section_int&pgtype=live",
        "category": "hong-kong"
    }
]


def get_detail(link):
    """获取文章详细内容"""
    util.info("news: " + link)
    try:
        response = requests.get(
            link,
            headers=headers,
            timeout=10,
            proxies=util.get_random_proxy(),
            impersonate="chrome110"
        )
        if response.status_code == 200:
            body = response.text
            # 尝试从 JSON-LD 中提取 articleBody
            if 'articleBody' in body:
                try:
                    # 查找 JSON-LD 格式的数据
                    match = re.search(r'"articleBody"\s*:\s*"([^"]+)"', body)
                    if match:
                        result = match.group(1)
                        # 解码转义字符
                        result = result.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
                        return result
                except:
                    pass
            # 如果 JSON-LD 方法失败，尝试从 HTML 中提取
            soup = BeautifulSoup(body, "lxml")
            # 查找文章内容区域
            content_elem = soup.select_one('article, .article-body, .article-content, [itemprop="articleBody"]')
            if content_elem:
                # 移除不需要的元素
                for element in content_elem.select("script, style, iframe, noscript, .ad, .advertisement"):
                    element.decompose()
                return str(content_elem).strip()
            return ""
        else:
            util.error(f"request error: {response.status_code}")
            return ""
    except Exception as e:
        util.error(f"Error fetching article content: {str(e)}")
        return ""


def fetch_posts_from_section(section_config):
    """从指定栏目获取文章列表"""
    url = section_config["url"]
    util.info(f"Fetching from {section_config['name']}: {url}")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
            proxies=util.get_random_proxy(),
            impersonate="chrome110"
        )
        if response.status_code != 200:
            util.error(f"Failed to fetch {url}: status {response.status_code}")
            return []

        body = response.text
        posts = []

        next_data_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.DOTALL)
        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                # 查找文章数据
                props = next_data.get("props", {}).get("pageProps", {})
                
                # 尝试不同的数据路径
                contents = props.get("contents", {})
                if contents and isinstance(contents, dict):
                    edges = contents.get("edges", [])
                    for edge in edges:
                        if len(posts) >= 3:
                            break
                        node = edge.get("node", {})
                        if node.get("headline") and node.get("urlAlias"):
                            posts.append({
                                "title": node["headline"],
                                "link": base_url + node["urlAlias"]
                            })
                
                # 尝试其他路径
                if not posts:
                    for key in ["data", "initialData", "pageData"]:
                        if len(posts) >= 3:
                            break
                        data = props.get(key, {})
                        if isinstance(data, dict):
                            contents = data.get("contents", {})
                            if contents and isinstance(contents, dict):
                                edges = contents.get("edges", [])
                                for edge in edges:
                                    if len(posts) >= 3:
                                        break
                                    node = edge.get("node", {})
                                    if node.get("headline") and node.get("urlAlias"):
                                        posts.append({
                                            "title": node["headline"],
                                            "link": base_url + node["urlAlias"]
                                        })
                                if posts:
                                    break
            except Exception as e:
                util.error(f"Error parsing __NEXT_DATA__: {str(e)}")

        if not posts:
            soup = BeautifulSoup(body, "lxml")
            # 查找文章链接 - 更精确的选择器
            article_links = soup.select('a[href*="/article/"]')
            seen_links = set()

            for link_elem in article_links[:30]:
                href = link_elem.get("href", "")
                if not href or href.startswith("#"):
                    continue
                # 构建完整 URL
                if href.startswith("/"):
                    full_url = base_url + href
                elif href.startswith("http"):
                    full_url = href
                else:
                    continue
                # 确保是文章链接
                if "/article/" not in full_url:
                    continue
                if full_url in seen_links:
                    continue
                seen_links.add(full_url)
                # 获取标题 - 尝试多种方式
                title = link_elem.get_text(strip=True)
                if not title or len(title) < 10:
                    # 尝试从 aria-label 或 title 属性
                    title = link_elem.get("aria-label") or link_elem.get("title", "")
                    if not title:
                        # 尝试从父元素获取
                        parent = link_elem.find_parent(["h1", "h2", "h3", "h4", "div"])
                        if parent:
                            title = parent.get_text(strip=True)
                if title and len(title) > 10:
                    posts.append({
                        "title": title[:200],  # 限制标题长度
                        "link": full_url
                    })
                    # 每个栏目只取前 3 条
                    if len(posts) >= 3:
                        break
        # 确保每个栏目最多返回 3 条
        posts = posts[:3]
        util.info(f"Found {len(posts)} posts from {section_config['name']}")
        return posts
    except Exception as e:
        util.error(f"Error fetching section {section_config['name']}: {str(e)}")
        traceback.print_exc()
        return []


def run():
    """主函数：爬取三个栏目的数据"""
    data = util.history_posts(filename)
    articles = data["articles"]
    urls = data["links"]
    insert = False

    all_posts = []

    # 从三个栏目获取文章
    for section in section_urls:
        posts = fetch_posts_from_section(section)
        all_posts.extend(posts)

    util.info(f"Total posts found: {len(all_posts)}")

    processed_count = {}
    for post in all_posts:
        link = post["link"]
        section_name = None
        for section in section_urls:
            if section["category"] in link:
                section_name = section["name"]
                break
        if not section_name:
            continue
        # 每个栏目最多处理 3 篇
        if processed_count.get(section_name, 0) >= 3:
            continue
        if link in ",".join(urls):
            util.info("exists link: " + link)
            continue
        title = post["title"]
        description = get_detail(link)
        if description != "":
            insert = True
            processed_count[section_name] = processed_count.get(section_name, 0) + 1
            articles.insert(
                0,
                {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "scmp",
                    "kind": 1,
                    "language": "en",
                },
            )
            util.info(f"Added article from {section_name}: {title[:50]}")

    if len(articles) > 0 and insert:
        if len(articles) > 20:
            articles = articles[:20]
        util.write_json_to_file(articles, filename)
        util.info(f"Saved {len(articles)} articles")


if __name__ == "__main__":
    util.execute_with_timeout(run)
    # detail = get_detail("https://www.scmp.com/news/hong-kong/society/article/3330763/bear-attacks-japan-why-are-they-rising-and-how-can-hongkongers-stay-safe")
    # util.info("detail: {}".format(detail))
