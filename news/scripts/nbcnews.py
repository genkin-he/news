# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'same-origin',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'ng_geolocation=HK; _gcl_au=1.1.535178749.1757672852; adops_master_kvs=; s_ecid=MCMID%7C35310310527697692179079898772245637622; AMCVS_A8AB776A5245B4220A490D44%40AdobeOrg=1; AMCVS_A8AB776A5245B4220A490D44%40AdobeOrg=1; AMCV_A8AB776A5245B4220A490D44%40AdobeOrg=1585540135%7CMCIDTS%7C20344%7CMCMID%7C84972380610642747566866691849751959321%7CMCAID%7CNONE%7CMCOPTOUT-1757680057s%7CNONE%7CvVersion%7C4.4.0; s_cc=true; usprivacy=1---; iter_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhaWQiOiI2OGMzZjVhZWZmOTQ4M2VhMmU1MWU4MTQiLCJjb21wYW55X2lkIjoiNjA5YzE5ZmFmOWUyYzgwMDAxYzU2NTFjIiwiaWF0IjoxNzU3NjcyODc4fQ.wZJK2ZwKQjRfP2HGvvZ5DhTDyPliDZ5p8kq68ad7BLc; OneTrustWPCCPAGoogleOptOut=false; ak_bmsc=6DF6C0C84D1CA63CE147B0DCCFBDDD8D~000000000000000000000000000000~YAAQDfAgFxcEzUuZAQAAYneGTB0IxBC7SZdziaN5kHzuaj6UWpfoNy/50LU8D/M9VG9ZdC0WyoY8b8LUcHEd14nW0dvWIPVYGJHG2geQiouDLqEvh9hjFaT5+9snnHbd3LZHlo0jMXIeLC1Auvvgo0JUSMT3lPtJO3i01IL6gH/Ytd26JTLU3e34xNZFfDKcHbZ4i0PeH+VXnlXELcgaKknzIFy2bnBFAXiC8GuA+9SCvP8bJ1lWQFqgsUqFPemR87D/zcS5xGeJRbYSuBs9dI05O31dDOXccBx6+BHaZXnHwqfgXF/Yk27MVz8DHsewuxE8HJHBw/c6+YpLzCh3zqrjPscRQ02B7F1CVfIpF94vWKLMkMhOBv8RpSLg85BGIuMEKwi2UvKj9fUGAD36ztUc/8h67onZ2BB4tZuzmJnJvSXuwkAi+oGzVBg7fApxIbiWx0w=; BI_UI_previousPage=direct; BI_UI_referrer=direct; _parsely_session={%22sid%22:3%2C%22surl%22:%22https://www.nbcnews.com/news/us-news/man-prison-sexually-exploiting-minor-girls-discord-rcna231134%22%2C%22sref%22:%22%22%2C%22sts%22:1757930106574%2C%22slts%22:1757925504263}; _parsely_visitor={%22id%22:%22pid=92df9da5-08b2-4fc9-8b70-dc76faf29154%22%2C%22session_count%22:3%2C%22last_session_ts%22:1757930106574}; _dpm_ses.1b16=*; _dpm_id.1b16=57217fdc-d4f6-4acf-a58c-573d041b1d2c.1757672858.3.1757930107.1757927651.e639e880-c39f-4767-96bb-e83580e797e1; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Sep+15+2025+17%3A55%3A06+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202309.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=60ffe136-85ef-4027-9606-a9bd5c769d6b&interactionCount=1&landingPath=NotLandingPage&groups=1%3A1%2C4%3A1%2C9%3A1%2C12%3A1%2C11%3A1%2C13%3A1%2COOF%3A1%2CUSP%3A1&AwaitingReconsent=false&geolocation=HK%3B; OptanonAlertBoxClosed=2025-09-15T09:55:06.653Z; prevVal_pn=nbcnews%3Apost%3Aman-prison-sexually-exploiting-minor-girls-discord-rcna231134; s_vnum=1760264857466%26vn%3D3; s_invisit=true; sailthru_pageviews=1; _awl=2.1757930109.5-6082ba9617038068c584d104962152a8-6763652d617369612d6561737431-0; sailthru_content=c74d9a1aaf8c112e26381d5a6988a355f6245954b2b4c8e6a0a0686f5c6bae125e513a798f1274f0afd75f24c24d8f5bd317f82710f6ec053111a9842464bd4327ed7d8819c22a93dfdc7e5522631a50090cbf0b3444b7839a2fdccc137417ca36e02e49042ae10ed86e05650c438a3be4410867d4b7284499b2b44bc1d2d8dc; sailthru_visitor=8a0faf8e-818f-416f-8f5e-a632d7e3bb60; akaas_NBCNews=1758794118~rv=94~id=788f4ace030b8bb3a95f773702d02c1a~rn=; bm_sv=071B49098A1792F46FF857CD69B7B413~YAAQDfAgF7Vz0kuZAQAAD97MTB0L0S14XFtWqp1RM5LssH9Sui7x1LhqgkrvJyAJASDVWHXPCSmasajM0ud6VltcAlnLMNI6xsuDHysDm2zfAAZ7ljOxMTVstKF78z2i9Ccjdq4tHgvgly//yhzLXqtEPdwywAgiOjmmWx6SiMrODBuzRgeBHMUmoQLWUXsenLhdFcGZ2Bi8FRGaH7pnM04oJsbK7SGtwOSPleSRqyIoowVVZ4A75gXffrUk8mdVyrU=~1; s_sq=msnbcnbcnewscomprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dnbcnews%25253Apost%25253Aman-prison-sexually-exploiting-minor-girls-discord-rcna231134%2526link%253DThe%252520case%252520was%252520initially%252520investigated%252520by%252520the%252520D.C.%252520Metropolitan%252520Police%252520Department%252520through%252520its%252520work%252520on%252520a%252520joint%252520task%252520force%252520with%252520the%252520F%2526region%253Darticle-content%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dnbcnews%25253Apost%25253Aman-prison-sexually-exploiting-minor-girls-discord-rcna231134%2526pidt%253D1%2526oid%253Dfunctionrh%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DP; AMCV_A8AB776A5245B4220A490D44%40AdobeOrg=1585540135%7CMCIDTS%7C20347%7CMCMID%7C84972380610642747566866691849751959321%7CMCAID%7CNONE%7CMCOPTOUT-1757937500s%7CNONE%7CvVersion%7C4.4.0; _dd_s=rum=0&expire=1757931546514',
}

base_url = "https://www.nbcnews.com"
base_filename = "./news/data/nbcnews/{}.json"
util = SpiderUtil()


def get_detail(link):
    util.info("news: " + link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split('<script type="application/ld+json" data-next-head="">')[1]
        .split('</script>')[0]
    )

    data = json.loads(body)["articleBody"]
    if data == "":
        return ""
    html = "<div>" + data
    return html + "</div>"


def run(url, filename):
    # 读取保存的文件
    file_path = base_filename.format(filename)
    data = util.history_posts(file_path)
    articles = data["articles"]
    urls = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(
        url,
        None,
        headers,
    )
    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = (
                response.read()
                .decode("utf-8")
                .split('<script id="__NEXT_DATA__" type="application/json">')[1]
                .split("</script>")[0]
        )
        datas =json.loads(body)
        items1 = datas["props"]["initialState"]["front"]["curation"]["layouts"][0]["packages"][1]["items"]
        items2 = datas["props"]["initialState"]["front"]["curation"]["layouts"][0]["packages"][2]["items"]
        posts = items1 + items2
        for index in range(len(posts)):
            if index > 2:
                break
            post = posts[index]
            title = post["computedValues"]["headline"]
            link = post["computedValues"]["url"]
            if link in ",".join(urls):
                util.info("exists link: " + link)
                continue

            description = get_detail(link)
            if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": util.current_time_string(),
                            "source": "nbcnews",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, file_path)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.nbcnews.com/tech-media", "tech_media")
    util.execute_with_timeout(run, "https://www.nbcnews.com/business/consumer", "business_consumer")
