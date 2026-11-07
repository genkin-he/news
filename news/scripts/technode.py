# -*- coding: UTF-8 -*-
import base64
import hashlib
import os
import time

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from util.spider_util import SpiderUtil

util = SpiderUtil()

# 原实现是 technode.sh：用裸 curl（仅带 User-Agent、无 TLS 指纹伪装）下载，且从不检查
# HTTP 状态码，直接把响应写入数据文件——403 的错误页因此被 xmlstarlet 正常处理并覆盖掉
# 已有的好数据（technode_global.xml 一度只剩 141 字节的 "Error 403 Forbidden" 页面）。
#
# 两个站的拦截并不相同：
#   technode.global  Cloudflare 质询（"Just a moment..."）——chrome131 为 403，
#                    safari18_0 返回 200，换档位即可；
#   technode.com     Automattic 的 Hashcash 工作量证明（"Checking your browser..."）——
#                    所有 impersonate 档位一致被拦，需按站点 JS 的流程算出 PoW 再提交。
IMPERSONATE_PROFILES = ("safari18_0", "firefox133", "chrome131")

FEEDS = (
    ("https://technode.com/feed/", "./news/data/technode/technode.xml"),
    (
        "https://technode.global/category/news/feed/",
        "./news/data/technode/technode_global.xml",
    ),
)
MAX_ITEMS = 10
# technode.com 的 feed 有 2000 个 item、约 11 MB，下载本身约 2.3 秒；加上 Hashcash 必须等满
# 的 3.6 秒，单个 feed 的固定开销已接近 6 秒。此处不写死超时，而是按 execute_with_timeout
# 的剩余预算动态收口，既不会因为写死 6 秒而误杀正常下载，也不会拖垮整轮。
MAX_TIMEOUT = 8
MIN_TIMEOUT = 2

# Hashcash 挑战（与 pharmatimes 同一套机制）：_hcc 形如 "<hmac>:<base64>"，base64 解出
# "客户端IP|时间戳|token|难度"；找到 nonce 使 sha256(seed + str(nonce)) 以 CHALLENGE_PREFIX
# 开头，再把 base64(seed+nonce) 放进 X-Hashcash-Solution 头 POST /__challenge。
# 关键点：页面 JS 中提交前有一个 3500ms 定时器，服务端会校验该最小耗时，立刻提交会得到
# 400 且 _hcc 作废，故必须等满 MIN_CHALLENGE_SECONDS。
CHALLENGE_PREFIX = "0000"
CHALLENGE_MAX_NONCE = 2000000
MIN_CHALLENGE_SECONDS = 3.6


def solve_hashcash(seed):
    for nonce in range(CHALLENGE_MAX_NONCE):
        candidate = seed + str(nonce)
        if hashlib.sha256(candidate.encode()).hexdigest().startswith(CHALLENGE_PREFIX):
            return candidate, nonce
    return None, None


def pass_challenge(session, host, issued_at):
    raw = session.cookies.get("_hcc")
    if not raw or ":" not in raw:
        return False
    try:
        seed = base64.b64decode(raw.split(":")[1]).decode()
    except Exception as e:
        util.error("hashcash: bad _hcc payload: {}".format(str(e)))
        return False

    solution, nonce = solve_hashcash(seed)
    if solution is None:
        util.error("hashcash: no solution found")
        return False

    remaining = MIN_CHALLENGE_SECONDS - (time.time() - issued_at)
    if remaining > 0:
        time.sleep(remaining)

    response = session.post(
        "https://{}/__challenge".format(host),
        headers={
            "X-Hashcash-Solution": base64.b64encode(solution.encode()).decode(),
            "X-Hashcash-Host": host,
            "accept": "*/*",
            "origin": "https://" + host,
        },
        timeout=budget_timeout(),
    )
    passed = response.status_code == 200 and "_hcp" in session.cookies
    util.info("hashcash: nonce={}, post={}, passed={}".format(nonce, response.status_code, passed))
    return passed


def budget_timeout():
    """取剩余预算与上限中的较小者，至少留 1 秒给后续处理"""
    left = util.time_left()
    if left == float("inf"):
        return MAX_TIMEOUT
    return max(MIN_TIMEOUT, min(MAX_TIMEOUT, left - 1))


def fetch(url):
    """逐档位尝试；遇到 Hashcash 挑战则求解后重试。链内被拒记 info，整链耗尽才是失败"""
    host = url.split("/")[2]
    response = None
    for profile in IMPERSONATE_PROFILES:
        session = curl_requests.Session(impersonate=profile)
        issued_at = time.time()
        response = session.get(url, timeout=budget_timeout())

        if response.status_code == 403 and "_hcc" in session.cookies:
            util.info("hashcash challenge from {}, solving...".format(host))
            if pass_challenge(session, host, issued_at):
                response = session.get(url, timeout=budget_timeout())

        if response.status_code == 200:
            return response
        util.info(
            "request url: {}, impersonate: {} rejected with: {}".format(
                url, profile, response.status_code
            )
        )
    return response


def looks_like_feed(text):
    """写入前必须确认拿到的是 RSS，否则 403 错误页会覆盖掉已有的好数据"""
    return bool(text) and "<rss" in text[:2000] and "<item" in text


def trim_items(text, max_items):
    """保留前 max_items 个 item 后截断并补回收尾标签。

    技术上也可用 BeautifulSoup 重建，但该 feed 有 2000 个 item、约 11 MB，
    字符串截断只需 0.0001 秒（解析重建约 0.24 秒），且输出经校验同样是合法 RSS。
    """
    end = 0
    for _ in range(max_items):
        found = text.find("</item>", end)
        if found < 0:
            return text
        end = found + len("</item>")
    return text[:end] + "\n</channel>\n</rss>\n"


def process(url, output_file):
    util.info("fetching {}".format(url))
    try:
        response = fetch(url)
    except Exception as e:
        util.log_action_error("request {} exception: {}".format(url, str(e)))
        return

    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else "no response"
        util.log_action_error(
            "request url: {}, error: {}, keeping existing {}".format(
                url, status, output_file
            )
        )
        return

    if not looks_like_feed(response.text):
        # 这正是原实现的致命处：拿到 403 页也照写不误
        util.log_action_error(
            "request url: {}, response is not an rss feed ({} bytes), "
            "keeping existing {}".format(url, len(response.text), output_file)
        )
        return

    trimmed = trim_items(response.text, MAX_ITEMS)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(trimmed)
    util.info(
        "{} items written to {}".format(
            len(BeautifulSoup(trimmed, "xml").find_all("item")), output_file
        )
    )


def run():
    for url, output_file in FEEDS:
        if util.out_of_time():
            util.info("out of budget, stop before {}".format(url))
            break
        process(url, output_file)


if __name__ == "__main__":
    util.execute_with_timeout(run)
