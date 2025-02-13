# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
from datetime import datetime, timezone, timedelta
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_vwo_uuid_v2=D239F69B14EA3F01E5CC8E04F2CDC0EED|c549ef9b993f5ac3f177ab04fae8211c; _vwo_uuid=D239F69B14EA3F01E5CC8E04F2CDC0EED; _vwo_ds=3%241724900710%3A88.385081%3A%3A; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _referrer=https://www.biopharmadive.com/; seerid=5e2ed602-577a-4450-bfc4-fc30d3e3fa08; _gcl_au=1.1.1587175011.1724900735; FPID=FPID2.2.Q3Quhd1ND2o%2FsX2yS067To8tYDG46PKovli1GMXKFmY%3D.1724900732; __td_signed=true; sp=ec5cdde0-1deb-4ae5-b85f-6d2ed83460df; __cf_bm=FhLKvHK.LUqX.XNjlVHp5oq.Q8OYxa0nBi4z8ix2x_Y-1725345151-1.0.1.1-Y3P2JGv0UVl2KhfwkKVaTERwnzDz9wixEHpeX0acj6wbTZd8EdfUO5HTUVuUsUZLyprAdOGqsQIMbk7ipGBkoQ; _prestitialPossible=1725345160766; _gid=GA1.2.1454121483.1725345162; seerses=e; _iris_duid=407c20a9-7b26-425c-9f2d-cea380b7d0bd; FPLC=GWAlLCIn8ALCngxKbQkS%2FjBn2LfXA9vEl44eWQmYhPdT2%2BZDmIJ%2Fh52%2FRjLU15Hn%2FSX%2BZ4Gw5Wd6wyH4ojgE%2Fj4SNiJabTrqqSeQeEu6DR0i8MR8zR0v%2Fh5jdkJ4zg%3D%3D; _clck=1iti3wi%7C2%7Cfov%7C0%7C1707; _sp_ses.f999=*; csrftoken=oioPHhm5WqsUJyM690YuvSMgmk7kTFy1oGmqeMI1LFGpUNIjrHHGdKHk5g0UfhOJ; sailthru_pageviews=13; _uetsid=5469274069be11ef8486ddf408d39314; _uetvid=91b4ed8065b311ef8735f308689f5d91; sailthru_content=14d9d0a9db229d0eee3234dd49a6f116e52bae5fc606613f893903d9ed9c8a85f35882b4c07ab7b6203030c3778e2784facf30a81c392fe22e1f4c310632bcf5e99fab9f34b9a0d91b4d92d31af4d2eb; sailthru_visitor=927a2b70-c252-4418-93ab-35f9745e729e; _td=7496650e-1316-46ee-9056-d6be2fdb2e61; _clsk=1km9z8y%7C1725345758300%7C7%7C1%7Cs.clarity.ms%2Fcollect; _vwo_sn=444443%3A15%3A%3A%3A1; FCNEC=%5B%5B%22AKsRol-swNI2faPYjBc5DgmR_tzxreEY07vhkDRW1To5FEOSTHAQ0b_R0UnNLRwZpYdEgV7pjvF8yra_4nPq5J_Di0sE-ZEK1R-drL1uYsKLsouREOZfvhz0hX2v899DNYbh83GvO7lk3kG6nbsun3hbmqod8Hh3Jw%3D%3D%22%5D%5D; _divecounter=15%090%090%091725345178546%091724900723713%090; _ga=GA1.2.1470260976.1724900732; _ga_CJ2H76VF2G=GS1.1.1725345162.3.1.1725345859.0.0.415736491; _sp_id.f999=407c20a9-7b26-425c-9f2d-cea380b7d0bd.1724900738.2.1725345954.1724902737.551540f9-2a1e-4c59-a648-2009978aaf32.1b8ef3e4-1016-4f68-887e-5bd43483ce46.1e70f65f-f114-4fa3-9e72-c6e463aaa0b6.1725345168221.76",
}

base_url = "https://www.biopharmadive.com/"
filename = "./news/data/biopharmadive/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    if link in current_links:
        return ""
    print("biopharmadive link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".article-body")
        if not soup:
            soup = body.select(".body")
            if not soup:
                soup = body.select(".content__text")[0]
            else:
                soup = soup[0]
        else:
            soup = soup[0]
            
        ad_elements = soup.select(".hybrid-ad-wrapper")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("biopharmadive request: {} error: ".format(link), response)
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".feed__item")
        for index in range(len(items)):
            if index > 2:
                break
            if not items[index].select(".feed__title > a"):
                continue
            link = "https://www.biopharmadive.com{}".format(items[index].select(".feed__title > a")[0]["href"].strip())
            title = items[index].select(".feed__title > a")[0].text.strip()
            if link in ",".join(_links):
                print("biopharmadive exists link: ", link)
                break
            description = get_detail(link)
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": util.current_time_string(),
                        "source": "biopharmadive",
                        "kind": 1,
                        "language": "en"
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("biopharmadive request error: {}".format(response))


link1 = "https://www.biopharmadive.com/"
link2 = "https://www.biopharmadive.com/press-release/"
util.execute_with_timeout(run, link1)
util.execute_with_timeout(run, link2)
