# -*- coding: UTF-8 -*-
# tipranks.py / tipranks_others.py / tipranks_announcements.py 共用的请求与正文解析。
#
# 2026-11 起 www.tipranks.com 全站走 Cloudflare 质询，没有有效 cf_clearance 的请求一律
# 403 "Just a moment"。cf_clearance 与过质询时的 user-agent / client hints 绑定，所以下面
# 的 UA 与 sec-ch-ua-* 必须和拿 cookie 的浏览器保持一致，换 cookie 时一起换。
#
# 同期详情页改版：正文不再放在 window.__STATE__ 的 JSON 里，而是直接 SSR 在
# <article class="tr-article-body"> 中。
import re
from curl_cffi import requests as curl_requests

# 首选档位沿用拿 cf_clearance 时的浏览器指纹；被质询后依次换下面的档位、且不再带
# cookie 重试。CI 实测（2026-11-17，最近 12 轮）详情页约 78% 被 403，其余同一脚本
# 同一时段能取到——是否放行取决于 runner 出口 IP 与指纹组合，而非全站封死，
# 故换档位能多拿到一部分；cf_clearance 绑定签发 IP，在 CI 的轮换 IP 上本就无效。
IMPERSONATE = "chrome"
FALLBACK_PROFILES = ("safari18_0", "firefox133", "chrome136")

CF_CLEARANCE = "Ci1CtpYclWI-aLZvYTvSKlH8tyJ4qFNehSd_EJQqGfR3GNlUfZaVAcEmj1iCjTbcjZXzaZHnp6aU-GAKUzR5H2bEoU0X3X5iFk1KS4-tdHV4EYt9X_TAhZDcPNIGxai72ChRyjluzGvIREOkpsfpMlVwld5uSij9tWFWk32kES4u2x7mfHpjtgjzLLxOMe75re4QNEGUbFWX13a9KBEINtPAPGG_5oI6aMdrpqlO7dYP2-RebPtxqfDCHl5aqEhFcMdFg9piIuGOnO2VxzQEzzJeIdwRy-dRseofceJEWvCyx-T7dfo-Mt9gPyhrR4I2D5cd8Yt8kGXptLGxQAHuh0G8JrRd56123WKY6vXh3Q7AYHfS6jfV-q61NL5ScMPV0_hnPgqqPRPR3qXLGdw_9vzQXnB7z1ruaeALkJINZLie3c7DsU9COrsMWEuy"

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'no-cache',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Google Chrome";v="155", "Chromium";v="155", "Not(A:Brand";v="24"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"155.0.8059.40"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="155.0.8059.40", "Chromium";v="155.0.8059.40", "Not(A:Brand";v="24.0.0.0"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36',
    "cookie": "cf_clearance=" + CF_CLEARANCE,
}

fallback_headers = {
    "accept": headers["accept"],
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1",
}

_session = None


def _profiles():
    yield IMPERSONATE, headers
    for profile in FALLBACK_PROFILES:
        yield profile, fallback_headers


def get(url, timeout=30, spider=None):
    """命中的档位缓存复用；被拒（非 200）时换下一个档位重试，返回最后一次响应

    spider 传入调用方的 SpiderUtil，用于把超时收敛进本轮剩余预算、预算不足时停止重试。
    """
    global _session

    def request_timeout():
        return spider.request_timeout(timeout) if spider is not None else timeout

    if _session is not None:
        response = _session.get(url, timeout=request_timeout())
        if response.status_code == 200:
            return response
        _session = None

    response = None
    for profile, profile_headers in _profiles():
        if response is not None and spider is not None and spider.out_of_time():
            spider.info("out of time, stop retrying: {}".format(url))
            break
        session = curl_requests.Session(impersonate=profile, headers=profile_headers)
        response = session.get(url, timeout=request_timeout())
        if response.status_code == 200:
            _session = session
            return response
        if spider is not None:
            spider.info(
                "request url: {}, impersonate: {} rejected with: {}, cf-mitigated: {}".format(
                    url, profile, response.status_code, response.headers.get("cf-mitigated")
                )
            )
    return response


def parse_detail(body):
    """从详情页 HTML 提取正文，取不到返回 ""。"""
    match = re.search(r'<article class="tr-article-body[^"]*">(.*?)</article>', body, flags=re.DOTALL)
    if not match:
        return ""
    result = match.group(1)
    # 正文外层 <div> 之后是 "Disclaimer & Disclosure / Report an Issue" 链接
    result = re.sub(r'</div>\s*<p><a href="https://www\.tipranks\.com/glossary/d/disclaimer-disclosure".*$', '', result, flags=re.DOTALL)
    result = re.sub(r'^\s*<div>', '', result)
    # 视频、广告位、推广
    result = re.sub(r'<div class="injected tr-jw-video[^"]*"[^>]*><div id="tr-jw-placement-video"></div></div>', '', result)
    result = re.sub(r'<div id="div-gpt-ad-[^"]*"[^>]*></div>', '', result)
    result = re.sub(r'<div data-announcement-top></div>', '', result)
    result = re.sub(r'<aside[^>]*>.*?</aside>', '', result, flags=re.DOTALL)
    result = re.sub(r'<figure[^>]*>.*?</figure>', '', result, flags=re.DOTALL)
    # 文末的分析师评级 / 股票数据 / See more / Trending Articles
    result = re.sub(r'<div class="tipranks-extra-content">.*', '', result, flags=re.DOTALL)
    result = re.sub(r'<div id="trending" class="trending-posts">.*', '', result, flags=re.DOTALL)
    result = re.sub(r'<p>See more .*', '', result, flags=re.DOTALL)
    result = re.sub(r'<p>For detailed.*', '', result, flags=re.DOTALL)
    result = re.sub(r'(<p></p>\s*)+', '', result)
    result = re.sub(r"(\n)\1+", "\n", result)
    return result.strip()
