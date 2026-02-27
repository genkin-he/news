# -*- coding: UTF-8 -*-
import traceback
import requests  # 替换 urllib.request
from util.spider_util import SpiderUtil
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"133.0.6943.142"',
    "sec-ch-ua-full-version-list": '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.142", "Chromium";v="133.0.6943.142"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.1.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_gid=GA1.2.1305156163.1741327806; __qca=P0-1643537626-1741327808150; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m7ydmaz36sojbdjj%22%7D; __pnahc=0; __pat=-18000000; cX_P=m7ydmaz36sojbdjj; cf_clearance=FiZzOWhhwsbQfWoeAsMyHKG3lSNqTnc2cossrynC2us-1741327821-1.2.1.1-Ei7ShWcU_Zc7xWPIOr.MDv2gwvu7gjNqoqi7fbFRvOqGx2NeBJJ7aAxWjhGWAONNG_e3iTFTHBbHvXdF.SfMczDvaRocSbkHZ3RmEPxlhShCpoTyVorZYzRiJm_Uo_.1YoJr2ZBBcBflJ2LpWYgbE_OFotzCHjNFCUbtZwcOkzto0zkJ0FXOeUrtGkLPOoNO7CgJAh0f._ovXWdYhL9iiZI0IWLUEh9vGmNG4c3RL5H0nYnSp4Jnlue7RgK06v59FBecncP21IdFwAe1XjgymMk_MGpIR.zRwvKQnfwBTgtgiLGeC5Pq_cn.N_6UdilKfPoPdL3_CYnn4SFgjZ6FB8jySgA_IX..F1ypJuONGMHD3LsdHzAfJu9NJO9KNnbq22qL.YRuz8HQNB8szc7ZBYWeFdQi.CXszpne2zWmwnw; __pvi=eyJpZCI6InYtbTd5ZG1hejh0MDdmNmRzcSIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTc0MTMyNzg0MTgwMn0%3D; __tbc=%7Bkpex%7DGXOcQIhMF3uMGcrVT5ugilQmE8JyNAiW61RkVDLls81TRRif_AqPojRPKKlo0Foa; xbc=%7Bkpex%7Dij4tc95XSDHTGbVkSJOOCtKDHNo6Gs1tuGi-IY5jMxAFrDbeRsuO9SvC_WlLSqVAQYS3EFJ4bwPP8Z3H1-zuJg_-iTexBy0K4O9DcGEtJb8; FCNEC=%5B%5B%22AKsRol-_fWIJnBKLpWTG-u0io4RF09_VDvtv8MR_GxcH-2MtKi8n9I9Sn-VGCKlHgtRnSQ3CcXLr5OGsvcAuz5xNbeKSjwnm1I5zbDHMxConU46DA3xZ8ZHNnjhpwk3LpnbkTrUG9wTuwpXxoV2eJ0pE5BcIOcCjSg%3D%3D%22%5D%5D; _gat_G-NFBGF6073J=1; _ga_NFBGF6073J=GS1.1.1741327805.1.1.1741328067.60.0.360822000; _ga=GA1.1.2092759476.1741327805; __adblocker=false",
}

base_url = "https://www.etf.com/news"
filename = "./news/data/etf/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)

    try:
        response = requests.get(
            link, headers=headers, timeout=10
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select(".etf_articles__body")[2]
            ad_elements = soup.select(".caas-da")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        else:
            util.error("request: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error(f"Error fetching detail for {link}: {str(e)}")
        return ""


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = requests.get(
            link, headers=headers, timeout=10
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.select(".image-card")
            for index in range(len(items)):
                if index > 0:
                    break
                link = items[index].select(".image-card__title > a")[0]["href"].strip()
                if link != "":
                    link = "https://www.etf.com{}".format(link)
                title = items[index].select(".image-card__title > a")[0].text.strip()
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
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
                            "source": "etf",
                            "kind": 1,
                            "language": "en",
                        },
                    )

            if len(_articles) > 0 and insert:
                if len(_articles) > 10:
                    _articles = _articles[:10]
                util.write_json_to_file(_articles, filename)
        else:
            util.error("request error: {}".format(response.status_code))
    except Exception as e:
        util.error(f"Error in run function: {str(e)}")


try:
    # run(base_url)
    print("etf 403 暂停")
except Exception as e:
    util.error("exec error: {}".format(repr(e)))
    traceback.print_exc()
