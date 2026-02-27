# -*- coding: UTF-8 -*-
import traceback
import urllib.request  # 发送请求
import json
import re
import logging
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'no-cache',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"142.0.7444.176"',
    "sec-ch-ua-full-version-list": '"Chromium";v="142.0.7444.176", "Google Chrome";v="142.0.7444.176", "Not_A Brand";v="99.0.0.0"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    "Cookie": 'personal-message=none; tr-plan-id=0; tr-plan-name=free; tr-experiments-version=1.14; tipranks-experiments=%7b%22Experiments%22%3a%5b%7b%22Name%22%3a%22general_A%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_B%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_C%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%5d%7d; tipranks-experiments-slim=general_A%3av2%7cgeneral_B%3av2%7cgeneral_C%3av2; test_group_a=v2; test_group_b=v2; _ga=GA1.1.340535434.1763522253; _gcl_au=1.1.144633351.1763522253; FPAU=1.2.1615411389.1763522253; _fbp=fb.1.1763522253590.199669018349474595; usprivacy=1YNY; _lr_env_src_ats=false; _cc_id=fa5c70c9325d0645349027e1fcf981b6; _scor_uid=f84e6cfb60ad4a48aeabe6416c300be2; prism_90278194=2803521e-cd6e-439f-9fcb-028a54b9ae75; _li_dcdm_c=.tipranks.com; _lc2_fpi=63104890847c--01k4brhr9yrp2nr1zp48586xkv; _lc2_fpi_meta=%7B%22w%22%3A1757036470590%7D; panoramaId_expiry=1764904162625; panoramaId=6f567c02a1b2add20c71c9c9bdb716d539382cfb5f52072a297d0912055d3bc0; distinct_days=["2025-11-19","2025-11-28"]; g_state={"i_l":0,"i_ll":1764314088222,"i_b":"JZ1pbX/STaKv8rMzWXD5c2B8S1L5jY0o6X9s1Ul4Rw0"}; _tfpvi=NTAyNGMyNDAtZDA2NC00Y2YxLWExMWMtNzU5ZTUzZDY5OWU1IzktMw%3D%3D; __gads=ID=7146033084cdff62:T=1763522275:RT=1764315872:S=ALNI_Ma7vp35Kfm4po0a0C-YZYTfEarbag; __gpi=UID=000011b8c9e57216:T=1763522275:RT=1764315872:S=ALNI_MZ5a3_ztfv76lkq90Z34GNGlqp7kg; __eoi=ID=6471c64dbacbbe1e:T=1763522275:RT=1764315872:S=AA-AfjZoHL7Iqj-DS7HqQVTbkyog; _ga_FFX3CZN1WY=GS2.1.s1764313997$o2$g1$t1764315903$j59$l0$h68896230; __cf_bm=LMRpK_fMgrnSe9G40AfcMtzUag7B35f7vKIuXIKJzCw-1764732949-1.0.1.1-BgsmnT8vQIqw3TF7C66b7vA_aDUmP8Gv2sYovE21gRXA.JK2cLA.By_RoOpVQ8Z.CuTpG6TTaNfxiP3emdtD.JJc0wm.WN4SpsIo_tQHlCg; cf_clearance=L3czIeis_bGj1vn7W2DOGrIPaKkc3NocDM6zht4zsR8-1764732956-1.2.1.1-26QizDU_3.JmKjHlwBuvTHYXIg6OqoXz1beCv8A36AFN_NbtkB1eMX9cBInv44tYYCRdlf2O_3TlflU6ttwW53NQu4KC2xDAH29GSwkn18QA9gSyzyz5HeOD7VHpY0LSRXli1gYvYehBfZAP5eUfiJmH27dBGS0kzhJT.hm4aoAAF3m3FvVY6U4NGybc6kULVdpoRlqAtzv8LE2KuCECq94hsl.3p4eGG7K.mt9Ar7k',
}
base_url = "https://tipranks.com"
filename = "./news/data/tipranks/list.json"


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
    return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    request = urllib.request.Request(
        "https://tr-cdn.tipranks.com/bff/prod/header/payload.json",
        None,
        headers
    )
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["posts"]
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
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
