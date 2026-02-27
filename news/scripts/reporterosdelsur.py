# -*- coding: UTF-8 -*-
import requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": 'pll_language=en; __gads=ID=0f672daa9626460e:T=1755602124:RT=1761902636:S=ALNI_MauLTbnrKS4g_iKd9Fj8RGJ6sXZQA; __gpi=UID=00001182d01c5226:T=1755602124:RT=1761902636:S=ALNI_Mabpe_tmsEPE8JR_gB6pCchMxHhsQ; __eoi=ID=c86647c0936a414c:T=1755602124:RT=1761902636:S=AA-AfjY09jvj-TF7Ip2YnDNCjZLh; __gsas=ID=82470bc1a4b2ac8d:T=1761902637:RT=1761902637:S=ALNI_MZgQfAECPLm8wBDANMX-mBh3neYKQ; FCOEC=%5B%5B%5B28%2C%22%5Bnull%2C%5Bnull%2C1%2C%5B1761902638%2C798552000%5D%2C0%5D%5D%22%5D%5D%5D; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%2208f70b31-11fc-4043-88da-a13f8e7fe552%5C%22%2C%5B1761902637%2C602000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol-n1UpMwzY4XkM8IVvLIPqvHPCn5g5G5VpKGe2GFNcM2XRWDwNKDUwK6ci1Uh0DeseDcphibxewaSdHzb151ubUAQebVEWTPyiKfHAwrVKci73R_JOW2nHMdU4EMtt_hLauT-uJ8EJ2QBVb58rEAzjrRAv6ZA%3D%3D%22%5D%5D; _ga_04DMKL0FPQ=GS2.1.s1761902639$o1$g0$t1761902639$j60$l0$h0; _ga=GA1.1.1127038968.1761902639; cf_clearance=qJgnuPd8rDL38O5VBmC5XhA0ik3CKkLwInDtrBSlCec-1761902641-1.2.1.1-.DwJRf_I_vAKkJPyO3pO3YlSjbmc_XRmHcF3_fJX0n6sBnZZUGq0qsCUZFtUZ_FJG2ePOzNV5VRHMZahaoKG54mw6o5PDi_Z3yfA9jfoWhZfRuieoy.KyYa2EaIuXwmPg6R8dRKkNg9BrBsBHF6L6GGkdFHD6MI1k8aQoB3nNjd5_qGYmr3_XeGFDCay7IFrY_ge82pjZs9jrOE_pSywMGhaaG6NpaZWM3M5FMZzNgI',
}
base_url = "https://www.reporterosdelsur.com/"
filename = "./news/data/reporterosdelsur/list.json"
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one(".entry-content")

        ad_elements = soup.select("div[itemprop='video']")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    # 使用 requests 发送请求
    response = requests.get(
        "https://lisboatv.pt",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.text
        lxml = BeautifulSoup(body, "lxml")
        posts = lxml.select("article")
        for index, post in enumerate(posts):
            if index < 3:
                title = post.select_one("h2 > a").text.strip()
                link = post.select_one("h2 > a")["href"].strip()
                # 判断图片是否存在
                image = post.select_one("figure img")
                if image:
                    image = image["src"].strip()
                else:
                    image = ""
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break
                if util.contains_language(title):
                    continue
                description = get_detail(link)
                if description:
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "reporterosdelsur",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if articles and insert:
            if len(articles) > 10:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error(f"request error: {response.status_code}")

if __name__ == "__main__":
    # util.execute_with_timeout(run)
    util.info("403 Forbidden")
    # detail = get_detail("https://lisboatv.pt/meridas-2025-property-boom-investors-flock-to-yucatans-soaring-market/")
    # util.info(detail)
