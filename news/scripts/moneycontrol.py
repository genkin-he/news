# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": 'MC_INTERSTITIAL_WEB_DFP_AD_LOGIC_20260117={"0":"https://www.moneycontrol.com/news/business/markets/"}; A18ID=1768637380908.477136; MC_PPID_LOGIC=normaluser2119941992873496mcids; _gcl_au=1.1.1241070444.1768637382; _cb=DU8Je6BZAJCMB0Og9E; _chartbeat2=.1757387119537.1768637382483.0000000000000001.CfWvxYBIjvKRC9VG2kDLD4Q71Caf4.1; _cb_svref=external; WZRK_G=ffb89247a88e48b3b6bab1eaef633627; WZRK_S_86Z-5ZR-RK6Z=%7B%22p%22%3A1%2C%22s%22%3A1768637383%2C%22t%22%3A1768637383%7D; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%220d3a384c-b876-49f4-927d-09139af56a4d%5C%22%2C%5B1768637383%2C113000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol9ZenMRcNH8-g-BqSxuLCIp4xus5TmcrD5zD_kbTI-ppYtCFydsNfMZ23OJDukq-OsQCMwA4yWHykbG_AbQqR7n7vA_5XDPiPgxG651Ultzj1BrIWpjhDkV5EQcY3BjZ42KVnDjQ0HQ5YFn3nHhmR8O-_HjIQ%3D%3D%22%5D%5D; cto_bundle=WMyvL195Q0FBS3BpckxURUt4WmxwZVVDVTZTR3RHWDhtUDRab05UMHUlMkJZQ3dqR1pWRXpiTUZDNFludjFtc3lDeGNVbiUyRm5wWmNNVWtSU2ElMkJ0cUlSd2RZR2UybUVmZE5vT2RYYlNTMllzZlR2Z1l1eGg5VlJsUFpGb3lRSVhKazJNeFNHalFJcXdDbTkwYVh2aFRUYmF5TXNZMXElMkJza0VJaGtpV0dzRHlxNCUyQmxNTWUyMmtmMVpsQllOOFc4ZTclMkIlMkI4RkhFaEhhaGdWSzlTN1cwdnNDJTJCc1RBd0NXZyUzRCUzRA; __gads=ID=1891752888cfd71d:T=1768637386:RT=1768637386:S=ALNI_MYXZryFFSSvvgzE2wcd5rlwoamPxg; __gpi=UID=000011e5ead53463:T=1768637386:RT=1768637386:S=ALNI_MZXMTKFWbVUQKpOgZmhz3rW4TmKrw; __eoi=ID=31d0c833ad50d26f:T=1768637386:RT=1768637386:S=AA-Afjab080LqdUBwDUAYCPLEnTx; _ga_4S48PBY299=GS2.1.s1768637382$o1$g0$t1768637387$j55$l0$h0; pbjs_debug=0; _vdo_ai_uuid=8625a365-977b-4969-a548-38526cfbf1aa; _gid=GA1.2.2093008810.1768637391; _gat_gtag_UA_113932176_46=1; _ga=GA1.1.282582866.1768637383; _ga_8J9SC9WB3T=GS2.1.s1768637390$o1$g1$t1768637399$j54$l0$h0; _ga_HXEC5QES15=GS2.1.s1768637391$o1$g0$t1768637400$j51$l0$h0',
}

base_url = "https://www.moneycontrol.com/news/business/markets/"
filename = "./news/data/moneycontrol/list.json"
post_count = 0
util = SpiderUtil()

# 2026-02 前后列表改版：#cagetory 下的链接由 h2 > a 改为 a > h2（标题包在链接里），
# 原选择器 #cagetory h2 > a 一条都匹配不到，静默零产出 9 个多月。
LIST_SELECTORS = ("#cagetory > li[id^=newslist-] > a", "#cagetory h2 > a")
REQUEST_TIMEOUT = 5


def get_detail(link):
    util.info("link: {}".format(link))
    # 视频与直播页（-liveblog-）都不是成文的文章
    if "videos" in link or "liveblog" in link:
        util.info("video or liveblog, skipped: {}".format(link))
        return ""
    request = urllib.request.Request(link, None, headers)
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status != 200:
        util.error("request: {} error: {}".format(link, response.status))
        return ""
    resp = response.read().decode("utf-8", errors="ignore")
    body = BeautifulSoup(resp, "lxml")
    # 原实现取不到 .content_wrapper 时回落到 select(".disBdy")，返回的是列表，
    # 取不到时会把字符串 "[]" 当正文入库
    soup = body.select_one(".content_wrapper") or body.select_one(".disBdy")
    if soup is None:
        util.log_action_error("article content not found: {}".format(link))
        return ""
    for element in soup.select("[class*=-ad]"):
        element.decompose()
    for element in soup.select(".related_stories_left_block, script, style, .social_icons_list"):
        element.decompose()
    if not soup.get_text(strip=True):
        util.log_action_error("article content empty after strip: {}".format(link))
        return ""
    return str(soup)


def run():
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(base_url, None, headers)
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(resp, "lxml")
        nodes = []
        for selector in LIST_SELECTORS:
            nodes = soup.select(selector)
            if nodes:
                break
        if not nodes:
            util.log_action_error("list page parsed, but no article node matched")
            return
        for node in nodes:
            if post_count >= 5 or util.out_of_time():
                break
            link = str(node["href"]).strip()
            title = (node.get("title") or node.get_text()).strip()
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                break

            description = get_detail(link)
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "MoneyControl",
                        "pub_date": util.current_time_string(),
                        "source": "moneycontrol",
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
    util.execute_with_timeout(run)