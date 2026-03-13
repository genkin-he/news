# -*- coding: UTF-8 -*-
import requests  # 发送请求
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "suid=1bfff62fe08049e6a547d3f2d8eb1b86; _vwo_uuid_v2=DCBC58E4108A58DAA100ADC1A556CB279|4682cf241609af444a150357709e3683; _vwo_uuid=DCBC58E4108A58DAA100ADC1A556CB279; _vwo_ds=3%241742183207%3A24.74134743%3A%3A; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _vis_opt_exp_9_combi=1; topoverlayDisplayed=yes; neuronId=0f78c652-bb11-4acf-817c-0c61b752900c; mySPHUserType=y-anoy; visitorcat=1; _gcl_au=1.1.1968945660.1742183212; permutive-id=c7a9fb53-1532-48bb-aeb6-cda35c88354e; _gid=GA1.3.1178590177.1742183213; sui_1pc=1742183212789206D2E9468E4D2FD17007EA48ABE6E3E47C5D0F736F; _cb=3pzwPCcBiUFBsdH0f; BTPulseTooltip=shown; my-account-anon-tooltip=shown; FPID=FPID2.3.1oqW3S9V4CU9t91oGw1Qi8xBVx4mPH5KD8vTJ%2BM1OFo%3D.1742183213; FPLC=B4DZQqKzKn8PsPqqHOB%2BQDfreqgloEU%2BsJ9Wr2isNDzfy2%2F1pcjEyr7bPPdhPuIXyNfiwg5ZZMnt9MA0cgkJMguOzD4Rl0QhGyOQ8KgR0x4miBDApw%2F4f9aJ2ujhtw%3D%3D; exit_intervention=true; spgwAMCookie=qq3bto844ntm67neifopnhtt4k; _ga_SM7K1EMZHH=GS1.1.1742190625.2.0.1742190625.60.0.0; topOverlayImpressionsServed=3; _vwo_sn=7382%3A2%3A%3A%3A1; _chartbeat2=.1742183213534.1742190673412.1.D6OQZITG96JCWhhnSD7e5bwCkxho5.1; sph_user_country=HK; AWSALB=yo6ADjT5FiVGt6s28MCD6CbgF17d/SkaKW3PbToIqoohPdYjbv2FvrYXi1h/9q/gUk06CdIZtfbSAbnR81gSnnWeOcdkBTLgIGqPoyY8NKGA6ZClpuXYMpQ9rzOU; AWSALBCORS=yo6ADjT5FiVGt6s28MCD6CbgF17d/SkaKW3PbToIqoohPdYjbv2FvrYXi1h/9q/gUk06CdIZtfbSAbnR81gSnnWeOcdkBTLgIGqPoyY8NKGA6ZClpuXYMpQ9rzOU; _ga=GA1.1.574282003.1742183213; _ga_BDB8DV371E=GS1.1.1742190724.2.0.1742190677.0.0.1701093259; panoramaId_expiry=1742277135750; ph_phc_yQ78F4A3sjKgkDMBvEsc1dNOEbSJfiHomZduQs1YL7z_posthog=%7B%22distinct_id%22%3A%220195a236-21ea-7ec0-a420-ce991c857213%22%2C%22%24sesid%22%3A%5Bnull%2Cnull%2Cnull%5D%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https%3A%2F%2Fwww.businesstimes.com.sg%2Fbreaking-news%22%7D%7D",
}

base_url = "https://www.businesstimes.com.sg"
filename = "./news/data/businesstimes-news/list.json"
util = SpiderUtil()

# 采集的页面列表
page_urls = [
    "https://www.businesstimes.com.sg/opinion-features?ref=listing-menubar",
    "https://www.businesstimes.com.sg/breaking-news?filter=companies-markets&ref=listing-menubar",
]


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            resp = response.text
            body = BeautifulSoup(resp, "lxml")
            soup = body.select_one("div.mx-auto.my-4.font-lucida.text-xl")
            if not soup:
                return ""

            ad_elements = soup.select("style, script, div")
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

    for page_url in page_urls:
        util.info("fetching page: {}".format(page_url))
        try:
            response = requests.get(page_url, headers=headers)
            if response.status_code != 200:
                util.log_action_error("page {} error: {}".format(page_url, response.status_code))
                continue

            body = response.text
            soup = BeautifulSoup(body, "lxml")
            items = soup.select("h3 a")
            for index in range(len(items)):
                if index >= 2:
                    break
                href = items[index].get("href", "")
                if not href:
                    continue
                link = href if href.startswith("http") else base_url + href.strip()
                title = items[index].text.strip()
                if not title:
                    continue
                if link in ",".join(_links):
                    util.info("exists link: {}".format(link))
                    continue
                description = get_detail(link)
                if description != "":
                    insert = True
                    _articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "businesstimes-news",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        except Exception as e:
            util.error("page {} exception: {}".format(page_url, str(e)))
            continue

    if len(_articles) > 0 and insert:
        if len(_articles) > 10:
            _articles = _articles[:10]
        util.write_json_to_file(_articles, filename)

if __name__ == "__main__":
    util.execute_with_timeout(run)
    # detail = get_detail("https://www.businesstimes.com.sg/international/hong-kong-q3-gdp-expands-3-8-yy-faster-forecast")
    # util.info(detail)
