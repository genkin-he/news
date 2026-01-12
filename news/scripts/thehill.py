# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 替换 urllib
import json
import re
import time
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    "cookie": '_pxhd=57fbb4fb344f1b67c07432a10499716db1c9cf7295d1f94414fe069ad20718bd:29628079-be16-11f0-b932-31bc81dec1b0; _pxvid=29628079-be16-11f0-b932-31bc81dec1b0; _cb=CGX4qB8To7iBTdSBE; usprivacy=1---; mm-user-id=pRNXA1U1AZOuqbNS; OTGPPConsent=DBABLA~BVQqAAAAAACA.QA; _lc2_fpi=aaf26d292db3--01k9pgxzmrqre3xwf27njb4412; _lc2_fpi_meta=%7B%22w%22%3A1762766290584%7D; _lr_env_src_ats=false; repeat_visitor=1762766290957-146891; _ga=GA1.2.2090524598.1762766291; _pubcid=597a4efd-36ac-4b09-8ea2-365f5b1e4ed7; _pubcid_cst=zix7LPQsHA%3D%3D; _cc_id=fa5c70c9325d0645349027e1fcf981b6; __qca=P1-ffc5acb7-4a7b-4c74-a167-490c7c528d3b; permutive-id=5d9287b7-0952-45f9-ab2b-f281f83c849d; brandcdn_uid=0b73ab24-5924-477c-a061-ac7d4fbb0545; pxcts=4b2a967e-ce8c-11f0-9e11-47a6e8304606; BCSessionID=0b9e7419-4d5d-4488-853e-7ddaf069f50b; panoramaId_expiry=1765181267498; panoramaId=6f567c02a1b2add20c71c9c9bdb716d539382cfb5f52072a297d0912055d3bc0; _lr_sampling_rate=100; _li_dcdm_c=.thehill.com; _gid=GA1.2.480847973.1764846386; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_identity=CiY4Mjk4NDU0NzMyODk5MzA0NTY4MTIxNzcxMDg3NzE2ODU0NTI4NlITCLj5u%2DimMxABGAEqBEpQTjMwAPABjtazyK4z; OneTrustWPCCPAGoogleOptOut=false; referralId=Direct; bob_session_id=1764903293133-317403; kndctr_19020C7354766EB60A4C98A4_AdobeOrg_cluster=sgp3; _lr_retry_request=true; AMP_TOKEN=%24NOT_FOUND; __gads=ID=0f587e0f872fe297:T=1762766291:RT=1764903296:S=ALNI_MZxfe_oUh_GgSnztrPvvjQ4fG3viA; __gpi=UID=000011b28a77e093:T=1762766292:RT=1764903296:S=ALNI_Maxg7I-HwfD54qtOfiQb8MTyNjVug; __eoi=ID=0ffbc1d1d8bb8f2c:T=1762766292:RT=1764903296:S=AA-AfjbAAz2CjcTFTiwE4Pvt19rJ; last_visit_bc=1764903338055; seg_sessionid=3f4f25dd-da81-4e47-8acf-a4293aa78431; sailthru_pageviews=2; _chartbeat2=.1762766287118.1764903338316.0000000000010011.CSGICSwEYJSD4fktDBBjBwa40PLN.1; _cb_svref=external; s_ips=357; s_tp=8949; s_ppv=thehill%253Ahome-page%2C4%2C4%2C4%2C357%2C25%2C1; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Dec+05+2025+10%3A55%3A38+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202510.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=4a494dd4-399b-4884-8c17-201573b098f6&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&gppSid=7&groups=SSPD_BG%3A1%2CC0002%3A1%2CC0004%3A1%2CC0007%3A1%2CC0003%3A1%2CC0001%3A1&AwaitingReconsent=false; sailthru_content=517bd98f83f5f5813508612a14a25d86a96f8a1c6e6bcca46de01b4a663aeaf73bd1cef926ded78f62a5120404a1b0a56c36f3a2ca26b05bc7a81661ac7f9f984d328e5001c111a5cc4572c41db500f22b5f7ff1d9ab1437be598f41ee2273963b0bda2a8f0b4361bc41444b6ecfe129; sailthru_visitor=a051b8fb-ad53-4c6f-91d2-e0aec42ad0f7; connectId=%7B%22vmuid%22%3A%229oczhuA7BZ_a3n2XfPcHhh0tIxsMtirz1qfMZ5RiKxORn6B668AVzuh0bIkFKSIKzSl_dN-T_CoXp15bT_hYSg%22%2C%22connectid%22%3A%229oczhuA7BZ_a3n2XfPcHhh0tIxsMtirz1qfMZ5RiKxORn6B668AVzuh0bIkFKSIKzSl_dN-T_CoXp15bT_hYSg%22%2C%22connectId%22%3A%229oczhuA7BZ_a3n2XfPcHhh0tIxsMtirz1qfMZ5RiKxORn6B668AVzuh0bIkFKSIKzSl_dN-T_CoXp15bT_hYSg%22%2C%22ttl%22%3A86400000%2C%22lastSynced%22%3A1764847166718%2C%22lastUsed%22%3A1764903339253%7D; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-10-10T09%3A18%3A11%22%7D; pbjs-unifiedid_cst=KixxLCos%2BQ%3D%3D; cto_bidid=yMBjrF9LNUlUa3Zrblc4NUpOVEhDQURzNlR0c1M4ZTc4OFB6ckhhemMxV2JzbDEwVktJSHUxQU8yNzdObUlxR1J2Y2tvcUZGY3NtOFJKOFRZc1I2cGtIcHEwRVc2cSUyRkxidXU5cXRhZURRUm5YbGdzJTNE; cto_bundle=K8j_0l9LVVo3WU9TUGVsbWRUbm41S3NxQ01GYlhYYjY5YUpBRE5vSUhQVGtjdHU1ekMlMkJrQ3NMaUNra2VKbTJRZG1uaGJJM0d3diUyRkViN2tMdzNvZ3VSTldJcEhjellIZm9KZ2RaSyUyRmo0JTJCeU43SXRjUXZhWHhIYVYxSzM5Z0U3c2xRWk5pMVJBMnpGdXVGaU1LaXVFZ2JZdzV5ZyUzRCUzRA',
}

base_url = "https://thehill.com"
api_url = "https://thehill.com/wp-json/lakana/v1/template-variables/"
filename = "./news/data/thehill/list.json"

# Create a session to maintain cookie state
session = requests.Session()
session.headers.update(headers)


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        detail_headers = headers.copy()
        detail_headers["sec-fetch-site"] = "same-origin"
        detail_headers["sec-fetch-dest"] = "document"
        detail_headers["sec-fetch-mode"] = "navigate"
        detail_headers["referer"] = base_url
        
        response = session.get(
            link, 
            headers=detail_headers, 
            proxies=util.get_random_proxy(),
            timeout=10,
            allow_redirects=True
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            article_text = body.select(".article__text")
            if not article_text:
                util.error("Article text not found for: {}".format(link))
                return ""
            
            soup = article_text[0]
            ad_elements = soup.select(".ad-unit,.hardwall, style, script, div, aside ")
            # 移除这些元素
            for element in ad_elements:
                element.decompose()
            return str(soup).strip()
        elif response.status_code == 403:
            util.error("403 Forbidden for: {}. Session may have expired.".format(link))
            return ""
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
        # First visit homepage to establish session and get cookies
        homepage_headers = headers.copy()
        homepage_headers["sec-fetch-site"] = "none"
        homepage_headers["referer"] = ""
        
        try:
            homepage_response = session.get(
                base_url, 
                headers=homepage_headers, 
                timeout=10,
                proxies=util.get_random_proxy(), 
                allow_redirects=True
            )
            if homepage_response.status_code in [200, 304]:
                util.info("Homepage visited successfully, session established")
                # Small delay to ensure cookies are set
                time.sleep(0.5)
            else:
                util.error("Homepage visit failed with status: {}".format(homepage_response.status_code))
        except Exception as e:
            util.error("Failed to visit homepage: {}".format(str(e)))

        # Now visit the API endpoint
        api_headers = headers.copy()
        api_headers["accept"] = "application/json, */*;q=0.1"
        api_headers["sec-fetch-dest"] = "empty"
        api_headers["sec-fetch-mode"] = "cors"
        api_headers["sec-fetch-site"] = "same-origin"
        api_headers["referer"] = base_url
        
        response = session.get(
            api_url,
            headers=api_headers,
            proxies=util.get_random_proxy(),
            timeout=10,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            try:
                data_json = response.json()
                if "sidebar" not in data_json or "just_in" not in data_json["sidebar"]:
                    util.error("Invalid API response structure")
                    return
                
                posts = data_json["sidebar"]["just_in"]
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
                            # Small delay between article fetches
                            time.sleep(0.3)
                
                if len(articles) > 0 and insert:
                    if len(articles) > 10:
                        articles = articles[:10]
                    util.write_json_to_file(articles, filename)
            except json.JSONDecodeError as e:
                util.log_action_error(f"JSON decode error: {str(e)}")
            except KeyError as e:
                util.log_action_error(f"Missing key in API response: {str(e)}")
        elif response.status_code == 403:
            util.log_action_error(f"403 Forbidden: Session expired or blocked. Cookies may need refresh.")
        else:
            util.log_action_error(f"request error: {response.status_code}")
    except Exception as e:
        util.log_action_error(f"request error: {str(e)}")

if __name__ == "__main__":
    if util.should_run_by_minute(divisor=10):
        util.execute_with_timeout(run)
