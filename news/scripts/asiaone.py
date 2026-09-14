# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "c1630a48-8fcf-4a15-81dc-f933c6f74165permutive-id=544b527c-b126-4f71-9808-612da5cb3caa; _ga=GA1.1.356214791.1742985989; uid_dm=38d9cf93-6f43-1684-6b6e-6e98c7fa9091; __browsiUID=dab939a3-e9da-42a7-b3be-12386d8d0aed; _pubcid=d841a5f7-da60-4650-8e09-eb39e55c0084; pbjs-unifiedid=%7B%22TDID%22%3A%222cbb91e3-5bb8-4dba-aec9-831e7755fd98%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-02-26T11%3A07%3A13%22%7D; pbjs-unifiedid_cst=zix7LPQsHA%3D%3D; cto_bidid=OMTUIV9zTjRIblEwQkNTbHk2Z2NCZEpLZHA2WWRrRmtDSzh2YTR0NzJlNkc4ejFVa29ybGtxOVJHNjZ3blQ3a2NuUFR2S2d3MTY1MXR2ZXR2cm1WNmJHSlU1SWJwc0NxUUEweDB0Skt3TUh5RGNKdyUzRA; _pubcid_cst=kSylLAssaw%3D%3D; articleCounter=4; _clck=moln49%7C2%7Cfuk%7C0%7C1911; __browsiSessionID=407a3051-059a-4098-8022-65ce95f423ae&true&DEFAULT&hk&desktop-4.39.843&false; _sharedID=44106d68-92bf-4256-92e5-26873e59fd1a; _sharedID_cst=zix7LPQsHA%3D%3D; ucf_uid=e4361384-3408-4ecc-84bf-a4d0de492e19; __gads=ID=2570ce2393cabc3d:T=1742987230:RT=1743040782:S=ALNI_MYGNjic4lXtkUygvwrMNcwRw-UxFQ; __gpi=UID=000010017bc23999:T=1742987230:RT=1743040782:S=ALNI_MbCIoAXBRqv93Hud6pkjnMynm-vgA; __eoi=ID=6eaca6873db0d4c2:T=1742987230:RT=1743040782:S=AA-AfjY0QNjotGLaS054uWYMPA2b; AWSALBTG=4aBxjYQxnDXYJBpCvMu8ZKedPfYx1a0ciYqhboIIq9oiqjwBYC876xsKGvLSZZFJRFLjRb8SlAGi3OO8CLe35F4qVOdCCgN7VGpqLbVW1rhV5/o7AuvIgm+XcMeWqWW+5HqIiwf0OdM86HhheKnzF3jUOPpp/lbGKS/jHjVmmm/Aol8R2Vk=; AWSALB=F3vrx8fDE6sYoZ7x+QDYltyheSgx8g+UVDa1Z19GwhL8SFtuaNGd4synYccbK0ms6H89t5botFpHL7jgJcUxUyA2hOS9ElolIRLSKmcxzvlqeuxXLL8ECp/35Lhy; cto_bundle=rNfQFl9BMWlrRk02a0txYlBiJTJCb0UwSEFmTnJqT2llMHZ0dkVXYldhbzJsUVJ1U282d0RRc1RNM1ZaJTJCYWMlMkZlREZRZHBHd1VPdUsyY3B3MnQya3RVcHRpc2NWWUIwdEpMT3VoejNYT0hFTWI3N0I3aVhaJTJGdGFwQXZKTmNmZWM1Y2w5cSUyQkdKYiUyRkRBTVNDS2tHVlB6QkdvbmxMOFElM0QlM0Q; _ga_M7E3P87KRC=GS1.1.1743040023.2.1.1743040863.60.0.307705496; panoramaId_expiry=1743127264067; _clsk=t1z68o%7C1743040864605%7C4%7C1%7Cn.clarity.ms%2Fcollect; FCNEC=%5B%5B%22AKsRol_ZnFICS1hCzdNC7ie5kKc-Tvz-VHHCBtdXdpWqdn0rfS93UnKGs7SKliYZh0LMzJ63CfBFVAjJ-oxQBrMtLt7WcChis6BSM5ocn1PIfF31FKF46WOyy5lve9EPw6ml3l0m4GAqXsiqTQy8eIpCkMBqKFg2Ew%3D%3D%22%5D%5D; v1st_dm=eb0a29df-4eab-61ed-30e6-4777614b619e; _ga_BCTQVFRTEJ=GS1.1.1743040010.2.1.1743040882.41.0.0",
    "Referer": "https://www.asiaone.com/lite",
    "Referrer-Policy": "no-referrer-when-downgrade",
}

base_url = "https://www.asiaone.com"
filename = "./news/data/asiaone/list.json"
current_links = []
post_count = 0
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        resp = response.text
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one(".body")

        ad_elements = soup.select("script,style,[class*=-ads],#aniBox")
        for element in ad_elements:
            element.decompose()

        # 移除特定格式的内容，例如 [[nid:713343]]
        # 使用正则表达式匹配 [[nid:数字]] 格式并移除
        pattern = r'\[\[nid:\d+\]\]'
        for tag in soup.find_all(string=re.compile(pattern)):
            new_text = re.sub(pattern, '', tag.string)
            tag.replace_with(new_text)

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 发送请求获取响应
    response = requests.post(
        "https://www.asiaone.com/_api/datacenter/summaries/search",
        headers=headers,
        data=bytes(
            json.dumps({"start": 0, "size": 10, "condition": {"category": ["money"]}}),
            encoding="utf8",
        ),
    )
    if response.status_code == 200:
        resp = response.json()

        if "data" not in resp:
            util.error("resp 不存在")

        items = resp["data"]
        util.info("nodes size: {}".format(len(items)))

        for index, item in enumerate(items):
            if index >= 3:
                break
            link = item["url"]
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            if "data" not in item:
                break
            title = item["data"]["title"]
            image = item["data"]["image"]
            description = get_detail(link)
            if description != "":
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "image": image,
                        "pub_date": util.current_time_string(),
                        "link": link,
                        "source": "asiaone",
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


if __name__ == "__main__":
    # 只有台湾的 IP 才能访问
    # 403 Forbidden
    util.info("403 Forbidden")
    # util.execute_with_timeout(run)
