# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts, parse_time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'ptrc=CAESEFo_A_Gv8j1dPyKSQKNLNw0; ptrpp=tPH2rxCPrPk4; ptrunl=RX-19266edd-7887-4190-a63f-71bbe422b67c-004; ptran=4484792103042527105; ptrt=ae123e0e-825b-46bf-bafa-7c4285fbdf94; ptrpub=291C1083-9491-4499-8305-DB615033772C; ptrrhs=C9LrrLKOl4YLO5HzuFr5dipCr1V3dQHsb2z4QgXpAds; ptrcriteo=9f0818d8-597c-4800-a0d5-b552618f1c05; ptreps=AQAK6s_ypjiDjgI8SX0aAQEBAQEBAQCQRXpNeAEBAJBFek14; ptradtrt=cuid_cf0f3b30-584e-11ef-ba1d-12a907f1fdf9; ptrstk=gbrYYas2VgR7puA-lm_MBttNBiw; ptrrc=LZQCK32V-1C-FYEU; ptrmnt=3664296415815660000V10; ptrb=d7d849b2-85d9-4cfe-a3ab-9961de405de6; ptrbsw=7c2904c5-fea5-4dc0-925f-df5cbf41ddc6; ptraa=%7B%24PARTNER_UID%7D; ptradfm=618664373301387081; ptrbeeswax=AAfxnE7NctoAABVhmR5eZw; ptrloopme=9d860c5c-ecc3-4cdd-b63b-41cb7060c301; ptreq=1100060860225078433; yieldmo_id=VmzBFFFuBwFXA47MqS80%7C1723593600000%7C3605057276825920498; re_sync=pp%3D1197665%7Cbsw%3D1197667%7Cadfm%3D1197667%7Ciqzone%3D1197667%7Ctapad%3D1197794%7Cmf%3D1197794%7Cbeeswax%3D1197667%7Cneustar%3D1197668%7Caa%3D1197667%7Cb%3D1197667%7Cc%3D1197665%7Ccriteo%3D1197666%7Cloopme%3D1197667%7Ceps%3D1197666%7Cstk%3D1197666%7Cdv360%3D1197794%7Ceq%3D1197668%7Can%3D1197665%7Crc%3D1197665%7Cunl%3D1197665%7Cmnt%3D1197667%7Cliveramp%3D1197794%7Ct%3D1197665%7Cadtrt%3D1197666%7Cz%3D1197668%7Cpub%3D1197665%7Crhs%3D1197665%7Copenx%3D1197794',
}
base_url = "https://finance.yahoo.com/topic/latest-news/"
filename = "./news/data/yahoo/list_finance_us.json"
current_links = []

def get_detail(link):
    if link in current_links:
        return ""
    print("yahoo_finance_us link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, 'lxml')
        soup = body.select_one(".article .body")

        # 过滤 <div data-testid="view-comments"></div> 的 div
        ad_elements = soup.select('div[data-testid="inarticle-ad"]')
        view_comment = soup.select_one('div[data-testid="view-comments"]')
        if view_comment:
            view_comment.decompose()
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return [str(soup), body.select_one(".byline-attr-time-style > time")['datetime'].replace('Z', '+08:00')]
    else:
        print("yahoo_finance_us request: {} error: ".format(link), response)
        return ""
    
def run():
    data = history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        base_url, None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, 'lxml')
        items = soup.select(".js-stream-content")
        for index in range(len(items)):
            title = ""
            link = ""
            if index > 3:
                break
            a_tags = items[index].select("h3 > a")
            for a_tag in a_tags:
                if "https://finance.yahoo.com/news/" not in a_tag['href']:
                    continue
                else:
                    link = a_tag['href']
                    title = a_tag.text
                    break
            if link == "":
                continue
            if link in ",".join(_links):
                break
            detail = get_detail(link)
            description = detail[0]
            pub_date = parse_time(detail[1], '%Y-%m-%dT%H:%M:%S.%f%z')
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date,
                    },
                )
                    
        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("yahoo_finance_us request error: ", response)


try:
    run()
except Exception as e:
    print("yahoo_finance_us exec error: ", repr(e))
    logging.exception(e)
