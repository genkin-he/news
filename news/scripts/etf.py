# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
import re
from util.util import current_time, history_posts
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"128.0.6613.138"',
    "sec-ch-ua-full-version-list": '"Chromium";v="128.0.6613.138", "Not;A=Brand";v="24.0.0.0", "Google Chrome";v="128.0.6613.138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_gid=GA1.2.449000181.1727426772; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIFYAODgdgGZ%2BAFg4AmfhwAMARin9eQ6SAC%2BQA; _pcid=%7B%22browserId%22%3A%22m1khatllnsq3v5iv%22%7D; __pnahc=0; __qca=P0-1797951138-1727426771953; cX_P=m1khatllnsq3v5iv; __pat=-14400000; __pid=.etf.com; __pil=en_US; FCNEC=%5B%5B%22AKsRol-KjpAWWIXYfmWIXdMnl991c-CHl9fNsd9RT8fbDjAccumkpeWSVWIawr2BeSRbwt5GBWySkgf_8FDYZQ7K3P4kXyWO7Fp1THwnypNC98Xxto6vU5WNTrbN-qDjuZzQDwlN_-2JFcoSNvwstMXPyLpBIYtkXA%3D%3D%22%5D%5D; __gads=ID=2304be3f9af063c9:T=1727426771:RT=1727432962:S=ALNI_MboRxC4514igGybFtPmXthgP7_Wrg; __gpi=UID=00000f20419ca802:T=1727426771:RT=1727432962:S=ALNI_MYgoPIQIilCju1wYDVg0Gm_zjy-EQ; __eoi=ID=ada6aa49a3a35f85:T=1727426771:RT=1727432962:S=AA-AfjZyXGqyWJ0uTYg_JRk_5PGo; _gat_G-NFBGF6073J=1; _ga=GA1.1.93062885.1727426771; _ga_NFBGF6073J=GS1.1.1727432559.2.1.1727432964.38.0.0; __adblocker=false; cf_clearance=Kgoin2AOH.NmP5Tsr2ZoCRa0_PaznQmCqia7NuVCCgg-1727432965-1.2.1.1-FNVMSKQiiGgDRwv157Y1aV9ifOa6HFZngoleUReKLV28zL.TULfbNJ_xTs7hTK6vsRCnKwEy9COMjfSfXRpC6Z1_JDhPYl7T0zU48RX5YBWFu4jx8ASDC3BQWQYv1hK6ycNFfqhQInhkpCe0gy_TXoKo9.aoOHDBdC4ySsw46bZYy.fy8PmXqEjbOPYZGADfwz6MSICeH5ko5KGfTqTm4WnmXLIX3mGI3tkDkErBr6pdc8TtFmMENer06_s63dnc73dpeWRsc1cKiwoo85wFqS0uaKz6eDq9O.gvPSmjzFC4FeTEpeM9C0DB5vzafZ1Rbtw8IukgAX99tNwBFfBUU3NaTEvzreDzZ15HAX_vn711YsK1u7a9Olr29su0S1zTvvVjlcbX2tEtwRTjTcdgEQ; __pvi=eyJpZCI6InYtbTFra3F3ZndjeGVzbG4yNCIsImRvbWFpbiI6Ii5ldGYuY29tIiwidGltZSI6MTcyNzQzMjk2Nzc4NX0%3D; __tbc=%7Bkpex%7DK7u4uKN9sGLKh7MITohUYx95FdtggQ3w_U33m1heb2xTRRif_AqPojRPKKlo0Foa; xbc=%7Bkpex%7DGabJte8ORgVD3LewbRzghJE45TBInetKF_Olx88n7ew-UP1bGOFOUsSUITLYRHt-IlKx2xsJDID9UVXg5dG-zybIP6zhyGzFnDN2Hx4VLoNwp9q6rvzPlDmzODFbuKSe3v7k7g70mvEE7A0oZ4zEMQ",
}

base_url = "https://www.etf.com/news"
filename = "./news/data/etf/list.json"
current_links = []


def get_detail(link):
    if link in current_links:
        return ""
    print("etf link: ", link)
    current_links.append(link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        body = BeautifulSoup(resp, "lxml")
        soup = body.select(".etf_articles__body")[1]
        ad_elements = soup.select(".caas-da")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        print("etf request: {} error: ".format(link), response)
        return ""


def run(link):
    data = history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        soup = BeautifulSoup(body, "lxml")
        items = soup.select(".image-card")
        for index in range(len(items)):
            if index > 0:
                break
            link = items[index].select(".image-card__title > a")[0]["href"].strip()
            if link != "":
                link = "https://www.etf.com{}".format(link)
            title = items[index].select(".image-card__title > a")[0].text.strip()
            if link in ",".join(_links):
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
                        "pub_date": current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": _articles}))
    else:
        print("etf request error: ", response)


try:
    run(base_url)
except Exception as e:
    print("etf exec error: ", repr(e))
    logging.exception(e)
