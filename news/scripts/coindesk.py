# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
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
    "cookie": "country=HK; region=hkg1; subregion=Eastern%20Asia; oficialCountryName=Hong%20Kong%20Special%20Administrative%20Region%20of%20the%20People's%20Republic%20of%20China; currencyCode=HKD; currencySymbol=%24; currencyName=Hong%20Kong%20dollar; city=San%20Francisco; CookieConsent={stamp:%27-1%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:9%2Cutc:1734925941545%2Ciab2:%27%27%2Cregion:%27HK%27}; _sp_ses.dcec=*; _pbjs_userid_consent_data=3524755945110770; _gcl_au=1.1.1134140743.1734925942; sailthru_pageviews=1; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.coindesk.com/%22%2C%22sref%22:%22%22%2C%22sts%22:1734925942611%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=2b06d1a8-6c2c-4f32-9df2-1106c81bace4%22%2C%22session_count%22:1%2C%22last_session_ts%22:1734925942611}; _rdt_uuid=1734925942736.638f100d-5e3e-4b96-970b-1d7b8d83aec5; _cc_id=cd3be24f714b9c8fee420c220e689dc7; panoramaId_expiry=1735012342869; _ga=GA1.1.288466544.1734925943; FPID=FPID2.2.aM6b3slcawxhacQjzYX8fqNHFdhTFiTkmnUN5%2B0e0p4%3D.1734925943; FPLC=v%2BFMa9x%2FRKhzrvc0Xm1b4YuQgO0W4RlHz9iY%2FVCAjtLyR2pLxdPsiHA2XGyr7GwmINF3ItAnxPhJbA4gi11Vve8gBBc0vScwJUGpyBmjzvrzGxYFIGPUDFqmy%2BjH%2Bw%3D%3D; FPAU=1.1.1134140743.1734925942; _gtmeec=e30%3D; _fbp=fb.1.1734925943212.1394991833; _hjSessionUser_1065293=eyJpZCI6ImVjN2I5ZjVkLWY3NWItNWM2NC04Y2U4LWEyZmFiNGE4MTI5OSIsImNyZWF0ZWQiOjE3MzQ5MjU5NDM1MjgsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_1065293=eyJpZCI6ImJhY2M2YjlmLWU1N2MtNGZiNi04ZDE0LTBhYTVkODNjMmM4NiIsImMiOjE3MzQ5MjU5NDM1MjksInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; _sharedid=e0df22df-46ac-4900-8f24-a7f942efc6c0; _sharedid_cst=VyxHLMwsHQ%3D%3D; _lr_retry_request=true; _lr_env_src_ats=false; hb_insticator_uid=6073ef4a-4d8f-4e0c-b14a-3b5bc20126b4; sailthru_content=f4618b8837368562f9d01fbc250e974b; sailthru_visitor=a394afba-a4bc-492f-8398-600ef6d80295; __qca=P0-2077519512-1734925943540; _lr_sampling_rate=100; _parsely_slot_click={%22url%22:%22https://www.coindesk.com/markets%22%2C%22x%22:24%2C%22y%22:203%2C%22xpath%22:%22//*[@id=%5C%22modal%5C%22]/ul[1]/li[3]/div[1]/a[1]%22%2C%22href%22:%22https://www.coindesk.com/%22}; _ga_VM3STRYVN8=GS1.1.1734925942.1.1.1734925992.0.0.1008416436; cto_bidid=rNJrv184YkVHbXF4MjRNamIwUnpwQjBXMEhlNzBDQmVtSjRDZGk0UU9jMyUyRkV5aGdKNzdyN1M0TWxydHVIOVVWcTJVWHNobDIxSXhZWHdadDBEOWFoT3Rma3dMZ0VHQjA2cGtoQ0w3dHpqQUFNZ0pjJTNE; _pn_Zepx0dJv=eyJzdWIiOnsidWRyIjowLCJpZCI6Ik1Hb1RFMG1tTzNQUmQwRU9DejdoSjRGbE1TVWJxakZ3Iiwic3MiOi0xfSwibHVhIjoxNzM0OTI1OTYyMTg0fQ; cto_bundle=1OgHYl84WGd0MUxidEolMkJSeks2cVA1Z3A4alJZWGxVN0Mwbmh6bkM2ZlA4eEVWMGNQRWdDRElheWROVXhPckx0cjFyWjZTTXV2UUJaWVpjWW40UjA3bk4lMkZCVlVuZHN2SHFwTDV3SjNsZk50U2NUOU55ZmFLTFElMkJISGJGN0w1NkQ3JTJGaXpyR3E4YkJZTHM2UnE1WCUyQkZ0S2FHNFR3JTNEJTNE; _sp_id.dcec=0dacab9fa472b24e.1734925942.1.1734926053.1734925942; _dd_s=rum=2&id=fb841954-96b9-4a48-950f-4c89d9ba7fd7&created=1734925961962&expire=1734926972947",
}

base_url = "https://www.coindesk.com"
filename = "./news/data/coindesk/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(link):
    print("coindesk link: ", link)
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select(".document-body")[0]

        ad_elements = soup.select(".article-ad,.h-56,.gap-2")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        print("coindesk request: {} error: ".format(link), response)
        return ""


def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(url, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select(".grid .flex > a")
        for node in nodes:
            if post_count >= 2:
                break
            link = base_url +str(node["href"].strip())
            if "markets" not in link and "business" not in link:
                continue
            if link in ",".join(links):
                print("coindesk exists link: ", link)
                break
            title = str(node.text.strip())
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
                        "source": "coindesk",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("coindesk request error: {}".format(response))


link1 = "https://www.coindesk.com/markets"
link2 = "https://www.coindesk.com/business"
util.execute_with_timeout(run, link1)
util.execute_with_timeout(run, link2)
