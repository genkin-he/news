# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import re
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'personal-message=none; tr-plan-id=0; tr-plan-name=free; tr-experiments-version=1.14; tipranks-experiments=%7b%22Experiments%22%3a%5b%7b%22Name%22%3a%22general_A%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_B%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%2c%7b%22Name%22%3a%22general_C%22%2c%22Variant%22%3a%22v2%22%2c%22SendAnalytics%22%3afalse%7d%5d%7d; tipranks-experiments-slim=general_A%3av2%7cgeneral_B%3av2%7cgeneral_C%3av2; distinct_days=["2025-11-19"]; test_group_a=v2; test_group_b=v2; _ga=GA1.1.340535434.1763522253; _gcl_au=1.1.144633351.1763522253; FPAU=1.2.1615411389.1763522253; _fbp=fb.1.1763522253590.199669018349474595; usprivacy=1YNY; _lr_env_src_ats=false; _cc_id=fa5c70c9325d0645349027e1fcf981b6; _scor_uid=f84e6cfb60ad4a48aeabe6416c300be2; prism_90278194=2803521e-cd6e-439f-9fcb-028a54b9ae75; g_state={"i_l":0,"i_ll":1763522428843,"i_b":"40Ebf+vy/cGemrXXa0PgC+kN5FNSLPygptE2dXd1Z1A"}; _ga_FFX3CZN1WY=GS2.1.s1763522252$o1$g1$t1763522769$j60$l0$h1623474745; __cf_bm=dpcxx0WNXWVLF5Woo6798ix3pXsDd.ZmirZ1rqX_e4s-1764298646-1.0.1.1-rJ7Jn2u6opyrjLgKZlBIw4v21NOGUs9xqWb.8GPIyIX0dcKpGwunlDIyibqOZ__ybZWZiT8Za_wVE1PpHAUHsPZ1wxFskKLZGm5xy3ST9G4; cf_clearance=CTIBLd3imCtbMemjOjoxntGXx7PmIi9Btv3lzehNUwM-1764299185-1.2.1.1-B1HvQ_JH2YXhl18PJCcMJsBn5BrjmUvnYQXfW_Lt1HFDmOW.XhmlFB9VtZGUhLw_Pt13G0C9IY5CTOPRCpYsFyMAXYpLWkBZ_AOIXryNF4B3GdjbXzVzCTLxb_BR6uN.KKpBISO91UfMt2fX9bZV2loZJctikRMfUaT_1jNMhxOE4hF7hekbWW_9t30L4wWcK2ZH_yzja92bl4wni4mWiWazJV1ZcO_w5Zi7ib6GbWY; _li_dcdm_c=.tipranks.com; _lc2_fpi=63104890847c--01k4brhr9yrp2nr1zp48586xkv; _lc2_fpi_meta=%7B%22w%22%3A1757036470590%7D; _lr_retry_request=true; panoramaId_expiry=1864904162625; panoramaId=6f567c02a1b2add20c71c9c9bdb716d539382cfb5f52072a297d0912055d3bc0; _tfpvi=NTA2ZGVjMDYtMWQ4Ny00ZmY2LWI3YTctNGU2NjViMmI1NWQ5IzAtNQ%3D%3D; DontShowPopupCampaign=true; __gads=ID=7146033084cdff62:T=1763522275:RT=1764299978:S=ALNI_Ma7vp35Kfm4po0a0C-YZYTfEarbag; __gpi=UID=000011b8c9e57216:T=1763522275:RT=1764299978:S=ALNI_MZ5a3_ztfv76lkq90Z34GNGlqp7kg; __eoi=ID=6471c64dbacbbe1e:T=1763522275:RT=1764299978:S=AA-AfjZoHL7Iqj-DS7HqQVTbkyog',
}
base_url = "https://tipranks.com"
filename = "./news/data/tipranks/announcements.json"


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers, proxies=util.get_random_proxy(), timeout=30)
    response.raise_for_status()
    body = response.text
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
            see_more_pattern = r'\n<p></p><p><p>See more.*'
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


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(
        "https://www.tipranks.com/api/news/posts?per_page=5&category=company-announcements",
        headers=headers,
        proxies= util.get_random_proxy(),
        timeout=30,
    )
    if response.status_code == 200:
        body = response.text
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 1:
                post = posts[index]
                id = post["_id"]
                title = post["title"]
                image = ""
                if "image" in post and post["image"]:
                    image = post["image"]["src"]
                link = post["link"]
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
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "author": author,
                            "pub_date": pub_date,
                            "source": "tipranks_announcements",
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
    # if util.should_run_by_minute(5):
        util.execute_with_timeout(run)
