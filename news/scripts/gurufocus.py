# -*- coding: UTF-8 -*-
import logging
import traceback
from urllib.parse import quote
import json
import re
from curl_cffi import requests as curl_requests
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

# 使用 curl_cffi 模拟 Chrome 以绕过 403（TLS/JA3 指纹）
IMPERSONATE = "chrome124"
API_ARTICLES_URL = "https://www.gurufocus.com/reader/_api/articles?v=1.8.07"

# Bearer 与 cookie 中的 password_grant_custom.token 一致，需同步更新
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU5NzU4MzI3NzBkZWIxZGFjZmUyNDY2ZDA3ZmExMzI5YTNmZTdlOTczNjMxYWZiNjY5ZmU5MWEwYjcwZDgzYWMzODAyNjEwZjlkOWFiYTM5In0.eyJhdWQiOiIyIiwianRpIjoiZTk3NTgzMjc3MGRlYjFkYWNmZTI0NjZkMDdmYTEzMjlhM2ZlN2U5NzM2MzFhZmI2NjlmZTkxYTBiNzBkODNhYzM4MDI2MTBmOWQ5YWJhMzkiLCJpYXQiOjE3NzIwMTgxMjMsIm5iZiI6MTc3MjAxODEyMywiZXhwIjoxNzc3MjAyMTIzLCJzdWIiOiIxNzEwNjcyIiwic2NvcGVzIjpbXX0.M1SvAD_oFnC9AchP5Ykigkk-8UNl_scxdCxsbXeuXNn9dKc5mmmRsKSK3lkrJB3grR6e909_CNDSZQF4zq4eaBVGzyjs5JvcmHH6raHluru8961rSxjIO15EPbXMpXdUGEuRp7N3Pns001lByw4O-FRmUQSYdpEzvmsQyqT2pq-B01DBX8o9z-JZpDNuxU6Ab8d0uU-WUlZ2KM5gUIERSrl8spOhHf4Rhw-V5g8vttlHY6UE4hfpHzIbEhkwauyt_ngVipH6U9kwThCo11PugnwF8Mmcs7o9Zy0rKh2qTYig29Xm_cupbSqkJV7pC6lkkSS8Xltpxk8uLGHBIMybxx_4H-MwgpRPuFCWcevc5CZIXzFIr-oEo5NCN2j1S4bWANDGS4gmxBNF-tqIlD_No6iX93pASQ7U4YWgdwIFtw9LZz3o8FLP7rBhNh5VRRJMKCo2Yi3gWicJwcledlWbXG0CSO7luxpNR6S_WnPsQq0tv6PP5ruOUn4nXYSYCXVvXJuvSrZmBhGmxW1avqa37DgTz3Un7-oQyV9-EatG6-HU_wuLGlhNng_XGWAV3-3IRE6FXdAIosIgSOQWF1zfazEsLCDFoVcvFTB-lNcigT3Zm9TkS6USOdBEdz0qifjgp3f51UZzSHX5pdamCnOSRzBn4bAoZbs2MzzxnUwARbs"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Referer": "https://www.gurufocus.com/",
    "cookie": "strategy=password_grant_custom; refurl=/latest-news/all/all; password_grant_custom.client.expires=1781277660; _gid=GA1.2.490994961.1772017872; _gcl_au=1.1.999200474.1772017872; prism_69655752=3099e6b2-5b91-4c06-af4d-22058c70855d; phorum_session_v5=ee840f1cb344a1b25850cbe5429b9d10:9b44c13474de6cbd34b805b8e337575b; password_grant_custom.token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU5NzU4MzI3NzBkZWIxZGFjZmUyNDY2ZDA3ZmExMzI5YTNmZTdlOTczNjMxYWZiNjY5ZmU5MWEwYjcwZDgzYWMzODAyNjEwZjlkOWFiYTM5In0.eyJhdWQiOiIyIiwianRpIjoiZTk3NTgzMjc3MGRlYjFkYWNmZTI0NjZkMDdmYTEzMjlhM2ZlN2U5NzM2MzFhZmI2NjlmZTkxYTBiNzBkODNhYzM4MDI2MTBmOWQ5YWJhMzkiLCJpYXQiOjE3NzIwMTgxMjMsIm5iZiI6MTc3MjAxODEyMywiZXhwIjoxNzc3MjAyMTIzLCJzdWIiOiIxNzEwNjcyIiwic2NvcGVzIjpbXX0.M1SvAD_oFnC9AchP5Ykigkk-8UNl_scxdCxsbXeuXNn9dKc5mmmRsKSK3lkrJB3grR6e909_CNDSZQF4zq4eaBVGzyjs5JvcmHH6raHluru8961rSxjIO15EPbXMpXdUGEuRp7N3Pns001lByw4O-FRmUQSYdpEzvmsQyqT2pq-B01DBX8o9z-JZpDNuxU6Ab8d0uU-WUlZ2KM5gUIERSrl8spOhHf4Rhw-V5g8vttlHY6UE4hfpHzIbEhkwauyt_ngVipH6U9kwThCo11PugnwF8Mmcs7o9Zy0rKh2qTYig29Xm_cupbSqkJV7pC6lkkSS8Xltpxk8uLGHBIMybxx_4H-MwgpRPuFCWcevc5CZIXzFIr-oEo5NCN2j1S4bWANDGS4gmxBNF-tqIlD_No6iX93pASQ7U4YWgdwIFtw9LZz3o8FLP7rBhNh5VRRJMKCo2Yi3gWicJwcledlWbXG0CSO7luxpNR6S_WnPsQq0tv6PP5ruOUn4nXYSYCXVvXJuvSrZmBhGmxW1avqa37DgTz3Un7-oQyV9-EatG6-HU_wuLGlhNng_XGWAV3-3IRE6FXdAIosIgSOQWF1zfazEsLCDFoVcvFTB-lNcigT3Zm9TkS6USOdBEdz0qifjgp3f51UZzSHX5pdamCnOSRzBn4bAoZbs2MzzxnUwARbs; password_grant_custom.refresh_token=def5020050cce0bd860031d0ef473590306987c1e24b077962a5b29b1dbbf471c7dc921af9b577b44b6519533ee992de6085ff7280891a70fbb586609910b06c1f2b6928986ef1a99e2535a7d7afac0f808b29ca8f3e9e622b14ac430e529a7cb992e265ff74ba3c68d0c4ffeceff5331e982e3b4651874a66eb8ce3d4557095ea23b01c0cedc63a5600cda38add2c17a166e47312a38972ab1cdb6bc7205f014e48b67c369774ef6312e56ad748ef117000219ad5b5d97f2be00225681ea641e46c8f2db86093aa2ceeb18c6cbd54da91c42feaced8237f2294043357575460331d6e8d9f92e963b214a82927de7843ef606b867cdcbfea8d4b2456dc1fb1c6cf109ce79c97f4c828d8a75a93b3ac4186772c465476446e1b12acb8a2ac73ee3261338611857d23f632c7caee481e36dc78fd2b705492e7231ea14386e1ee0744d10bfafb17c741066b437d17644ce5ffc1ebbaff1fd4d91ce4e9ee94c8111f767a2be4aa; password_grant_custom.expires=1777202123; original_ref=false; refsite=https://www.gurufocus.com/social-login?platform=google&username=118366726857149582815&ref=%252Fpricing; upgrade_counter=1; password_grant_custom.client=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjY0MTA4NTJhODZmMGM3NzMyMzBkMzQ5MDVjOWI3NjYwZTRlYWRkNGZlMGIzM2Q1ZjIxY2JiYWUzYzU3MWEyOTZkNWY3MjgyODdkNjU0ZjhlIn0.eyJhdWQiOiIyIiwianRpIjoiNjQxMDg1MmE4NmYwYzc3MzIzMGQzNDkwNWM5Yjc2NjBlNGVhZGQ0ZmUwYjMzZDVmMjFjYmJhZTNjNTcxYTI5NmQ1ZjcyODI4N2Q2NTRmOGUiLCJpYXQiOjE3NzE5Mzg2MDIsIm5iZiI6MTc3MTkzODYwMiwiZXhwIjoxNzgyMzA2NjAyLCJzdWIiOiIiLCJzY29wZXMiOltdfQ.pts8PJNyj7FdOQGxyL3FOV6WzDxCrOxQfIxlNiT_4rS18NK0xKaGRLDBkdURykuqAGzJbu_CWnY0U42NzPjUWHTP7BGApjbM3BTs0uC70X79yWv9YKaY7U1zz9zpcze-IAlTsvvHwPdnA4AB5theJEw2lkW1IHfCMVzhEBAqBDw7n8qkJicE29rEDrLueytcihCT8ZT_BDp-LhUhGU3RgM0j9EbR1W5T4-rqfEX-t2sWfjdinYPE9hdm5POsLO3aYJTCreqDpRaO9K4arJNqHfRoA5-OqA2HTS4ABgn-SW9nugAE0WYjJKaXGMKzhQJUusUrhVuwXb10l0wYN5jlaQF2-WyhxxlGhu9-8IlVWjR88Dv2C9iQmgnmwTjG5Rplp-_F59hD17Komyc1fi4Sp4yjHKqU1Vn4O6LpAViiVEo1i1szJGBqt2qxG45-QghyG0pzm5jhK6aEewA7eFHc2KhKEFDBAc08riV1RaxSxmpZAb4s5ndcGAjXFBcoMlWF35pXk4TH1qVjfjckOA0c_hFDZTwwYh3ng1l8i6GU9cSCaYzFdkScieQSQX3_ZSz1jmmWOYMzUEW-uBhz634fR-ISqVIb4qHBk-A_G84T8nnzQSLXTUgyA7ScxNmLaXL08P0g360lwLt8849Y1kQpq8uw9WnQ8VtjXNTED-lt1dk; homepage_upgrade_counter_ads=1772104532; g_state={\"i_l\":0,\"i_ll\":1772018133996,\"i_e\":{\"enable_itp_optimization\":0},\"i_b\":\"+mak6422e4QRtLQMQZ1XAkkKIgneguRJTcNxJGAwF6c\"}; cf_clearance=QQHWwOdq_EUfmVocCJiN9jZJOSXcFnrGa2lE2SOkGhI-1772070507-1.2.1.1-1_qtF.dgp3fHViXy8fP7huuKsLIK.fre13ZVhVTA3IhsHESke9L2qJjk3hZdCBIi0tlF6ZyiiDWltwxHVvZkSyWZHAInzgYvKramVh_xOP8MdKs4BXWhmQDMYdQp1sM1.yo899winVNWX8VnGMaxb7XzQRcNJfsv98E9TXvTgEGfF9RPGMtxgaW7mKEHuqHNU_p8ClPIiWrZft6q9y_psDnvBzGNdtyUVZDj_jbGk6s; _ga_T14K4LKYZE=GS2.1.s1772070429$o2$g1$t1772070508$j60$l1$h1364957089; _ga=GA1.1.1163599393.1772017872",
}


def _api_headers():
    """文章列表 API 请求头（参考 curl）"""
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "authorization": "Bearer " + BEARER_TOKEN,
        "content-type": "application/json",
        "origin": "https://www.gurufocus.com",
        "priority": "u=1, i",
        "referer": "https://www.gurufocus.com/latest-news/all/all?page=1",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "cookie": DEFAULT_HEADERS["cookie"],
    }


_curl_session = None


def _get_session():
    global _curl_session
    if _curl_session is None:
        _curl_session = curl_requests.Session(impersonate=IMPERSONATE)
    return _curl_session

base_url = "https://www.gurufocus.com"
filename = "./news/data/gurufocus/list.json"
util = SpiderUtil()


def get_detail(link):
    util.info("link: {}".format(link))
    try:
        response = _get_session().get(
            quote(link, safe="/:"),
            headers=DEFAULT_HEADERS,
            proxies=util.get_random_proxy(),
            timeout=30,
        )
    except Exception as e:
        util.error("request: {} error: {}".format(link, e))
        return ""
    if response.status_code == 200:
        body = BeautifulSoup(response.text, "lxml")
        soup = body.find(class_="main-body")
        if soup is None:
            util.error(
                f"Error: 'main-body' class not found in the response. Link: {link}"
            )
            return ""

        ad_elements = soup.select(".ad-container")
        # 移除这些元素
        for element in ad_elements:
            element.decompose()
        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response.status_code))
        return ""


def _api_body(page=1, per_page=20, cat="column", start_year=2025):
    return {"page": page, "per_page": per_page, "cat": cat, "start_year": start_year}


def run(_link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    try:
        response = _get_session().post(
            API_ARTICLES_URL,
            headers=_api_headers(),
            json=_api_body(),
            proxies=util.get_random_proxy(),
            timeout=30,
        )
    except Exception as e:
        util.log_action_error("request error: {}".format(e))
        return
    if response.status_code != 200:
        util.log_action_error("request error: {}".format(response.status_code))
        return
    try:
        resp_json = response.json()
    except Exception as e:
        util.log_action_error("api json error: {}".format(e))
        return
    items = resp_json.get("data")
    if not items or not isinstance(items, list):
        util.log_action_error("api response has no data list")
        return
    for index, node in enumerate(items):
        if index > 1:
            break
        title = node.get("subject")
        message_id = node.get("message_id")
        if not title or message_id is None:
            continue
        link = base_url + "/news/" + str(message_id)
        if link in ",".join(_links):
            util.info("exists link: {}".format(link))
            break
        description = get_detail(link)
        if description:
            insert = True
            _articles.insert(
                index,
                {
                    "title": title.strip() if isinstance(title, str) else str(title),
                    "description": description if isinstance(description, str) else str(description),
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "gurufocus",
                    "kind": 2,
                    "language": "en",
                },
            )
    if len(_articles) > 0 and insert:
        if len(_articles) > 10:
            _articles = _articles[:10]
        util.write_json_to_file(_articles, filename)

if __name__ == "__main__":
    # util.execute_with_timeout(run, "https://www.gurufocus.com/latest-news/all/all")
    util.info("403 Forbidden")