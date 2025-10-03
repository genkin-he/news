# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'en;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'AKA_A2=A; _gcl_au=1.1.236061359.1759221026; _ga=GA1.1.2104089670.1759221026; oly_fire_id=6456G7901134A6F; oly_anon_id=fc576103-afbb-44ef-a36c-38badfb1da90; bid-50189-46617_0-100=46617; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.eetimes.com/category/news-analysis/%22%2C%22sref%22:%22%22%2C%22sts%22:1759221027823%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=59b1ce48-7b15-4d8d-ab90-f3513bb026fb%22%2C%22session_count%22:1%2C%22last_session_ts%22:1759221027823}; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2025-09-30%2008%3A30%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.eetimes.com%2Fcategory%2Fnews-analysis%2F%7C%7C%7Crf%3D%28none%29; sbjs_first_add=fd%3D2025-09-30%2008%3A30%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.eetimes.com%2Fcategory%2Fnews-analysis%2F%7C%7C%7Crf%3D%28none%29; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F140.0.0.0%20Safari%2F537.36; tk_or=%22%22; tk_r3d=%22%22; tk_lr=%22%22; tk_ai=2KIE3t0MErHgP262bxVdG1Bi; __gads=ID=1735de1f861e425c:T=1759221028:RT=1759221028:S=ALNI_MZHKHEtyM3hptMnabFjqadXqyzsdw; __gpi=UID=0000119cb2fc1aae:T=1759221028:RT=1759221028:S=ALNI_MbUkX37iGiyC8EC50QTFOkuwzcmfQ; __eoi=ID=437f7c04e702299f:T=1759221028:RT=1759221028:S=AA-AfjZF4x41yN6RRrdGhBoGCVOk; _ga_M9DCV37F0X=GS2.1.s1759221026$o1$g0$t1759221092$j60$l0$h2005549432; _ga_ZLV02RYCZ8=GS2.1.s1759221026$o1$g0$t1759221092$j60$l0$h0; bm_sz=E739AFEE5735971A03F261FE69EFE5E3~YAAQUz0xF67ft22ZAQAAQ07AmR0uWjfo6bmd1/Smg2aiEK9J6Pk+HhLn+7IjBvshUA6DInNsbq3BagIP7e65dwMi3KWHo3efXkiMaumpOdMTwtfOvM4wqICMW3hpy85lqRfUzBj2DRHKB38UwrdG05QuyJdFe3vQp1JSuzXidsVTvAc/5OsC+KyyE23PWNfqRfFqhlQD2sfCHymQeFWew0D8K0rASDaFgT1Kest62cvSHUYARx52hab/n+4BfSbG6F2mrgLfbcHno96TYEKoqY+QNOqv5xxo9hcWZjmDdNIfkUkR76zQ0rD8bqmbKxRRnsla0BvJ4WArVHD6gtCov4H6gEa5GyNbLsMXvAuc3imJA0lfDu2DNoD9Rm4uYA08YiEJtQ9zHoMS8RfiDOse4xzfQWLrof5bU1xW5xGv/34PE3fq~3293491~4408130; FCNEC=%5B%5B%22AKsRol8WjBg3p2Gef-_gbfXLeIDsZPXQAKu-_lMvLqQ57zYLdLUN0EwzuDo_JbmqGlHm0F3L6uywFkelTG0m-mCeZ2fcucoCVNSx7LFZZfxJUyHU9BEnpryB96hJ2z5YIzt6hvRMxWLkrhMK7UsYd6HexrwoLEFftg%3D%3D%22%5D%5D; sbjs_session=pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.eetimes.com%2Fcybersecurity-expectations-peak-as-genai-lands-in-the-trough%2F; tk_qs=; bm_mi=4BA50E6238A68EBC4C0934CDDBD2B2B4~YAAQUz0xF9sCuG2ZAQAAVKDAmR1hGmx/8IQUWgh63hZBiK/rfvDKVK0tnflFGl4BkiuaS0Bbp/nKKgrvGk3F59iAbE5dfjD2hJ40wonokh6r9b27OHZZG+Z7Vpm5UQHSj3fjludIyXRHaiML6u8qKextILNDW3bOGyCUwZS+xsSNb3siCjF9JWpDbXJvlQqxeKrk/5+OeIRkk7mVQd8lQEba7ttGHFA4KrgRRA1e4HyvTv0xmaZjGJpRhFeL6t+j9WGFUnIni++00/TSgcy8K/sU5UZkibH7DhM2p/RDw865qH3Xz7QcAejUnfUOBLynyrN4FNTpqVVBNO0iRmcNwok+xtPG7b8n2kl6gWwIDnN3KCoZORlNYAyNExIfQ7Ve8Q==~1; ak_bmsc=607C1A139F3593527A93C82EA66E874F~000000000000000000000000000000~YAAQTj0xFyOckpaZAQAA3bvAmR17bIbDrd5CajJwGfXy540YebEWar9E1ongvsjcachOsJT1j8WgUJ7Njc5xKDlYiaHWeyX/tFcq+Y2iDWPGr7GVRuy8IlvpJGaixnXpbM1f7Ygz5ySCd2xccjr5YTa+/NDxOUN4XnsZWy5rPX9jIYLf2ffmvY8GcvUcf8xKzKRL+lfUsOSxv99y+w6nv5mMxE2h/lvZeEcTO7J0e3WIBYngrqeTNvKqH7bYAzxEsYIR7D3yhiIM1T0PTSl5HBlQC5q/rTGXlxRw7go9aaOyCHd1MXqDa//Qgpkz3PzleU88DCemnHyZXvYrMWIJS8vR6gSY4xWO+48+zDtsBuKV96dldi/lX8/py3wjBT+4ZUSeZCL6R4DyK5ckwiSgkX2y74AK+VZFePiZ6DQd6J2GlHX9LHe7pNlpIlxZLlyVte0f88hPVS02PKz4RvtEF5xp+H0lnqz5+dK3rX7gQ/o+NAZhJAZ4C7V61A2SgxrAmCBRDCF8atzevKH9P2zREGk4X1XY5QqOXuA9NhJQDzwIDDPW//w=; _abck=A89D944F2FB7E1A170D9144D06D3FD38~-1~YAAQTj0xFyidkpaZAQAA1rzAmQ5138VxaTb80gZ+TSY8G3hxkN29A1JDQP14UzCY6eFQAaSvPuo9BetGDY7LVpWMgpp8uYsVM5WF/INerL3KV+Ga8K0yCZV6GLhw7j92GF7eY9whuesGTf9Cu7uranRNoqLWyMRf9tEB3qytsOPBvVDX2wxt43BV0YxlXUvvY9mQ1p3dFoJkjH0oiZAkohGgybHo4dqLA9K0aVR3SOC1N/UJMfp8AKy3Hk3HjYxhOVPKrmjBjovz76G7jueJV8LvElEUl4Pxb9DOW05F2+cJZQKziVC0hSGNxpS20dQo/xEF9zn2Gv880LOFOSTmoVwPrnoQr4sKtWD5CYNNUw6ld5cajMCHPR6GUPuoZWQttFJBx9NNfhU17sIgqRYEhnn2fCdgXpwg+/QPpLNjwVBKhfRAjwikCWbi8u1HJh9qP4NGxPZHBX8cHwsqLFePxjbRa4VIvVcIeq7mBHpgUB2I/7w/aTNYi0lyc5Y9rkDIjFMM+cgvaAcxiVc0E1PsDTA3ogOIp+9iFM3Z52YD16PMV2mwVQ7DuF4FcDLmdPXYyu4/flDJwjKzKENt2GLiA48jMipIh9jSeUxeh+ObSF4=~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f83Rf2I15DNCe5YLkuD4AG3LkedcH9pBROeGGyDb4dGHgkkPQr3AnBP1buBhz4+mrOjiyYnxCgbC+TbKLpDvAXo77UuRjGhKzQPp~-1; bm_sv=B25B11F024393B32E4E2B17EFFF65407~YAAQTj0xF8SmkpaZAQAA2snAmR2z3hC5ZOgfLlUDISgkuBu+t8s3YO1AgMHnXvKvWBTeFldYocRrEjixzYGO9+wH2E7VjW3G3PZunMsAETxkvJz5zheHQg4Wc5ZinBh3LkiPnHuN1ZgL0uDyDbHD49a7H7rWBzikl+81meDf2YaYIDziTL1619xJCrBoeLCWoYnFd4LWL5Q8NYxPAgllACYmFrBKjHZCAPgiKhy+Oo9YBvoUy4iRuaqfEt3Ml0XAIw==~1',
}

base_url = "https://www.eetimes.com"
filename = "./news/data/eetimes/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def parse_rss_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)

        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'media': 'http://search.yahoo.com/mrss/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'wfw': 'http://wellformedweb.org/CommentAPI/',
            'sy': 'http://purl.org/rss/1.0/modules/syndication/',
            'slash': 'http://purl.org/rss/1.0/modules/slash/'
        }
        items = []

        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')

            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""

                if title and link:
                    items.append({
                        'title': title,
                        'link': link
                    })

        return items
    except Exception as e:
        util.error("解析 RSS 时发生错误：{}".format(e))
        return []

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one("div.articleBody")
        if soup is None:
            return ""
        ad_elements = soup.select("div, script")
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        rss_items = parse_rss_xml(resp)
        for item in rss_items:
            if post_count >= 2:
                break
            link = item['link']
            title = item['title']
            util.info("link: {}".format(link))
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            util.info("title: {}".format(title))
            if title == "":
                continue
            post_count = post_count + 1
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "investors",
                        "kind": 1,
                        "language": "en-US",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.eetimes.com/category/news-analysis/feed/")
