# -*- coding: UTF-8 -*-
import logging
import traceback
import requests  # 发送请求
import json
import re
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "referer": 'https://www.fidelity.com/',
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    "cookie": 'AP171348_HEADER_APP_SERVICE_COOKIE=%7B%22toggle%22%3Afalse%2C%22loggedIn%22%3Afalse%2C%22navigationId%22%3A%22e8b830eb8f75c5e701305c4d07061018%22%7D; MC=oCr981bL3x4Ah7l_vFF0lIu3mBASAmkEYkYSiPzmloPeiZRfqjMGBAAAAQAGBWkEYkYAP03; AKA_A2=A; bm_ss=ab8e18ef4e; _svsid=bd2653a943ca66c4a261c166d547c4bc; at_check=true; _cs_c=1; AMCVS_EDCF01AC512D2B770A490D4C%40AdobeOrg=1; AMCV_EDCF01AC512D2B770A490D4C%40AdobeOrg=-330454231%7CMCIDTS%7C20393%7CMCMID%7C10536888539231425703000179183234443481%7CMCAAMLH-1762499789%7C11%7CMCAAMB-1762499789%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1761902189s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.1.2; s_sess=%20s_cc%3Dtrue%3B; mboxEdgeCluster=38; ajs_anonymous_id=b202612b-81ce-4106-9e58-b7d0370cc1b7; npt=; _ga=GA1.1.137653250.1761895024; analytics_id=%7B%22externalSessionId%22%3A%22331549ac-06a7-4fba-8436-8fa38e74a055%22%2C%22analyticSessionId%22%3A%22%22%7D; _gcl_au=1.1.767873481.1761895026; bm_mi=451F52ACE0AE3498E28A5BA947690B06~YAAQnA7SF7HNsi2aAQAAmiMkOR3eK07FbIe/DUwNSM60z3w9BnRLH0sYQVjGUsUEVs4tl7MOh/PYSeUhA1YJP1w1xzwcdtab5Kg/da3FkBdAGe3/PR+JM9+EWXI9WbsFiR6y7SP6kTetNihKzKB8Vqe7d4qc8QzDeQScPvceEK6DZCS2GZqapSQy5m/HJmStWKd3JyDwf/TZd+CTcIQvDqRAbvz+1KJGUmPv7uioyzkbE+VPp1BSG3xRn8bHp7lTTiaf+8/h+6L2muAm3jlaeHHYZ6VVQ1gubPPgqKXiVpcWtftTUEQO6WWVrjAZmWOCUb4nUkJIm72AtDyF~1; _cs_ex=1758551549; bm_sv=E11AFDF111BD90780C33A6C2F347AF45~YAAQnQ7SF7UA9zGaAQAAv1AkOR2cMS01YlkvFHVUx93qvfimj41Eo2/s74N/losQrHPoWzafRy4OfEXv/KMgad+KpG5plZJMkIVgyNsQIzotl7VB9rqwJMPmpGoYs7Y18hVwTC53WC5x1ZAFBM3EfTF3v43kROQluSa2GOjVWSyRhOoUrFyVL07FHYZwPvFRd1bVbKF9B8pj0YCyEgDOXMfqa3NJOWV+f0UdA8WCyKOrMhXuW8ntE+vfa7hmxd9AGNDd~1; dmt_x=2b98d5770be34e2388f0e1c0ad25c81b; ak_bmsc=D942452E064F48A1FC51E35053D4C9C1~000000000000000000000000000000~YAAQof7DF41Mxi6aAQAAiGMkOR1i9UMDqBTJH6d2wvjp/+nu0Y+WY1uzDNrFrLrF1EHRNwjGEA609ZL1DpnPyzHf6z4w07U9TaRv+5i+HV4BovmusJYiAdDLC1sK0lUEebDB2Hg4YCfvA3hAOnIvtLiqATTLYDoxpXWc+CaFpNi5SVshEWz8OJshzLCavuV/VtFu6DIA/CsBBrBcymOhBR9Ke/nFUGTkWCzGBh3XGUTjXRQQpO65FPFpTS/wF7nC1KfZjUjilc5FfTs/lc3MYoV2itJsKeJPcFhdktth3bMP5cFB6lxWMFYQYee2iFO5nHcO8uWmGRBY9BjYaxkg5I81ObUFhRF3DX8f+IxsaGEfhTVjOJsimlyYShJn08Ov363InfTPWrBddaaTZkHkTdu6cVU4pxnlU7JduM7mAtsGfJsHLWEGq+5mc9VNtP89iwcQDlBj9Mc/gocsk2sZ8J5iLIBNjPVaCwxYNoG1/C7RJtVk7edIg8bimfhYN6IV1AeO; cvi=p1=690462461288fce69683de89945faa33&p2=&p3=&p4=&p5=&p6=&p7=690462461288fce69683de89945faa33&p8=&p21=&p22=&p99=; dmt_g=CN; dmt_t=SC; bm_so=0892B729CB740A7FD77798D5E4EB28D101AB7CF0E1596F3FB25F5023DE93686E~YAAQnA7SFy7StS2aAQAA2UM1OQWbeKToWz+M0kYeOKrDEqRUJHJQX5Q5d+OvnZ6o4WzJofurcpSSknFlER8hwN9ub3dGWn2Q8ZtNdt0aCGmsdF7vwj5L28z2HvsHjmZoCtWBt+q1JSFAiG6Wv7LGIKYO9eMSlvZEm3QwdWvJhbwUekctWMqWdBHDkUZNQjnGIRTZIghDNBIAiZJ9nrX8iXmvPDD+vCy5FmWk26s4Emf7f6NpGzza1dYuMbhT8f7YwqfyvdYtW98+IF1zXXe61sBgHkCGL9lCPGn/3VSG88zr8ec7915hfx8bTJSoO7I6PogZmXTke3LjD0FDF3ECA5bxYb/TJQvbJZ5vGOTXfOwzjo3kiSSfooqAjNvWvHpVGvj0fMuFe41caSJe/HvCMIRuG84e/5UjbnTY1JVTAkFSDRdr0pkCr5BIaU5VMFVsB+Drh+evFe4n7PqRQQOuR4T+; X-csrf-token=baa615dc161ebcf886c63e324b19d90554bd596f7eb3ebd74ca85edb109ff908f76300b1d33d36f024924a2364b221100ad015e1d177bf7b6a44af776e3adaf30daa7ecacd0b1117140431449d31b4c0de824e027311686b999d123c5fc5246826b02b274867465a513bf3206e705a52d452f00f70e12c01293b83ceb28cf731%7CTop%2520News%2520-%2520Fidelity%2520Investments; connect.sid=s%3A1wOQn8LiTV7Yu90LtVgAuE7Lq4_CyX4x.0MjtUd1zMgSVTd0BJNnOygxRcHe%2BKnkAlA4tYrMuz4Q; f_csrf_check=baa615dc161ebcf886c63e324b19d90554bd596f7eb3ebd74ca85edb109ff908f76300b1d33d36f024924a2364b221100ad015e1d177bf7b6a44af776e3adaf30daa7ecacd0b1117140431449d31b4c0de824e027311686b999d123c5fc5246826b02b274867465a513bf3206e705a52d452f00f70e12c01293b83ceb28cf731; _abck=659ED76CCA5FC445C69430AD2593D902~0~YAAQnA7SFxfZtS2aAQAAcnE1OQ7TjmvUnv+zRtMp7hTpAzHE1Yf/tV7CzsrPs6tPmCi7RSH/qCgIAIYTXULdvwlUZ70SB6LBoeExb9JG+jZLQCX/tIOCHDLN/UEp1dkAp3wR9Fg+K3PHIra0CtO1j1Pw4N9Lo9G/twTKZK00w8JxkZCDZTn2LfBXe2doP/OzInrWndyS+qLiRsVeg70S12nqzVdDWZ6LDlg86t/DT8krcy0sj+KTo6ff4DPvdWf00Vujk4McE7rUXdnYADPHmzL0hnIm5NfeQRTMppm3aiyJNkbZc4Sxpnifq23Zq3LLa3vMxmM4JrWOrnKGng5ib+33T5zDKZZRgAB3LZ7VrOX4wiNjO/RHJHr8a1Fckw6j4brxutTIoaRYI8g+/JuWpubQ77amM0I3RagRynWhKyO0MRDIU/jVh64hegt587zXQyPlPuNLE9Lqoq2BoDigiDORy1ppruCOayR++fiRt0mFKOOnqFNMXPwRtA/K+7bo7NMi/IFiMNPfzT0iA8qbO+dRiI0qtAZIbYqHnYZOkNlf+FXeQyaV6ruLp83eRc5J2vvej3LvwPZKmnBjPYX4ZgFQxT1uFD9Gvv0h+u69A+tPacj7C6HhumfF2xJUKqO+oJE4zTKYoYgaeM+exzq/zA/1HwaFEMVZn8fIkP3Kx4ut2kvPjyDApcqmABBYfnvM2G1YUmHFxIVRFNpopFK2kpzFB4FBRbZNravGs1fQcG4ELN5o/+4ayjYdpYsVWdrcBfCBz1GGY6r13zZUFUhkYdVJu8kIB7mydIgHqsraT0qSFhpJHsvNBFitNMsLA2Vx44ULXVoN30Ip1xus1WjwhcuKdYogmljax1xg/+iz6Cc+EBc80g==~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f4HkRfsCAcSy7MZX+4iOaICy%2fAjzcGAhkHtqhBuJk76btxObC%2flqJLboqX7z+%2fgfpiJJ+sATf0qUD1QDc2kJgZ6dcDmLpusasyVhSMiibZvwAXB59mVct57Er%2fGF8oS2evATbuCA7zTqJf4lbtF6cEUtZzkj1+cKOlfcIR9Bpg%3d%3d~-1; bm_s=YAAQnA7SFxjZtS2aAQAAcnE1OQRdZhLMYiOBpkUnXhopWcJf6b9qYJZZi39dTML/Zx4PTWJOHYy5bykMutDrNcWyne2pSPJx0S1FeYxtndcmxUdUHgvrRk/K1TU/ydQ3iWNiW/tA2Qspmiy2mLQRtPgVL0ymRfotYtVG9H1b2enwDvi1p/OriCVjmKcPxJFLVyGnE6BpMi/WRriwspi41sN6GjfK/q7ESCll4qNaPlWBhYRXceOrdmd/SD1anVd7pwk/iP2DstX94/NWx7KIqMFTkeax2Emq8GgGwxgvlZ/dxSEgTJI2Fa7FRtZaBhHEH5yv7CIe4wMK7bhEPGcCGxVxXvIiAVlIQzTVVzICFaHL1NZqzHo+VWFmcqSWnjCah8vn0YPi1VKQYwYwCKOyqDrUs01K8M/KVz8Uo3PKaCsIBIs38gOzeYfskt3j2fiOM6sPlaIdTgwcubIPPy2Vs6C+vjb3vUh4B0ahzyswZiZUM5pvQ/a9XLlXKR+ZevGhYSjGFSVyaKBH3GqEDuy0ndqexWs7AEqGPD9EwNJfnLVgT3E15xMEBekZo1kdcBZsnEp9zB2lu8GjpQ==; bm_sz=22143B651B16085CC81D54031510F4EA~YAAQnA7SFxnZtS2aAQAAcnE1OR07h+77YL9rsN9shFtqHripBvBdqejtySSZfrxSrwpJB7k/OIyLMNmkEJGQY0IsM+xpiKWPUFJt5xnIEx8ohEXhHtNHUbZQqsfxZ25lC1TtKI+ZaSsVPPVqdLVay/+RKzdMLnbq2rmYNYExNtmJVE/KUbbH38C8PshBqr+psyt33i3U889EVKRZNj8Gh0F5xbc4ZyhrdYjYskJ+dLWOBIDaIEA4nSc1oXI4dCmEp1bdWXAVnD5ZVUAaxgL3Zp1C1x+u/X2qMJZ14g3NH14TIpTQqy+/WSZaAcutrJ+CBbaRqzA2Sadn2Nw/WsGWZTI//YCPOumkgEnwckPCML9bJWy+ixBq15UVTQMTPsjGYTX2+P50YsDikGoLqYWLDpqy9Ujbw4gGJ481ohxuK1AdQkAWLLc+JfcMTneqihPkFxM4k6RkzwSBpXX2a32Tlq626UeTogiUU1s2BtOSeIeqKTeegMsyFNwafaeNwd2yattTxsPf8O2KG14BWjXVC0vh418=~4405299~3752757; _ga_GL9JN8SMCE=GS2.1.s1761895024$o1$g1$t1761896396$j60$l0$h0; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+31+2025+15%3A39%3A56+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=https%3A%2F%2Fwww.fidelity.com%2Fnews%2Foverview&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; mbox=session#0e8e94f4671d4cfdb393f8740a476fb0#1761898257|PC#0e8e94f4671d4cfdb393f8740a476fb0.38_0#1825141197; bm_lso=0892B729CB740A7FD77798D5E4EB28D101AB7CF0E1596F3FB25F5023DE93686E~YAAQnA7SFy7StS2aAQAA2UM1OQWbeKToWz+M0kYeOKrDEqRUJHJQX5Q5d+OvnZ6o4WzJofurcpSSknFlER8hwN9ub3dGWn2Q8ZtNdt0aCGmsdF7vwj5L28z2HvsHjmZoCtWBt+q1JSFAiG6Wv7LGIKYO9eMSlvZEm3QwdWvJhbwUekctWMqWdBHDkUZNQjnGIRTZIghDNBIAiZJ9nrX8iXmvPDD+vCy5FmWk26s4Emf7f6NpGzza1dYuMbhT8f7YwqfyvdYtW98+IF1zXXe61sBgHkCGL9lCPGn/3VSG88zr8ec7915hfx8bTJSoO7I6PogZmXTke3LjD0FDF3ECA5bxYb/TJQvbJZ5vGOTXfOwzjo3kiSSfooqAjNvWvHpVGvj0fMuFe41caSJe/HvCMIRuG84e/5UjbnTY1JVTAkFSDRdr0pkCr5BIaU5VMFVsB+Drh+evFe4n7PqRQQOuR4T+^1761896396998; s_pers=%20visitStart%3D1761894988685%7C1793430988685%3B%20gpv_c11%3DFid.com%2520web%257Cnews%257CNews%2520Homepage%7C1761898200053%3B; QSI_HistorySession=https%3A%2F%2Fwww.fidelity.com%2Fnews%2Foverview~1761895028397%7Chttps%3A%2F%2Fwww.fidelity.com%2Fnews%2Farticle%2Ftop-news%2F202510302131RTRSNEWSCOMBINED_KBN3M52PH-OUSBS_1~1761895078969%7Chttps%3A%2F%2Fwww.fidelity.com%2Fnews%2Foverview~1761895271833%7Chttps%3A%2F%2Fwww.fidelity.com%2Fnews%2Fus-markets~1761896191818%7Chttps%3A%2F%2Fwww.fidelity.com%2Fsitemap%2Foverview~1761896213753%7Chttps%3A%2F%2Fwww.fidelity.com%2Fnews%2Foverview~1761896235809%7Chttps%3A%2F%2Fwww.fidelity.com%2Fsitemap%2Foverview~1761896372526%7Chttps%3A%2F%2Fwww.fidelity.com%2Fnews%2Foverview~1761896400477; akaalb_www_AWS_ALB=1761897307~op=EAST_AWS_WWW:WWW-EAST|:~rv=76~m=WWW-EAST:0|~os=f1162b9d355bd32846e2d2dc4b3e9a05~id=070ae8aa599a5b8a6cc594abfdaf21a7; _dd_s=logs=1&id=f00b473b-e425-48de-a458-f64154b0d714&created=1761895023619&expire=1761897412933'
}

base_url = "https://www.fidelity.com"
filename = "./news/data/fidelity/list.json"
current_links = []
util = SpiderUtil()

def extract_js_variable(body, var_name):
    try:
        parts = body.split("var " + var_name + "= ")
        if len(parts) < 2:
            util.error("Variable {} not found".format(var_name))
            return None
        json_data = parts[1].split("</script>")[0].strip()
        # 如果以分号结尾，去掉分号
        if json_data.endswith(';'):
            json_data = json_data[:-1].strip()
        if json_data:
            try:
                json_data = json.loads(json_data)
                return json_data
            except json.JSONDecodeError as e:
                util.error("Failed to parse JSON for {}: {}".format(var_name, str(e)))
                return None
        return None
    except (IndexError, ValueError) as e:
        util.error("Error extracting variable {}: {}".format(var_name, str(e)))
        return None

def parse_article(article_data, var_name):
    try:
        link = ""
        if var_name != "topNews ":
            link = article_data.get("link", "")
        else:
            guid = article_data.get("guid", "")
            if not guid:
                return None
            link = base_url + "/news/article/top-news/" + guid
        if not link:
            return None
        if not link.startswith("http"):
            link = base_url + link if link.startswith("/") else ""
        title = str(article_data.get("title", "")).strip()
        if not title:
            return None

        pub_date_str = article_data.get("pubDate")
        pub_date = util.current_time_string()
        if pub_date_str:
            try:
                pub_date = util.parse_time(pub_date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            except (ValueError, TypeError):
                try:
                    pub_date = util.parse_time(pub_date_str, "%Y-%m-%dT%H:%M:%S%z")
                except (ValueError, TypeError):
                    pub_date = util.current_time_string()
        description = ""
        try:
            description = get_detail(link)
        except Exception as e:
            util.error("Error getting detail for {}: {}".format(link, str(e)))
        if not description:
            return None
        
        return {
            "title": title,
            "description": description,
            "link": link,
            "pub_date": pub_date,
            "source": "fidelity",
            "kind": 1,
            "language": "en",
        }
    except Exception as e:
        util.error("Error parsing article: {}".format(str(e)))
        return None

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        var_data = extract_js_variable(resp, "articlejson ")
        if var_data and isinstance(var_data, dict):
            story = var_data.get("story", {})
            result = story.get("text", "")
            return result
        else:
            util.error("var_data is not a dict or is None")
        return ""
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run(url):
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        variable_names = ["companyNews", "international", "investingIdeas", "technology", "topNews ", "usEconomy", "newsUS"]

        for var_name in variable_names:
            util.info("Extracting variable: {}".format(var_name))
            var_data = extract_js_variable(body, var_name)

            if var_data and isinstance(var_data, list):
                top_two = var_data[:2]
                for article_data in top_two:
                    if not isinstance(article_data, dict):
                        continue
                    parsed_article = parse_article(article_data, var_name)
                    if not parsed_article:
                        continue
                    article_link = parsed_article.get("link", "")
                    if not article_link:
                        continue
                    if article_link in links:
                        util.info("exists link: {}".format(article_link))
                        continue
                    articles.insert(0, parsed_article)
                    links.append(article_link)
                    insert = True
                    util.info("Added article: {} from {}".format(parsed_article.get("title", ""), var_name))
            else:
                util.error("Variable {} not found or is not a list".format(var_name))

        if len(articles) > 0 and insert:
            if len(articles) > 40:
                articles = articles[:40]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.fidelity.com/news/overview")
    # get_detail("https://www.fidelity.com/news/article/international/202510310307RTRSNEWSCOMBINED_L1N3WC079_1")
