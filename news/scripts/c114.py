# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
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
    "cookie": "Hm_lvt_3d113c8324b108865d5f578fa799f678=1734919806; HMACCOUNT=6C8CECE5E323CD44; acw_tc=0a47314617349198059184624e004eae6896f2a34d92739480f1a086ab3d4f; ASPSESSIONIDSAADQTDB=MMMEDJJDNHCALCAAPILCJDMN; _ga=GA1.1.1062564735.1734919806; Hm_lpvt_3d113c8324b108865d5f578fa799f678=1734919821; _ga_YD8KXPNBE7=GS1.1.1734919806.1.1.1734919821.0.0.0",
}

base_url = "https://www.c114.com.cn"
filename = "./news/data/c114/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

# execute_with_timeout 的预算为 10 秒、CI 另有 gtimeout 15 秒兜底。请求若不设
# timeout，urlopen/requests 会无限等待，连接一慢就把整轮拖死并且零产出
# （日志表现为 "timeout: still running after 10s, aborted"）。
# 此处按本脚本的请求数反推每次请求的上限，保证最坏情况仍在预算内。
# urlopen 的 timeout 对每次 socket 操作各计一次，最坏约为该值的两倍；
# 且截止检查无法中断已发出的请求，故取值需留足余量
REQUEST_TIMEOUT = 2  # 1 次列表 + 最多 2 次详情，最坏约 12 秒 -> 由截止检查兜底
# 列表页 66KB，从美国 runner 拉境内站点时常见「每片都不超时、整体却极慢」，
# 表现为整轮零产出被看门狗打断。给读取本身加总时长上限，慢就尽早放弃换一次重试。
READ_BUDGET = 3.5
LIST_ATTEMPTS = 2

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    try:
        response = urllib.request.urlopen(
            request, timeout=util.request_timeout(REQUEST_TIMEOUT)
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, repr(e)))
        return ""
    if response.status == 200:
        resp = response.read().decode("gbk")
        lxml = BeautifulSoup(resp, "lxml")
        # 正文容器缺失时跳过该条，原实现直接取 [0] 会抛 IndexError 并中断整轮
        nodes = lxml.select(".text")
        if not nodes:
            util.info("content not found, skipped: {}".format(link))
            return ""
        soup = nodes[0]

        ad_elements = soup.select(".ad")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def fetch_list():
    """列表页：读取超预算就重试一次，两次都不行才算失败

    连接与读取的上限都按「剩余预算」现算：第一次尝试最坏 connect 2s + read 3.5s，
    若不预先扣掉这部分，第二次尝试会把整轮推过 10 秒看门狗（CI 日志里 #148 的
    "timeout: still running after 10s" 就是这么来的）。
    """
    for attempt in range(1, LIST_ATTEMPTS + 1):
        # 剩余预算不足以再跑完一次「连接 + 读取」时就不要再试了
        if attempt > 1 and util.out_of_time(reserve=REQUEST_TIMEOUT + READ_BUDGET + 1):
            util.info("out of budget, stop retrying list page")
            break
        request = urllib.request.Request("https://www.c114.com.cn/news/", None, headers)
        try:
            response = urllib.request.urlopen(
                request, timeout=util.request_timeout(REQUEST_TIMEOUT)
            )
            if response.status != 200:
                util.info("list attempt {}: status {}".format(attempt, response.status))
                continue
            return util.read_with_deadline(
                response, min(READ_BUDGET, max(1.0, util.time_left() - 3))
            )
        except Exception as e:
            util.info("list attempt {}/{}: {}".format(attempt, LIST_ATTEMPTS, repr(e)))
    return None


def run():
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]

    body = fetch_list()
    if body is None:
        util.log_action_error("list page unavailable after {} attempts".format(LIST_ATTEMPTS))
        return
    resp = body.decode("gbk")
    soup = BeautifulSoup(resp, "lxml")
    nodes = soup.select(".content_c_list > .new_list_c")
    for node in nodes:
        if util.out_of_time():
            break
        if post_count >= 2:
            break
        anchors = node.select("h6 > a")
        if not anchors:
            continue
        link = str(anchors[0]["href"].strip())
        if link in ",".join(links):
            util.info("exists link: {}".format(link))
            break
        title = str(anchors[0].text.strip())
        post_count = post_count + 1
        description = get_detail(link)
        if description != "":
            articles.insert(
                0,
                {
                    "title": title,
                    "description": description,
                    "pub_date": util.current_time_string(),
                    "link": link,
                    "source": "c114",
                    "kind": 1,
                    "language": "zh-CN",
                },
            )
            # 逐篇落盘。站点在 CI 的美国 runner 上偶发极慢，而 urlopen 的 timeout
            # 管不住 DNS 解析、也管不住分片很慢的 read，整轮仍可能被外层 10 秒
            # 看门狗打断；那时若还没写文件，这一篇就白抓了。先写再抓下一篇，
            # 被打断也只丢未抓的部分（超时是否告警见 execute_with_timeout）。
            articles = articles[:10]
            util.write_json_to_file(articles, filename)


if __name__ == "__main__":
    util.execute_with_timeout(run)
