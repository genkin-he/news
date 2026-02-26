# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'en-US',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": 'macOS',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": '__cf_bm=tczc15vS9GtpmPpyomOBN6gazzWY8yQ2Ku2zhjI5938-1758079541-1.0.1.1-yjzlixa1nl175ndGt9TcEO17GSYDPAshzpNu9VupXbU8Kxp6vXyQ7G.ESjSjbVaLPwS_G.5JryIOQ78T02PHgTUS1FPh8Drj34lty9utx_8; mrf-client-id=cf0b8868-636e-478f-99e1-db38ec5e5c3d; cf_clearance=TsB2Yy6o9L5qvLsdjmrK2raIdm9ZVEJk9KU1cAwvrxo-1758079550-1.2.1.1-WfNT3yq7R3DUMADt9HUtRQRj_SslwGRou1QQ35tgZALlMnunFiZkIsEvQQUzTBB6YI75VtewfaLPQawVF52Ohe9wHpGU.2fkbkXQ0qTXLoHVJ.va7dvQ4ZCipLTKkiREHfEY_GsFTXs1BOXKF1igctuyrRuiU.DkfqlSqwSfwSISBuB4_bpB2OjfpATMBa2r.W7AJvLjTJqofI.YJ_FWbfuFSbxWP0NK825PzvMds5I; _gid=GA1.2.1384714074.1758079552; _fbp=fb.1.1758079554496.643985530465752040; __gads=ID=58b3a4feb20ccb43:T=1758079551:RT=1758079853:S=ALNI_MboB_AAW1nAVTLe2EFRFTXGSNmn-w; __gpi=UID=0000114c538909b4:T=1758079551:RT=1758079853:S=ALNI_MZBPi6JwCjdWMJU1gHGTlkT63FaUQ; __eoi=ID=797d5f020be1b2c1:T=1758079551:RT=1758079853:S=AA-AfjaJ4yJ-yY578J0A3gUymYGe; FCNEC=%5B%5B%22AKsRol9L5J6Vtcash6xErV8i94gngwwIvkKiWsTXoXoHdnqwe0r2hPFtAeSmHLJ0Uk8cO6imWs0Demj8KyN_OBFM_lyGOXYoLC8OSMnvwuh8vLyLtC3akpbioxFLTr64rv1ucCAGwnUUNrfr4IVSXYBNLXO1yvYskg%3D%3D%22%5D%5D; MCPopupClosed=yes; _ga=GA1.2.1311935280.1758079546; _gat_gtag_UA_18444479_1=1; _awl=2.1758079914.5-fccab06bcc9736a87012473123204e2d-6763652d75732d7765737431-0; _ga_BRWNS0TK1P=GS2.1.s1758079545$o1$g1$t1758079928$j45$l0$h0',
}

base_url = "https://cleantechnica.com"
base_path = "./news/data/cleantechnica/list.json"
current_links = []
util = SpiderUtil()


def get_detail(link):
    if link in current_links:
        return ""
    util.info("link: {}".format(link))
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8", errors="ignore")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select_one(".cm-entry-summary")
        if not soup:
            return ""
        ad_elements = soup.select("hr, div, figure")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        # 删除包含 "Support CleanTechnica's work through" 的 em 元素
        em_elements = soup.find_all("em")
        for em in em_elements:
            if em.get_text() and "Support CleanTechnica's work through" in em.get_text():
                util.info("删除 em 元素：{}".format(em.get_text()[:50]))
                em.decompose()
                break
        result = str(soup).strip()
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(link):
    file_path = base_path
    data = util.history_posts(file_path)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select("article h2 a")
        util.info("items length: {}".format(len(items)))
        for index in range(len(items)):
            if index > 3:
                break
            a = items[index]
            link = a["href"].strip()
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
                        "source": "vietnamnews",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, file_path)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://cleantechnica.com/category/clean-transport-2/electric-vehicles/")
