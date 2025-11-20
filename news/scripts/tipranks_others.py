# -*- coding: UTF-8 -*-
import traceback
import urllib.request  # 发送请求
import json
import re
import logging
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": '__cf_bm=XIMIM8b3RKm2yIf_JROFWlsUsT521UznX4msn2Lxu_g-1763521973-1.0.1.1-W9ijit8MhGaPEiADczUrfFiiQCbkaNWK93DEfLu7OWfFB43LHQYlWNh4KAu5OQ0bxMM7_CRFfNQJPZB2M4r6mw8K8maiYireyacBzo0urIk; personal-message=none; tr-plan-id=0; tr-plan-name=free; tr-experiments-version=1.14; tipranks-experiments=%7b%22Experiments%22%3a%5b%7b%22Name%22%3a%22general_A%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_B%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_C%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%5d%7d; tipranks-experiments-slim=general_A%3av2%7cgeneral_B%3av2%7cgeneral_C%3av2; distinct_days=["2025-11-19"]; test_group_a=v2; test_group_b=v2; _ga=GA1.1.340535434.1763522253; _gcl_au=1.1.144633351.1763522253; FPAU=1.2.1615411389.1763522253; _fbp=fb.1.1763522253590.199669018349474595; usprivacy=1YNY; _li_dcdm_c=.tipranks.com; _lc2_fpi=63104890847c--01k4brhr9yrp2nr1zp48586xkv; _lc2_fpi_meta=%7B%22w%22%3A1757036470590%7D; _lr_retry_request=true; _lr_env_src_ats=false; panoramaId_expiry=1764127054845; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId=7ae457095db1f8ad248d04f150c1185ca02c79e6ed66d2b1dab9fc44f66b4657; _scor_uid=f84e6cfb60ad4a48aeabe6416c300be2; prism_90278194=2803521e-cd6e-439f-9fcb-028a54b9ae75; __gads=ID=7146033084cdff62:T=1763522275:RT=1763522275:S=ALNI_Ma7vp35Kfm4po0a0C-YZYTfEarbag; __gpi=UID=000011b8c9e57216:T=1763522275:RT=1763522275:S=ALNI_MZ5a3_ztfv76lkq90Z34GNGlqp7kg; __eoi=ID=6471c64dbacbbe1e:T=1763522275:RT=1763522275:S=AA-AfjZoHL7Iqj-DS7HqQVTbkyog; DontShowPopupCampaign=true; g_state={"i_l":0,"i_ll":1763522428843,"i_b":"40Ebf+vy/cGemrXXa0PgC+kN5FNSLPygptE2dXd1Z1A"}; _tfpvi=YmYzOTQ4MzUtZjIwZi00MzNjLTg2YmEtMmQwNGY1MjgwMGU3Iy00LTE%3D; _ga_FFX3CZN1WY=GS2.1.s1763522252$o1$g1$t1763522433$j4$l0$h1623474745',
}
base_url = "https://tipranks.com"
base_path = "./news/data/tipranks/{}.json"


def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = response.read().decode("utf-8")
    items = body.split("document.querySelectorAll")
    if len(items) > 1:
        body = items[1]
    else:
        return ""
    result = re.findall(".*window.__STATE__=JSON.parse\\((.*)\\);*", body)
    if len(result) > 0:
        resp = json.loads(result[0])
        result = re.findall('.*content":(.*),"date:*', resp)
        if len(result) > 0:
            result = eval(result[0])
            result = re.sub(r"(\n)\1+", "\n", result)
            # 删除从 <html><head></head><body> 到 Unlock powerful investing tools... 的整个段落
            promo_pattern = r'<html><head></head><body>.*?Unlock powerful investing tools, advanced data, and expert analyst insights to help you invest with confidence\.\n</li></ul>'
            result = re.sub(promo_pattern, '', result, flags=re.DOTALL)
            # 删除 <p>See more insights into 之后的所有内容
            see_more_pattern = r'<p>See more .*'
            result = re.sub(see_more_pattern, '', result, flags=re.DOTALL)
            for_detailed_pattern = r'\n<p></p><p>For detailed.*'
            result = re.sub(for_detailed_pattern, '', result, flags=re.DOTALL)
            body_html_pattern = r"\n</body></html>.*"
            result = re.sub(body_html_pattern, '', result, flags=re.DOTALL)
            extra_content_pattern = r'\n<p></p><div class=\"tipranks-extra-content\"><a href=\"https://www\.tipranks\.com/.*'
            result = re.sub(extra_content_pattern, '', result, flags=re.DOTALL)
            trending_pattern = r'\n<div id=\"trending\" class=\"trending-posts\"><h2 class=\"fontWeightsemibold textDecorationunderline\">Trending Articles.*'
            result = re.sub(trending_pattern, '', result, flags=re.DOTALL)
            figure_pattern = r'\n<figure.*'
            result = re.sub(figure_pattern, '', result, flags=re.DOTALL)
            return result

def collect_first_post(url, filename):
    """收集每个栏目的第一条新文章，不获取详情"""
    filepath = base_path.format(filename)
    data = util.history_posts(filepath)
    links = data["links"]

    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
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
        util.log_action_error("request error: {}".format(response))
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

