# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re

from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "application/json",
    "accept-language": "en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-origin",
    "cookie": "_cb=DVDXuHB676okBc4WHm; bz_access_type=anonymous; benzinga_token=97vau8evlh8ua56nrbt22sp15o3vgkje; bz_access=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2NzAwNzEzLCJpYXQiOjE3NDY2OTk4MTMsImp0aSI6ImJmOTAxNWQzOTkzNjQ2NzU4YjEyNWZjNjBkNjQ2ZDQ5IiwidXNlcl9pZCI6Ik5vbmUiLCJpc3MiOiJodHRwczovL3d3dy5iZW56aW5nYS5jb20ifQ.YpyTZ10jp38B1MFkHb9X87Z9Upcf0ERjCUu1EH9ZQdR6-IHHuzsCIlVxuSfT1deuJvtATRTDq72NxkQR8-Q6nwSeDyf1jc5PgSQKlGDIFAQr03X7iaGWVpz1_OzVG_JV4y-mw8jg4bbG7vO_F4Bw-QOL19YU8o1bBi8K9F9g6ev0-UgWyBTnGJ8m_zY4aQH4gkIyFFdqEK0_M7FmW4mWjJvxAX2Nkg58vV-rN9j2bfO0ljWnb5lmsjSm52OqKHVeNXpDIHzGFm9kTIuMbv2GC65DCFif1uDPWtM5MKi9LE010s_KGNfuq4nrp27AHN8RiDo6k6e_XyCdJ7RTDijqPg; csrftoken=MShCVB0f2I6uLyLxqYKJQlYh3gZyNoc9; _gcl_au=1.1.1069732821.1746699814; bz_landing_url=https://www.benzinga.com/; _clck=14959ip%7C2%7Cfvq%7C0%7C1954; ajs_anonymous_id=f11e9639-0a27-45aa-afa7-7b0676c8a429; _hjSession_15446=eyJpZCI6ImJlZDI0NmNjLTgzNGYtNDY5YS05YjdiLTM3ZjJmYjE2NGU2ZCIsImMiOjE3NDY2OTk4MTY1MzQsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; usprivacy=1YNY; _li_dcdm_c=.benzinga.com; _lc2_fpi=f4f35c7bd450--01jtqpr4g5cnz1fh1xr6nfdmbh; _lc2_fpi_meta=%7B%22w%22%3A1746699817477%7D; _lr_retry_request=true; _lr_env_src_ats=false; _hjDonePolls=1617152; panoramaId_expiry=1746786218193; _cc_id=9204d48c0e4de0714abb2448b7efe0c; panoramaId=eeff86e280abaf8c24c7fc67e576a9fb927a0b90650ecb308b3bb1ec4e2512f5; _scor_uid=3e155569b7a043e39776b5f5a107f44c; _cb_svref=external; __cf_bm=18Uu_aEXdhxSg8ZtnAXzBgQ37_7vSund3_YkwlhcKv0-1746699877-1.0.1.1-3ZyMTnuVV5UmVLd3pP7E7pRI2I4pS55TNg_2dLNyG2UqlUwe5Dqvgf1r_fCZ_a8q1n.9XCzOhCjVcR63qb4nrqOVbvhsG0gdUTwohAA4opI; _hjSessionUser_15446=eyJpZCI6IjIyNDY2NDQ2LTRjOWMtNTEzZC1iZGY3LTg2YzMyNDBkYzQ0MiIsImNyZWF0ZWQiOjE3NDY2OTk4MTY1MzQsImV4aXN0aW5nIjp0cnVlfQ==; _sharedid=e5fb465d-0bcc-4fa8-aec9-a9e53f77fe69; _sharedid_cst=zix7LPQsHA%3D%3D; _clsk=11a1qxq%7C1746699879707%7C2%7C1%7Ci.clarity.ms%2Fcollect; ccuid=0ffd54be-05e1-4a35-84c1-6ef9b4e8f798; cto_bidid=SeujFl85RmhVYW93OXB1Y2VFaU5GN1ZXZWFCdzVCMGx0b0ZFS1ZIdXp2UmhsZVJzbXVkNnUlMkI0SEJ5UDdNOGglMkYlMkZnOHRXTnRhbyUyRk9FS0tmN3duc2pucWxSaTZvNE9XcWVzWldVS1NlJTJCTzFWNVVsVk0lM0Q; _ga=GA1.1.GA1.1.1074365313.1746699816; __gads=ID=cb691691a334e8be:T=1746699883:RT=1746699883:S=ALNI_MbEW7Q7xXWKXoQ9qiQ4FIeM5_9KDQ; __gpi=UID=0000101bac2671df:T=1746699883:RT=1746699883:S=ALNI_MbRLPlfaPweiMAOvpVI4lg6FhgzEA; __eoi=ID=b27019c447fc6975:T=1746699883:RT=1746699883:S=AA-Afjazu9Wf0rdpRupG_jdQIIEv; _ga_V7ZK73W7N0=GS2.1.s1746699816$o1$g1$t1746699884$j0$l0$h0; _chartbeat2=.1746699813190.1746699887527.1.P0lpIDDdYjMC699RXCwuRWsD1Hd08.2; _ga_BYLBCMMCG8=GS2.1.s1746699815$o1$g1$t1746699890$j54$l0$h0; _uetsid=7fd8a7402bf611f089fe2d3356360dcb; _uetvid=7fd8b0f02bf611f0821cad91654e1723",
    "Referer": "https://www.benzinga.com/recent",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
base_url = "https://www.benzinga.com/"
filename = "./news/data/benzinga/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers, timeout=5)
    if response.status_code == 200:
        resp = response.text
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one("#article-body > div:first-child")

        ad_elements = soup.select(
            "style,figure,script,.copyright,.sr-only,.adthrive-content,.call-to-action-container,.lazyload-wrapper"
        )
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        # 移除包含 "See Also:" 的 <p class="core-block"> 标签
        see_also_elements = soup.select(".core-block")
        for element in see_also_elements:
            # 定义需要移除的关键词列表
            remove_keywords = [
                "See Also:",
                "SEE ALSO:",
                "Read Next:",
                "READ MORE:",
                "Read More:",
            ]
            # 检查元素文本是否包含任何关键词或免责声明标签
            if (
                element.text
                and any(keyword in element.text for keyword in remove_keywords)
            ) or "<em>Disclaimer</em>" in str(element):
                util.info(
                    "移除无关元素: {}".format(
                        element.text.strip()[:30] if element.text else "免责声明"
                    )
                )
                element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # 使用requests发送请求
    response = requests.get(
        "https://www.benzinga.com/api/news?limit=10", headers=headers
    )
    if response.status_code == 200:
        body = response.text
        posts = json.loads(body)
        for index in range(len(posts)):
            if index < 2:
                post = posts[index]
                link = post["url"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    continue

                id = post["storyId"]
                title = post["title"]
                image = post["image"]
                description = post["teaserText"]
                if (_description := get_detail(link)) != "":
                    description = _description
                pub_date = util.parse_time(post["created"], "%Y-%m-%dT%H:%M:%SZ")
                if (
                    description != ""
                    and "Read the full article here" not in description
                ):
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "benzinga",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 5:
                articles = articles[:5]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response.status_code))


if __name__ == "__main__":
    util.execute_with_timeout(run)
