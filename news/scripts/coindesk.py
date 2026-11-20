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
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "__ld_anon=ld_anon_a36270a1-5ac6-4511-aa32-d1a905ed5811; _gcl_au=1.1.440652632.1752734521; _ga=GA1.1.265572468.1752734521; FPID=FPID2.2.CNRertFuxHdyLNDsh%2BjRNxAeFhIKgNDo1DsfBoLBl4g%3D.1752734521; FPLC=YXk445Kw2czANBzn5L%2FmWlk4tv9aHfUTaxKa0M2ScN67j815LWkHcoqWpXpLVbLBfqThl48KBPuopHUct61yTVd5%2BqgFlmRNUc3JT40heobOIWo3VIQSgyEpLovT%2FQ%3D%3D; FPAU=1.1.440652632.1752734521; _gtmeec=e30%3D; _fbp=fb.1.1752734520826.1251143480; sailthru_pageviews=3; sailthru_content=bb8d48decf0d39da6b163afe770ef328; sailthru_visitor=4dcd3e2c-3472-4e2a-bd67-11516945d069; ___adrsbl_nonce=ce00e3305bc43490ed89b86c2b068eb2; _uetsid=24a82cb062d911f08e69d1cb86a90fd5; _uetvid=24a8384062d911f088ed81a675c8ca10; COINDESK_PREFERENCES=eyJhbGciOiJIUzI1NiJ9.eyJ0aGVtZSI6ImxpZ2h0IiwiY3JlYXRlZEF0IjoxNzUyNzM0NTU4ODk3LCJsYXN0QWNjZXNzZWQiOjE3NTI3MzQ1NTg4OTksImlhdCI6MTc1MjczNDU1ODg5OSwiZXhwIjoxNzUyNzQyMzM0ODk5LCJpc3MiOiJjb29raWUtc2VydmljZSIsImF1ZCI6InVzZXIifQ.5Ny-LSiSlikpssNb4wQ49WjoJl-xMCwyC_TuNa_ABB0; COINDESK_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJwbGFuIjp7Im5hbWUiOiIzLXBsYW4iLCJsaW1pdCI6MywicGVyaW9kIjoibW9udGhzIiwiZHVyYXRpb24iOjEsInJvbGxpbmciOmZhbHNlfSwic3RhcnREYXRlIjoxNzUyNzM0NTEwODczLCJhcnRpY2xlc1JlYWQiOjMsImFsbG93ZWQiOlsiL21hcmtldHMvMjAyNS8wNy8xNy94cnAtYnJlYWtzLWFib3ZlLTMtd2l0aC12b2x1bWUtc3VyZ2UtYWhlYWQtb2YtZnV0dXJlcy1ldGYtbGF1bmNoLW5leHQtdGFyZ2V0LTM0MCIsIi9wb2xpY3kvMjAyNS8wNy8xNi9oYWNrLXZpY3RpbXMtc2F5LXRvcm5hZG8tY2FzaC1vZmZlcmVkLW5vLWhlbHAtaW4tdGhlLXdha2Utb2YtZXhwbG9pdHMtZGF5LTItb2Ytcm9tYW4tc3Rvcm0tdHJpYWwiLCIvdGVjaC8yMDI1LzA3LzE2L3RoZS1wcm90b2NvbC1sYXllci0yLWVjbGlwc2Utcy1haXJkcm9wLWdvZXMtbGl2ZSJdLCJjb252ZXJ0ZWQiOmZhbHNlLCJmYWxsYmFjayI6ZmFsc2UsImxhc3RQYWdlIjoiL3RlY2gvMjAyNS8wNy8xNi90aGUtcHJvdG9jb2wtbGF5ZXItMi1lY2xpcHNlLXMtYWlyZHJvcC1nb2VzLWxpdmUiLCJjcmVhdGVkQXQiOjE3NTI3MzQ1NTg4OTgsImxhc3RBY2Nlc3NlZCI6MTc1MjczNDU1ODg5OSwiaWF0IjoxNzUyNzM0NTU4ODk5LCJleHAiOjE3NTI3NDIzMzQ4OTksImlzcyI6ImNvb2tpZS1zZXJ2aWNlIiwiYXVkIjoidXNlciJ9.1SLJoOvVF2E0WFTTHUYu6oLLeFxqcNUSh5CJKoZDcNE; OptanonAlertBoxClosed=2025-07-17T06:42:43.503Z; eupubconsent-v2=CQUrf0AQUrf0AAcABBENBzFsAP_gAEPgABJ4LYNT_G__bWlr-b73aftkeYxP9_hr7sQxBgbJE24FzLvW_JwWx2E5NAzatqIKmRIAu3TBIQNlHJDURVCgKogVryDMaEyUoTNKJ6BkiFMRI2JYCFxvm4tjeQCY5vr991c1mB-t7dr83dzyy4hHn3a5_2S1WJCdIYetDfv8ZBKT-9IEd_x8v4v4_F7pE2-eS1n_pGvp6D9-Yns_dB299_bbffzPn__rl_e_X_vf_n37v943H77v____fBbAAEw0KiCMsiBEIlAwggQAKCsIAKBAEAACQNEBACYMCnIGAC6wmQAgBQADBACAAEGAAIAABIAEIgAoAIBAABAIFAAGABAEBAAwMAAYALAQCAAEB0DFMCCAQLABIzIoNMCUABIICWyoQSAIEFcIQizwCCBETBQAAAgAFAQAAPBYCEkgJWJBAFxBNAAAQAABRAgQIpGzAEFAZotBeDJ9GRpgGD5gmSUwDIAiCMjJNiE34TDxyFEKCHIAAAAA.f_wACHwAAAAA; _ga_VM3STRYVN8=GS2.1.s1752734519$o1$g1$t1752734563$j60$l0$h396934818; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jul+17+2025+14%3A42%3A43+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202504.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=02bb85be-a245-441f-bbef-5b77a4d1fac4&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0003%3A1%2CV2STACK42%3A1&intType=1; _clck=ycbch6%7C2%7Cfxo%7C0%7C2024; _dd_s=aid=455cdf4b-54ff-42e0-ae31-79a3b17374ec&rum=2&id=77cec484-656b-4190-b448-8eff2fb6085c&created=1752734513692&expire=1752735463496",
}

base_url = "https://www.coindesk.com"
filename = "./news/data/coindesk/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
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
        util.error("request: {} error: {}".format(link, response))
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
            link = base_url + str(node["href"].strip())
            if "markets" not in link and "business" not in link:
                continue
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
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
        util.log_action_error("request error: {}".format(response))


link1 = "https://www.coindesk.com/markets"
link2 = "https://www.coindesk.com/business"
if __name__ == "__main__":
    # util.execute_with_timeout(run, link1)
    # util.execute_with_timeout(run, link2)
    util.info("HTTPError 429: 'Too Many Requests'")
