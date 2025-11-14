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
  "cookie": "PHPSESSID=on8bg2tulnbo9qpcdgigv159uv; pv_r0_rand=18; pv_r0_date=2025-09-09; _lr_geo_location_state=SC; _lr_geo_location=CN; lc=en_HK; aTest_5_37=1545; aTest_5_38=1559; iStreamV3=on; aTest_tunnel-membre_social=social; _gid=GA1.2.1211343054.1757414856; _clck=158sx21%5E2%5Efz6%5E0%5E2078; zbconnect=zhanghong.yuan%40longbridge-inc.com; rappelcookie=1; aTest_1_16_20=1577; aTest_periode_essai=classique; aTest_page-services=deployed_top_detail; zb_auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlVWRjRaWE5FY1hSTVYzTjBXRmhzTkZock1UQm1kejA5IiwiaWF0IjoxNzU4MDE5Nzg0fQ.VWz8x_IBDznMpVxtPnn6w1vqM8sBeIdEk9ckCHYaxow; zb_membre=1; hmv=54c00abccdc7b3a958449b0863ec345fc5c30212; aTest_1_4=46; UTM_intern=%7B%22date%22%3A%222025-09-09%2018%3A51%3A19%22%2C%22id_utm_lien%22%3A%22108764863%22%7D; _ga=GA1.1.1913837678.1757413478; __gads=ID=49a507804a1b57d6:T=1757413486:RT=1757415107:S=ALNI_MYwHsyL4K3QBV-sU6yrN4MnomQnOg; __gpi=UID=00001193a1dfde8c:T=1757413486:RT=1757415107:S=ALNI_Mby3_9E0uRwnJ2llvd78H6OLZ8P-Q; __eoi=ID=9447793ba7d33bb3:T=1757413486:RT=1757415107:S=AA-AfjYgpu0iqdog4HsvSceRHcu4; pv_r0=18; _clsk=1pnogy0%5E1757415364524%5E15%5E1%5Ea.clarity.ms%2Fcollect; _ga_QWFHW0MRG9=GS2.1.s1757413477$o1$g1$t1757415364$j59$l0$h0"
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
            a = items[index].select_one("td.w-100 > div.grid > a.txt-overflow-2")
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
