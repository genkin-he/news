# -*- coding: UTF-8 -*-
import logging
import traceback
import requests
import json
import time
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "referer": 'https://www.businesswire.com/newsroom?language=en&industry=1000178%7C1778661',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'bw-ab-testing=%7B%220%22%3A%22A%22%2C%2210%22%3A%22B%22%2C%2220%22%3A%22A%22%2C%2230%22%3A%22A%22%2C%2240%22%3A%22B%22%2C%2250%22%3A%22B%22%2C%2260%22%3A%22B%22%2C%2270%22%3A%22B%22%2C%2280%22%3A%22A%22%2C%2290%22%3A%22B%22%2C%22100%22%3A%22B%22%7D; _gcl_au=1.1.1026421930.1759138802; _ga=GA1.1.100633507.1759138802; hubspotutk=977460cfe13e3612eabcb9873ef581ba; __hssrc=1; OptanonAlertBoxClosed=2025-09-29T09:41:23.701Z; bm_ss=ab8e18ef4e; bm_so=946366AE82A2A16C82DF8664BFDE9AC2BB9CAA1551D701C11B1F2C9AF9FA410D~YAAQnVAXAigeIXGZAQAA7dZ/mQU1ZcKCqhPwwW48MBJ8gjDvxKSul/ujaElRDTeJ0JqKsZNaWSpOlZc9CkxSAGRRuXr8Bw7ZukUngz+ps1JbBslGcPtAwzjzlBCJhA1p/2th7aWtnrnEkX9J90pzJsXiocQvGqI3IOA+c0zEIn6nsczwV4xWLszQ5xytVNBdn+7yG4aUhgZTO56UdFHTIdVY4YzTKY3CVxLSZSIL2mB3YPESaiKHOOoWyvEUl9/piPe53FgpGxRdhq7/4uOcqbO7xW8Yo69cBXI5DxdvlxaJb3rNwit+0zS/DBvgzoC2vnlSMDWOIhrZsdj2h39sI937HQvbFQrP6IiHPZxTmvB0bt/1ASObA4UZadwa+7q9I5YYmM1Aa7tf5lzabuOJPDqxB8sAeNmH0bUmKnlapbxYA09ViOB+MVE7DdiARk4yhw434e8fRyougGfOTxaTuOMNI6tBPA==; bm_lso=946366AE82A2A16C82DF8664BFDE9AC2BB9CAA1551D701C11B1F2C9AF9FA410D~YAAQnVAXAigeIXGZAQAA7dZ/mQU1ZcKCqhPwwW48MBJ8gjDvxKSul/ujaElRDTeJ0JqKsZNaWSpOlZc9CkxSAGRRuXr8Bw7ZukUngz+ps1JbBslGcPtAwzjzlBCJhA1p/2th7aWtnrnEkX9J90pzJsXiocQvGqI3IOA+c0zEIn6nsczwV4xWLszQ5xytVNBdn+7yG4aUhgZTO56UdFHTIdVY4YzTKY3CVxLSZSIL2mB3YPESaiKHOOoWyvEUl9/piPe53FgpGxRdhq7/4uOcqbO7xW8Yo69cBXI5DxdvlxaJb3rNwit+0zS/DBvgzoC2vnlSMDWOIhrZsdj2h39sI937HQvbFQrP6IiHPZxTmvB0bt/1ASObA4UZadwa+7q9I5YYmM1Aa7tf5lzabuOJPDqxB8sAeNmH0bUmKnlapbxYA09ViOB+MVE7DdiARk4yhw434e8fRyougGfOTxaTuOMNI6tBPA==^1759216917778; bm_mi=36E56B7FF54F86F17FBAF8665970E11C~YAAQnVAXArUeIXGZAQAANOR/mR3G/HNMzAr2CLkJP0KL0+I/QM2sJUzhYZmvuHZHEVVoSQjVGcgnwA/+40qd8m4yJpz7AAknZw2ypfzr0lnGmFXVXorS2EO+fVBAwn5YRRKPYeP+ln2KWWI3lrb2N7wUjy+Ayeqnto5J0+w502Gy5+CWTQkywSgTfL5gzCjJhR2qhqPLrcZaowvyabPISRLmGOnBTlbbl8SN42cz2UU64R89ZpKW0V0AGnBANWL13GI5/6oKN370Zpz7BMdEoAo1SGRM5OGmmG3uhCN6A1CxODZ1Ucfo9ud6tJxTdPzvPhKjO5pM2pf/LME=~1; bm_s=YAAQnVAXArYeIXGZAQAANOR/mQTfpHgRlTfNH/tguAKhaKKGTWGV81bpDLaPJIrfg05nkgrirm+schAXO+tmmMohMv6hvpaFSoCgUyrSnp5Z0OA8BXo/SWAazZmyf6XbJdOjdQt+jqI5+abEDpp/xo7r74goxqLbAE10NYYMkJfRlpnzf/i3Gb1xkLVMJ69ap89MnNNMaB2pOu9z+aGWA7clZNlaB/66HCb0sTdmaQN/aEhnqIcGDS8ByYiVtcdaIbe4OFt7oRwuIH03MNPnrnau5FXhq0ryI+Cf0jSrUIF38mXtJqi8JjzoUyXv0pnjISP7cLonlQRnOUw/VqBudvnY7DJtJZ0BQu4Ng79UE+5n9EM/dyuwkTSRWCeLxJVFx5OuAQXLundv8/dQn7An04ei0alLS5r9PxvsgJ7fEQ/rtrpTNBYDqPYhKcxt/wCEuhuk9viIjxNm+nmR/VWzD6Zbcyb6VBGWVZGTZ0HkoyO/A8wikXkhIhOKYY8+DZQDRwJ0RlDeNw3Zdz5fdEz7u1vpWFX1q3aUfKz5qnGEBmOqpOWwG5ORdyx98M0Xudt/4YvZaF1YN/l/30ikXsw=; bm_sc=4~1~66806802~YAAQnVAXArceIXGZAQAANOR/mQXVafGwYGqXuHytt5h63QrFaEtXWh327oweHXcFmkbhTmU8DuQDHwWFZl/9z3oaS3poqOfTxXu0tZUSBqef6BW+Sa7HPe8tcFyU9FdyruaYd5+HFGSq8gp3w3L76lp11ry7FnowoGz52PB/EF8V43FhKIWQw4hibaWBha7Z8WRMu+k4QP5kdT4wraX8P8Dt1DOlYcFFtdI3lCBpSxxBoNkySBC3cEuEKNgjBZ3HPiaruuX18u8KjOHhsR5Z12gdsQp4tiUm//gbuS6AzyHNSoCjXpKQwZxxetDiOid2BlvRDoyf7smv7ELO5wm78dU2Clq8M51Yl9oj60fhsxCdoYsLKd0Ld0DX1PEDnR2xe9eTfk2eczDf29eYFxyhQTqvWkXcB1+bWx1cFs1uCmsGPNojTvnGzhG0CEi+1ZvwP5FFqVecMS3gIgCrdl3dHhZe4fMxBXW98Hx0WKdGHQBrMjkhtikc; ak_bmsc=27A9FB6A9B6A1827F7543A6A6636CFB6~000000000000000000000000000000~YAAQnVAXAu0eIXGZAQAADOx/mR2mYa1wFa5l5apTf4wdOMzZB4R+wmvLM0Xnzx2942lCneDpmwjVT9/vV/UofWTe5Y/OtbsyrFtWa0WM9rDzcIe4d3+T46NZHWKcIob+iXliumOr9uVkoMyZ7siF+7dALgekqXGxz9I2N7QMfOEv41MTobItHBBkwKAKOp1L/3GZS9xzxGz9MM4NZmDkpXq27dqVbpMKWqRtPcM1BSJVjq9OktXugsJGSdIeX37vLdDfIaGg59gyAdJoRehdPIjjepe6km4nIVNLQ8rrUQgIwn95fOnQDGWfPA8Jc5Io6C8kVvxWoH0OzUviCbVU4IxFWw/Cv2VObbdMMoY+tkxrdUGLzDA46dE/n1sgCpsM3XWq62QK3US14Hq1SEay3uvcxnWJooGqY50TBbL1md+/Lj/bqou5GBFc//go33wqlTsIBj7OUsN3B3J3FvrQQmJZA6F2y+2NE1ZDQap6ZuWbh3ueDvib85CgxbGLIEFw; bm_sv=1D70805B35A1E5138AD1732A6E50BAAC~YAAQnVAXAgYfIXGZAQAAWO1/mR0YbpexQwVYZzHlArQjLrKdLXn5iQ40y5zgpBWUHBbM2tHJnd5hjN+505I94NV9k/jvrLeeKXp2vz89FOZ2QWDvI0IR/tcDQcisBDl5bsHfqvPuyNrg2d6KtpHyIiN/9mtC46JVFQFmlO7aj9F0gJQLJ0+I0DIwjQaChNP0CFBYmknbxlvxNE2ImZ+P8pTtQAU/Ny4DGQLIOlG04h5RlV/1tR5spGs3JQ2gbQJTzozGTUYq~1; OptanonConsent=isIABGlobal=false&datestamp=Tue+Sep+30+2025+15%3A22%3A02+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.4.0&hosts=&consentId=cfacf185-9359-42d9-bb11-c1ba4541054c&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1&AwaitingReconsent=false&geolocation=CN%3BSC; __hstc=241090844.977460cfe13e3612eabcb9873ef581ba.1759138803429.1759198441031.1759216922358.3; __hssc=241090844.1.1759216922358; _ga_ZQWF70T3FK=GS2.1.s1759216921$o4$g0$t1759216922$j59$l0$h0',
}

base_url = "https://www.businesswire.com"
filename = "./news/data/businesswire/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

# Create a session for better connection handling
session = requests.Session()
session.headers.update(headers)


def make_request_with_retry(url):
    try:
        util.info("Making request to {}".format(url))
        response = session.get(url, timeout=30, allow_redirects=True)
        if response.status_code == 200:
            return response
        else:
            util.error("Request failed status code: {}".format(response.status_code))
    except Exception as e:
        util.error("Request failed error: {}".format(str(e)))

    return None


def get_detail(link):
    util.info("link: {}".format(link))
    response = make_request_with_retry(link)
    if response and response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select("#bw-release-story")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            ad_elements = soup.select("style")
            for element in ad_elements:
                element.decompose()
        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(url):
    try:
        post_count = 0
        data = util.history_posts(filename)
        articles = data["articles"]
        links = data["links"]
        insert = False

        response = make_request_with_retry(url)
        
        if not response:
            util.error("Failed to get response from main page")
            return
            
        response.encoding = 'utf-8'
        resp = response.text
        soup = BeautifulSoup(resp, "lxml")
        nodes = soup.select("div.overflow-hidden a.font-figtree")
        
        for node in nodes:
            if post_count >= 3:
                break
            try:
                a = node
                href = str(a["href"].strip())
                if href.startswith("http"):
                    link = href
                else:
                    link = base_url + href
                title = str(a.text.strip())
                
                if link in ",".join(links):
                    util.info("Link already exists, skipping: {}".format(link))
                    continue
                if title == "":
                    util.info("Empty title, skipping")
                    continue
                post_count = post_count + 1
                # Add delay between requests to avoid rate limiting
                time.sleep(2)
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "pub_date": util.current_time_string(),
                            "link": link,
                            "source": "businesswire",
                            "kind": 1,
                            "language": "en",
                        },
                    )
                else:
                    util.info("Failed to get description for: {}".format(title))
                    
            except Exception as e:
                util.error("Error processing article: {}".format(str(e)))
                continue
                
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
            util.info("Successfully saved {} articles".format(len(articles)))
        else:
            util.info("No new articles to save")
            
    except Exception as e:
        util.error("Error in run function: {}".format(str(e)))
        traceback.print_exc()

link1 = "https://www.businesswire.com/newsroom?language=en&industry=1000178%7C1778661"
if __name__ == "__main__":
    util.execute_with_timeout(run, link1)
