# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "referer": 'https://www.insidermonkey.com/blog/category/news/',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": '_gid=GA1.2.509540211.1761552121; prism_69633062=73077a89-f5aa-4ca2-9a70-cb260eaf7e54; g_state={"i_l":0,"i_ll":1761552319464,"i_b":"a3180AqeHsdIDFCyMOdXaZk9fP5uZUyKrR//JYmqazI"}; _pn=eyJzdWIiOnsidWRyIjowLCJpZCI6ImhBTlFuQzVQRUROSFJZMUp2RFhNNHg5TWYzQXp1ZmVYIiwic3MiOjEsImRzZSI6MTc2MjE1ODk5NjQ5Nn0sImx1YSI6MTc2MTU1NDE5NjQ5Nn0; _ga=GA1.2.585552331.1761552121; __gads=ID=dde67c7acc19cfdc:T=1761552121:RT=1761554211:S=ALNI_Mb7ZSP6UbLuQPU7UhtQcEarHQtHfA; __gpi=UID=000011aa45e47441:T=1761552121:RT=1761554211:S=ALNI_Makco1Hji6EqHpyGGrdyOWXSkEaTg; __eoi=ID=b18197474df27ac6:T=1761552121:RT=1761554211:S=AA-AfjZCjHbYTJ-ppY1RWR3czjv4; FCNEC=%5B%5B%22AKsRol-ruMzPpeuCwz5XhEzGdW9OCG0A9L1fiD5HEthxu7ics03XViPUhM6c7CmnfZDAKqUxFuirkHK7FOPo6iPXCwRDQC60eihJSdIktlYiiODCu0-WqS1by-kl_Tre0x1VY_YFdWVqoqofzsdbDErPAhvTyMgBuw%3D%3D%22%5D%5D; _ga_VESG0SN62K=GS2.1.s1761563711$o2$g0$t1761563711$j60$l0$h0; aws-waf-token=629cd88e-27e7-4db4-a45f-cd85178f5b4d:EwoApD1O/8UKAAAA:ANJO7K5KeoASEt3zqC1vNACyLV93nfykPE8WEBjP5jz6KebngjzUtaaxu6gSf1NjNCymfAe8tnlPhRe9lUvjAte1pvm0rCJQUqrYCZ8tNnQCGoAAVrSve44gAWZroybHwSNcoMXcRhGFK2Mpwtsq1ORR5cCIalYP+gwkLUWuNS0cD2vxErxiwxxwnCNhBGON14gczhjH+1Y='
}

base_url = "https://www.insidermonkey.com"
filename = "./news/data/insidermonkey/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        if "Access Restricted" in resp or "JavaScript is disabled" in resp or "challenge-container" in resp:
            raise Exception("AWS WAF protection detected") 
        body = BeautifulSoup(resp, "lxml")
        # Try different content selectors for InsiderMonkey
        content_wrappers = body.select(".entry-content, .post-content, .article-content, .content")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            # Remove unwanted elements
            ad_elements = soup.select("script, style, .ad, .advertisement, .ads, .social-share, .related-posts")
            for element in ad_elements:
                element.decompose()

        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run(url):
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    util.info("Response status: {}, headers: {}".format(response.status_code, dict(response.headers)))
    
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        util.info("Response body preview: {}".format(body[:500]))
        if "Access Restricted" in body or "JavaScript is disabled" in body or "challenge-container" in body or "aws-waf" in body.lower():
            util.error("AWS WAF protection detected, cannot scrape")
            return
    elif response.status_code == 202:
        util.error("AWS WAF challenge page received (202), cannot scrape")
        return
    else:
        util.error("Unexpected response code: {}".format(response.status_code))
        return
    
    soup = BeautifulSoup(body, "lxml")
    # Try different selectors for InsiderMonkey article links
    nodes = soup.select("h2 a, h3 a, .entry-title a, .post-title a, .article-title a")
    util.info("nodes: {}".format(len(nodes)))
    for node in nodes:
        if post_count >= 3:
            break
        link = str(node["href"])
        if not link.startswith("http"):
            link = base_url + link
        title = str(node.text)
        title = title.replace('\n', '').strip()
        if link in ",".join(links):
            util.info("exists link: {}".format(link))
            continue
        description = ""
        try:
            description = get_detail(link)
        except Exception as e:
            util.error("request: {} error: {}".format(link, str(e)))
            if "AWS WAF protection detected" in str(e):
                break
        if description != "":
            post_count = post_count + 1
            insert = True
            articles.insert(
                0,
                {
                    "title": title,
                    "description": description,
                    "link": link,
                    "author": "insidermonkey",
                    "pub_date": util.current_time_string(),
                    "source": "insidermonkey",
                    "kind": 1,
                    "language": "en",
                },
            )
    if len(articles) > 0 and insert:
        if len(articles) > 20:
            articles = articles[:20]
        util.write_json_to_file(articles, filename)

if __name__ == "__main__":
    # 202 AWS WAF challenge page received (202), cannot scrape
    # util.execute_with_timeout(run, "https://www.insidermonkey.com/blog/category/news/")
