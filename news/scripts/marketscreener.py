# -*- coding: UTF-8 -*-
import requests  # 发送请求
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
  "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' ,
  "accept-language": "zh-CN,zh;q=0.9",
  "cache-control": "no-cache",
  "pragma": "no-cache",
  "priority": "u=0, i",
  "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"macOS"',
  "sec-fetch-dest": "document",
  "sec-fetch-mode": "navigate",
  "sec-fetch-site": "same-origin",
  "sec-fetch-user": "?1",
  "upgrade-insecure-requests": "1",
  "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
  "cookie": 'zbconnect=zhanghong.yuan%40longbridge-inc.com; rappelcookie=1; UTM_intern=%7B%22date%22%3A%222025-09-10%2011%3A36%3A13%22%2C%22id_utm_lien%22%3A%2286227424%22%7D; PHPSESSID=6h6d2gdufsgdsh5fv5bvnmg7cc; pv_r0_rand=12; pv_r0_date=2026-01-07; pv_r0=1; _ga=GA1.1.1076743318.1767784157; g_state={"i_l":0,"i_ll":1767784156586,"i_b":"vzlnjw7K2Zxybux8Nl/UGEeUAmQPqDf1PKSvpFU5wX4","i_e":{"enable_itp_optimization":0}}; x_login_id=42867a152ad662f2c838ffde39e971aa4b1b2d9c87a23dc81aba9f940612e70c; _ga_QWFHW0MRG9=GS2.1.s1767784156$o1$g0$t1767784156$j60$l0$h0; _lr_geo_location=JP; ic_tagmanager=AY; usprivacy=1---; IC_ViewCounter_hk.marketscreener.com=1; __gads=ID=49a507804a1b57d6:T=1757413486:RT=1767784158:S=ALNI_MYwHsyL4K3QBV-sU6yrN4MnomQnOg; __gpi=UID=00001193a1dfde8c:T=1757413486:RT=1767784158:S=ALNI_Mby3_9E0uRwnJ2llvd78H6OLZ8P-Q; __eoi=ID=9447793ba7d33bb3:T=1757413486:RT=1767784158:S=AA-AfjYgpu0iqdog4HsvSceRHcu4; lc=en_HK; cto_bundle=ytu_6l9mUDU5QUQxTzhXa1RzbWxmakdUem1CMlNxd2g5Rkd4QlE5TEVMSU1La3huWXAlMkIyZ0EwcEtsVkVHV3ElMkZJOXN6RVBtYnlUWW8lMkJ0N2JPbHVaMGFrd3lGQmY1cnk4ZWtRRXJndVY5dnJ0cDR0bTFQJTJCMGc4d212dmN6SzhNJTJGJTJCZEtJdHd5eDBBRFROOUdUSTZHamdEJTJGc0xha2w0cExsendSRFBTNndGYklJOTUlMkJnJTNE; _unifiedId=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-12-07T11%3A09%3A20%22%7D; _unifiedId_cst=VyxHLMwsHQ%3D%3D; lotame_domain_check=marketscreener.com; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId_expiry=1768388961956; panoramaId=12f5a1e99b9bac744734715359f0185ca02cdd9ed636364c786310a5bcff1f3d; panoramaIdType=panoDevice'
}

base_url = "https://hk.marketscreener.com"
filename = "./news/data/marketscreener/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            resp = response.text
            body = BeautifulSoup(resp, "lxml")
            soup = body.select_one("div.article-text")

            ad_elements = soup.select("style, script,.zppAds,.zppAdvertising")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()

            return str(soup).strip()
        else:
            util.error("detail: {} error: {}".format(link, response.status_code))
            return ""
    except Exception as e:
        util.error("detail: {} exception: {}".format(link, str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    response = requests.get(
        "https://hk.marketscreener.com/news/",
        headers=headers,
    )
    if response.status_code == 200:
        body = response.text
        soup = BeautifulSoup(body, "lxml")
        items = soup.select("#newsScreener > tbody > tr")
        for index in range(len(items)):
            if index > 10:
                break
            a = items[index].select_one("td.w-100  div.gnowrap a.txt-overflow-2")
            link = base_url + a["href"].strip()
            title = a.text.strip()
            if link in ",".join(_links):
                util.info("exists link: {}".format(link))
                continue
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
                        "source": "marketscreener",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(_articles) > 0 and insert:
            if len(_articles) > 40:
                _articles = _articles[:40]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("list error: {}".format(response.status_code))

if __name__ == "__main__":
    util.execute_with_timeout(run)
    # result = get_detail("https://hk.marketscreener.com/news/nebius-jumps-on-17-4-billion-ai-computing-deal-with-microsoft-ce7d59dfdf8ff722")
    # util.info(result)
