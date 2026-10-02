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
    "cookie": '_gcl_au=1.1.236061359.1759221026; _ga=GA1.1.2104089670.1759221026; oly_fire_id=6456G7901134A6F; oly_anon_id=fc576103-afbb-44ef-a36c-38badfb1da90; bid-50189-46617_0-100=46617; tk_or=%22%22; tk_lr=%22%22; tk_ai=2KIE3t0MErHgP262bxVdG1Bi; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2025-10-15%2007%3A42%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.eetimes.com%2Fcategory%2Fnews-analysis%2F%7C%7C%7Crf%3D%28none%29; sbjs_first_add=fd%3D2025-10-15%2007%3A42%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.eetimes.com%2Fcategory%2Fnews-analysis%2F%7C%7C%7Crf%3D%28none%29; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F141.0.0.0%20Safari%2F537.36; _abck=A89D944F2FB7E1A170D9144D06D3FD38~0~YAAQGJ46Fx3eYqSZAQAAz/7R5g5b68GTVyl2HaFyu8z5bT/DQjqkw1VaHjgY/BzNU1mMTxDvTT0Q8e0ZktNUrq++BmZc0KPDxC6xJD5gQviPPmtV6dELcZkUTrZtCwF6L9BK4i5PCBV+He4iOdNy/IRg0os7Z462lBFAQ8Q6eCJ9WoLWWcJGvCBn7uFXL4Vpm/NGkmnhOJOkvTWW9c2/WPRcQWxfA9LXUiHStwx4RmVPncPxAfyKKcGLme6VzFg4wtngQbqzFCg49AJNa6iKhYjQLfm7zODtPC3g7vo5PhCaHx1CxTMeSeA/zzzGOTBLF2/jZmpbgTsSJhAvOy6bdu6TKPU/UPjb8mnYBfvWMREuYYIaSlYcurVJB/BeH7ilkm7vbQcWQNQsF/5JxdE6+Rr0r5+IsmNHqjW/29pAYNa1Ukky+Yt44jv7j6wFK6zvLBkDY5YUQ6bkoEy4fCNvEaj+ELG4oUJuk/3Nl91RJH+kiV+NcaAPxm6vPZBm/o38gyXmYvu0MsP3q6p9hmB3LmlymSgxUVmwwyZ9WD2zWg34c0LfFxat1JMjvTo+0s+lMX0oLC81axot5BbaFaKR7DMYJE/t0S9dgSfTAtO5DkRKZrN5nmRSvQ9n+DtVIUMYIQYuqMc=~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f+G4nYJoPGZnowDsg0gg16Rhb+IVlSzU5mg0jqlrX7Qc+cm6Xq+iW1p3oDKGlorS+a%2fnv21mY0fTrshYwUD16%2fuwWyPTLjKbgOg8~-1; tk_r3d=%22%22; _ga_ZLV02RYCZ8=GS2.1.s1760514146$o2$g1$t1760514176$j30$l0$h0; _ga_M9DCV37F0X=GS2.1.s1760514146$o2$g1$t1760514176$j30$l0$h369032400; FCNEC=%5B%5B%22AKsRol8Fy5C6URfCVQ0dHfrtGnXgQJwIaJLkdLyyL4FV97NbgnCr3l-JbOpt2iboPIsr0ID_Fa0Qb0f4EdREzsyfONaHReWEC2BK0GHkLo51A0sXJSQV0MledkghMMS7uUb1fYXM5WHGccuQa2GMCTXQaLjNplh3tQ%3D%3D%22%5D%5D; _parsely_visitor={%22id%22:%22pid=59b1ce48-7b15-4d8d-ab90-f3513bb026fb%22%2C%22session_count%22:3%2C%22last_session_ts%22:1760516350432}; __gads=ID=1735de1f861e425c:T=1759221028:RT=1760516950:S=ALNI_MZHKHEtyM3hptMnabFjqadXqyzsdw; __gpi=UID=0000119cb2fc1aae:T=1759221028:RT=1760516950:S=ALNI_MbUkX37iGiyC8EC50QTFOkuwzcmfQ; __eoi=ID=437f7c04e702299f:T=1759221028:RT=1760516950:S=AA-AfjZF4x41yN6RRrdGhBoGCVOk',
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
