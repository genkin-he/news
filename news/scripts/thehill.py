# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": '_pxhd=57fbb4fb344f1b67c07432a10499716db1c9cf7295d1f94414fe069ad20718bd:29628079-be16-11f0-b932-31bc81dec1b0; _pxvid=29628079-be16-11f0-b932-31bc81dec1b0; _cb=CGX4qB8To7iBTdSBE; usprivacy=1---; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_identity=CiY4Mjk4NDU0NzMyODk5MzA0NTY4MTIxNzcxMDg3NzE2ODU0NTI4NlITCLj5u%2DimMxABGAEqBEpQTjMwAPABuPm76KYz; mm-user-id=pRNXA1U1AZOuqbNS; OTGPPConsent=DBABLA~BVQqAAAAAACA.QA; _lc2_fpi=aaf26d292db3--01k9pgxzmrqre3xwf27njb4412; _lc2_fpi_meta=%7B%22w%22%3A1762766290584%7D; _lr_env_src_ats=false; repeat_visitor=1762766290957-146891; _ga=GA1.2.2090524598.1762766291; _pubcid=597a4efd-36ac-4b09-8ea2-365f5b1e4ed7; _pubcid_cst=zix7LPQsHA%3D%3D; _cc_id=fa5c70c9325d0645349027e1fcf981b6; __qca=P1-ffc5acb7-4a7b-4c74-a167-490c7c528d3b; permutive-id=5d9287b7-0952-45f9-ab2b-f281f83c849d; brandcdn_uid=0b73ab24-5924-477c-a061-ac7d4fbb0545; last_visit_bc=1762766777613; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Nov+10+2025+17%3A26%3A18+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202510.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=4a494dd4-399b-4884-8c17-201573b098f6&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&gppSid=7&groups=SSPD_BG%3A1%2CC0002%3A1%2CC0004%3A1%2CC0007%3A1%2CC0003%3A1%2CC0001%3A1&AwaitingReconsent=false; _chartbeat2=.1762766287118.1762766778080.1.D76Qd3CMfHktC3VzhJBV9n9YChSIqU.1; connectId=%7B%22puid%22%3A%225e5472aac294f1dd61c96bbf4003be7132e81978d445d0bef283610ac55829e4%22%2C%22vmuid%22%3A%22GwbiMUQdoC1Jmuktc2tLvni6C3x5oOEEwqRVG3xRoqJRzYu7O9Gz-P0L2HJhanfmZwE4YhGXCBvKT7oU3tQtUQ%22%2C%22connectid%22%3A%22GwbiMUQdoC1Jmuktc2tLvni6C3x5oOEEwqRVG3xRoqJRzYu7O9Gz-P0L2HJhanfmZwE4YhGXCBvKT7oU3tQtUQ%22%2C%22connectId%22%3A%22GwbiMUQdoC1Jmuktc2tLvni6C3x5oOEEwqRVG3xRoqJRzYu7O9Gz-P0L2HJhanfmZwE4YhGXCBvKT7oU3tQtUQ%22%2C%22ttl%22%3A86400000%2C%22lastSynced%22%3A1762766291409%2C%22lastUsed%22%3A1762766778106%7D; sailthru_content=517bd98f83f5f5813508612a14a25d86a96f8a1c6e6bcca46de01b4a663aeaf73bd1cef926ded78f62a5120404a1b0a5; sailthru_visitor=a051b8fb-ad53-4c6f-91d2-e0aec42ad0f7; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-10-10T09%3A18%3A12%22%7D; pbjs-unifiedid_cst=VyxHLMwsHQ%3D%3D; cto_bundle=kbZ3iV9EUW1DeiUyQm5VN3AyeWlBMEpscFVKRWZ1bWxZWHV4a2JnVzJUak8lMkJOMVk2UUxKJTJGUExINWZFQ0ZCcjh4eEYlMkZkYlI0JTJGTFRFaHpXM3JaJTJCUDBmYTBjdkw2Uk45RDRpODhFRlo2SXpkWVNnQng0MGdXM2h0VWdQU0V4MTRxY29BUWxjeW8xWTBJaDk5cVRlTDYlMkJOemJTRDVmekg4U2U3S2cyMnZ3UkJzR1psQjRXMHBxZ0lRYUMxcGNLa3ZaYnF1eEpRQw; cto_bidid=6eCaO19LNUlUa3Zrblc4NUpOVEhDQURzNlR0c1M4ZTc4OFB6ckhhemMxV2JzbDEwVktJSHUxQU8yNzdObUlxR1J2Y2tvNUpBQkIlMkI1eHprNXZmNUthTHN4WDAzSjI4NVk1dlAxQ1RmSSUyQlN4QnAyQmhtYkIlMkJZWVl0VHJJMXcwMUkyTmcxTGZHS3V0VEE2VGpXMEJlWUVHNFkxY3clM0QlM0Q; __gads=ID=0f587e0f872fe297:T=1762766291:RT=1762767221:S=ALNI_MZxfe_oUh_GgSnztrPvvjQ4fG3viA; __gpi=UID=000011b28a77e093:T=1762766292:RT=1762767221:S=ALNI_Maxg7I-HwfD54qtOfiQb8MTyNjVug; __eoi=ID=0ffbc1d1d8bb8f2c:T=1762766292:RT=1762767221:S=AA-AfjbAAz2CjcTFTiwE4Pvt19rJ; pxcts=4b2a967e-ce8c-11f0-9e11-47a6e8304606; _px2=eyJ1IjoiMzBiODAxNTItY2U4Yy0xMWYwLTkwMmUtMjBkZTk3MWUxNmFhIiwidiI6IjI5NjI4MDc5LWJlMTYtMTFmMC1iOTMyLTMxYmM4MWRlYzFiMCIsInQiOjE3NjQ1NzY3MTkxNDgsImgiOiIxYmRjOTRjYTQ0OTUzNzNjMmY2NDdmY2E1Zjk4YWU0Yzk2ZmMyOWI4YTJkYTkyMDMxZTA0NTY3OGI5MmZjNmY0In0=',
}
base_url = "https://thehill.com/news/"
filename = "./news/data/thehill/list.json"


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = requests.get(link, headers=headers, proxies=util.get_random_proxy())
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.select(".article__text")[0]

            ad_elements = soup.select(".ad-unit,.hardwall, style, script, div, aside ")
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

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    try:
        response = requests.get(
            "https://thehill.com/wp-json/lakana/v1/template-variables/",
            headers=headers,
            proxies=util.get_random_proxy()
        )
        if response.status_code == 200:
            posts = response.json()["sidebar"]["just_in"]
            for index in range(len(posts)):
                if index < 2:
                    post = posts[index]
                    kind = post["post_type"]
                    id = post["id"]
                    title = post["title"]
                    link = post["link"]
                    if link in ",".join(links):
                        util.info("exists link: {}".format(link))
                        break

                    description = get_detail(link)
                    if description != "":
                        insert = True
                        articles.insert(
                            0,
                            {
                                "id": id,
                                "title": title,
                                "description": description,
                                "kind": kind,
                                "link": link,
                                "pub_date": util.current_time_string(),
                                "source": "thehill",
                                "language": "en",
                            },
                        )
            if len(articles) > 0 and insert:
                if len(articles) > 10:
                    articles = articles[:10]
                util.write_json_to_file(articles, filename)
        else:
            util.log_action_error(f"request error: {response.status_code}")
    except Exception as e:
        util.log_action_error(f"request error: {str(e)}")

if __name__ == "__main__":
    util.execute_with_timeout(run)
