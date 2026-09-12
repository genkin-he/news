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
    "referer": 'https://www.telegraph.co.uk/business/companies/',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "cookie": 'ak_bmsc=4A87F807D5D616BA243A2A22CDEF5328~000000000000000000000000000000~YAAQyJTYFzmSo2iZAQAApuPajh2Pj72sR17uRGJ2xePWkmqxNoDzEFqjBca8PgHfGPOgkZe4xoseUAeB2Un2JoyLwzevbf3YvcYk2fhi3E+4Ye070B4iBwsfGJuvehhMZc3deMcYfoyu6z9/dDGuws326xr4Cvb2z8ilHMlFpkKQsbMQ1Buh8bZWb9oTX2qqgFd44g6oB8boLqUO0XxHHwK/urnSvviKSCHh4Pbg9Kv7CfC2NjoyJ2rv5NgkA8kpvxNDv4OQ2BVYvop597NlFMjZHR0F0sTHGQBgiKk4kb5//MPiD8iBVHepUwCZT11lolGaVU4ZBQ4O8deWqYF/wk9ZJmVynLEp6mcYTSx5i6rPjr8RhotQscbD4vbFuZzcmQSV4KRI7W1T; AMCVS_2C7336C753C676BA0A490D4B%40AdobeOrg=1; s_ecid=MCMID%7C04897461127758770702447246814315217597; kndctr_2C7336C753C676BA0A490D4B_AdobeOrg_identity=CiY4MjQ3NTkwNTUxMjc1NzE5MTYwMzU3ODg3OTg5Nzc5Mzc2Nzg0M1ITCOCD7PaYMxABGAEqBFNHUDMwAPAB4IPs9pgz; dnsDisplayed=undefined; ccpaApplies=false; signedLspa=undefined; _sp_su=true; qm_mrk-funnel=0; ccpaUUID=96905a47-db36-407b-a941-10667d2d084b; consentUUID=8b17dfe4-2d75-48a7-8d03-7c5a32a0f6ad; _sharedID=66568513-1e9b-4646-aaed-fdaebb69e38f; _sharedID_cst=TyylLI8srA%3D%3D; _pcid=%7B%22browserId%22%3A%22mg3a0gnvap2mc38g%22%7D; _cb=CJfTV2BV4HQ_K8L2N; __pat=3600000; cX_P=mg3a0gnvap2mc38g; permutive-id=19869525-ecf1-4877-b730-49fcd553d265; QuantumMetricUserID=10c8eea9fe7315bd083ca2e64683bae1; _gcl_au=1.1.432400901.1759038453; g_state={"i_l":0}; tmg_pid=PNIPgs9QNt3ab0k; tmg_session=undefined; tmg_createddate=1759038789000000; tmg_refresh=eyJjdHkiOiJhcHBsaWNhdGlvbi9qc29uIiwiYWxnIjoibm9uZSJ9.eyJ0b2tlbklkIjoiZmZjNmVhZGMtNjkwNy00YTVhLWJjYWMtNGUxZTRkM2NlNDJhIiwicHJvZmlsZVB1YmxpY0lkIjoiUE5JUGdzOVFOdDNhYjBrIiwiY2xpZW50SWQiOiJ0Y3VrIiwiaWF0IjoxNzU5MDM4Nzg5fQ.; AMCV_2C7336C753C676BA0A490D4B%40AdobeOrg=-432600572%7CMCIDTS%7C20360%7CMCMID%7C04897461127758770702447246814315217597%7CMCAAMLH-1759643597%7C11%7CMCAAMB-1759643597%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1759045997s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.5.2%7CMCCIDH%7C-699413734; __tac=%7Bjax%7DEQ0vfsLVNgGvqGONkSwYsgJY27K4_34MuGqtEnpjhyy-1dZ1PZ2Q6BibvlCcz7ABJfBHd3FFcHKqndmEm7Z5rdaHISX1-ItszdTu_yqOWk4KBAbDynzBUsbbujoYMzflA2-xmA_oewZcesLKjTaKatOUX9TFgLcakR0-U7HEQuu12exWVfQqjQaiMT7YkUvC; __tae=1759038858670; _pctx=%7Bu%7DN4IgrgzgpgThIC5QAUByBJZBzCBOAiqgC4DMAhgEYAMA1oqAA4xQBmAlgB6IgcD2AXiAA0IIgE8GUbgDUAGiAC%2BCkZFgBlImSKRuACzIQAggGMibAG5QTxqBHgiIbIlHQATbgEYPAFioAOEj9cAHYSXxIqAFYAJj8qb0UgA; tmgOfferId=freetrial-digital-month-RP725; __utp=eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2lkLnBpYW5vLmlvIiwic3ViIjoiUE5JUGdzOVFOdDNhYjBrIiwiYXVkIjoiTkp1NUtuT0ZwdSIsImxvZ2luX3RpbWVzdGFtcCI6IjE3NTkwMzg5MDA1MDkiLCJlbWFpbCI6InpoYW5naG9uZy55dWFuQGxvbmdicmlkZ2UtaW5jLmNvbSIsImVtYWlsX2NvbmZpcm1hdGlvbl9yZXF1aXJlZCI6ZmFsc2UsInByZV9jb25maXJtZWRfdXNlciI6ZmFsc2UsImV4cCI6MTc2MTY2NjkwMCwiaWF0IjoxNzU5MDM4OTAwLCJqdGkiOiJUSU9UREcxcTBRdDNhYjNvIiwicGFzc3dvcmRUeXBlIjoicGFzc3dvcmRsZXNzIiwibHMiOiJJRCIsInNjIjowLCJ0c2MiOjR9.s59p-Gvri6cOJRwcBrLPaDBJ6tMp2SAMS2JXaZ5MHUY; tmg_p13n={pId:"PNIPgs9QNt3ab0k",username:"zhanghong.yuan",email:"PUlVshl0z2YBHH1asZOX0l4mJa0+LkN9/uF0fHuqAghCKTBJ9sQzEOZSMFltDVcsCst0GN3AF/dg0k32BXL6/A3XjVWjVdHTVtuCP5gws8L5Z7MKHJeLxPqC23TnmQJy",readerType:"registered",creationDateTimeInMillis:1.759038789E15,subscriber:"false",subButton:"false",expire:1.853646901524E12}; DtmSubIcid=; bm_ss=ab8e18ef4e; s_vis_repeat=1759039766867-Existing; kndctr_2C7336C753C676BA0A490D4B_AdobeOrg_cluster=sgp3; affinity="b7ab21e7b6f921c4"; qm_lastarticle=/money/banking/savings-accounts/the-magic-number-of-bank-accounts-you-need-to-get-richer/; artTags=companies,business; _topp=1759044765304; _chartbeat2=.1759038344054.1759044765906.1.BkPgNqCWPY2hDlW1ovWpXQaCWGT9f.1; _cb_svref=external; __gads=ID=89f8ee9f14a7db89:T=1759038344:RT=1759044767:S=ALNI_MY7NDHturz-9G16SkiEvcHybtXpmg; __gpi=UID=0000119bc662b2ef:T=1759038344:RT=1759044767:S=ALNI_MaLPvxWuG_JKwiqRD4L-dguS7qSiQ; __eoi=ID=b3c4837244b8728c:T=1759038344:RT=1759044767:S=AA-AfjZhrsgvSJTpBXsTal28QEo_; __pvi=eyJpZCI6InYtbWczZHU1NG85dzF3ajRjYSIsImRvbWFpbiI6Ii50ZWxlZ3JhcGguY28udWsiLCJ0aW1lIjoxNzU5MDQ0NzY3MzUyfQ%3D%3D; __tbc=%7Bkpex%7DLPypE3e2n4Z7Wy0WidbDeuLgmer95sRjSJFL5D2kLKO9UQREXgO4i9b1WfRDfJTv; xbc=%7Bkpex%7D2Km64qfll7PveJVXv3W_mAU1eTIN85nV-HQszmzOdxVKssODkGopbwnjyWydp-VG; _pcus=eyJ1c2VyU2VnbWVudHMiOnsiQ09NUE9TRVIxWCI6eyJzZWdtZW50cyI6WyJMVHJldHVybjowZTJlNzBlODMyYzUyNDRlZmE1NGNiYjIzZWM1ODVkYzJiNDcwYmMyOjAiLCJMVHM6NDgwMDU5YTI2MzcyMGY0ZDY4ZDAzNjZhY2Q5ODEwNzU3YzkwYjM4MDo0IiwiQ1Njb3JlOjkxZTJjODM3NjhlNTU1NmJiYzA3ZTQ1ODA0OGMzYzhlMjk3ZmViNDM6bm9fc2NvcmUiXX19fQ%3D%3D; cto_bundle=ql5lq191Y2lOVGtjMGIwQkYlMkJweTFQbThKQjhQdWlyRVJDY2hueHR6Uzk0MnVubWp1WW5UQUg4MnloZmNqTU9RSFlkbDVBSGNUNVhUdUYxa1p6Q2oxanBXaVpQVlZxdldNZWxiY1loNjNHN093RVRYSW5Jc05FaDZkSlY0N3ZVRHBXOWQlMkZTNHU3c3pPS3c3MER6NVAwVUhWWWFnJTNEJTNE; cto_bidid=WWuHUl9WY3Q2ZmdhWlBzWVdwTHFzUHlnSUZYSGNkSk5qbmVvQldpM1JySkx2ZE1oekt5bzdJS1JuNlgzWGNldEp0azJkUnlVNjZuM0xiYzJNZ0NUUFBvT2pZOGpNbFNXdGYzM2Zzd0wydFZiNFFrJTJCJTJCVUhBS1RXZDVYUTBwSGdncmZIQXU; propensityData=4+0++no_score; bm_lso=FCECF065D76D16551F1203BE0534053BAEBA49810DECC54B65E7CF5B116E96EB~YAAQxUJ1aFtI3kGZAQAA0gA9jwU9RY2x4gBDZ5T7lNxFqDHPANY+zYpFDMOubsjEWtS2+YsAZ/7eaW58RVIWtPYWqJWqCTcSLiocAqZErKoZo8mEqy6DsnZzqyl8VUyzvIjFZS9JXUAry6TQFOSuSlifb6rJwe1A9jhjg5/5Ar3Q3ohzYD6f+ZnM+0UEtXOlaf3yyuUX1W04P5kCiA7fhk0JBbDagPCAt3O95e8iCEMzKUigxH0hmvwYdFKkvrjC/x1BnuxjiTfTGlz2X2jp/QyK6IDDdArzCaONggYOW7Bfgxwlt3zQP9yohd0NzRm5x2hD1J2XHri1WFZ+KrClnFM50wrp4wJ3PHTyTeXg94TYk6dVP2zjZyyRHL27mK1PS64KzyNptT16cqlr2hd1BHIQKNjFGudDAdbs36ZgIjzamjIuk8wNFePGSOmSwkk7lkEYwdK+ImUzTCVsBd6x0cjy6VqG^1759044770002; bm_s=YAAQf/BuaHhqNHuZAQAANY0/jwTMQxfFpDmeAQ5Poo6XFHqaD+oIc0zsqn7+Kbfc90Uo89YIzOacu6fSjospaz3E+hvSic3SfJmNJ4QRj6/AhG9KmsTWXE5WxU+9RST7WzyqYY34KKJE1kjXcxWJCqolUPyJ/5kImztOMMhrhS2WQgubM7ilLL/Yn3lhEPTYn/NhVfKZidhM+gZAFO2npS7z9Jrv3FI1H4qIBmbEmtlrseryup0KelV8vwFlieZXXDT7lGY3ie2JyIffAb4dXf+mEXtNLuC0jpPLf4IiV+6gobiDttm5ZGrvW3Jr9B7Bb5+oONTM3V/yMhXZmdT2sFvv3xSkbX604QTnRX/Gz+rSopkuA2NyfLDqkBZVG5eL0GypSfWXqO26L50/S6RzIqzsb3v9ynLJPnndzKjFq/gfC0RhFQtsxDnzwimoXHhWvD2wOsHsywtjhHKE67/8rv/L9rsdmkHZwTOSwen4bcRBNZFDjRoMJCfPsWvFkLboLnym4VmSbEDsdJxmnA+n44H2wuIckAtV+Y0WfY/Bw6TnrxmG4eVGBdenKnNJTif64Y3APN5Gk07oidUOoQ==; bm_so=9CDE696AE6C593AEDB292D0A7C3885CC19F38BA67D8FC9482300598D107586DE~YAAQf/BuaHlqNHuZAQAANY0/jwXlvdIymB7mc9DVn6FMIRSx8AeOvdiXMzJyJBCy3Hrg5Dxgo4nnoPz2M7tBZEK3m1HFdYS7vFB4ldVBhxOZGs7Vu8kxdjmoFk2tQJEpjrttO4zEihqKxyoKMAbpfytFdAS/IBMI8A1MUO+va2csKvdBWfgd0h6kiSHSOwOvmJlvoeEi1QblD43bHK7DrS427LBt5IJR+U0ffDyeb5gS15VUEKHb8i8YWKkji30yU4VQmuKc12J+PcFYGEyKOSfXM4WFQmnM1z5l6zc/dANn6BM2XN0V+U48RhIgzikpX/9U/iNy+VSEAczaifSgzSblhYCuic2gbvNlAclx+va78UB0IMawudhn9uay14bZIrUv/3PgCqpdW+rzyQimcnu7YWG/7EVaffTu03us3ob2bREXcaDOErvCYDHFPtmvneZ89eYG3f1GmVR36iYJsiBJJgCV; bm_sv=8BEF05C9028BBCC03C81E2AEA029B354~YAAQf/BuaHpqNHuZAQAANY0/jx2w2NDj4pbEn913He4QLgwtmpZnhXo0sZBJVN3ls/TIqVCqv0wnD6wona/MI4r1SSys+Z7HN3LE6BiEJ3Jx/5q4cu/96teoJmztBiPbeMZyflTha6sY7vTsmKydCN/7cMakd0cUd9oB03Njge0oWrS5H5AY6bDAhBG6apAf7UgrgUZ+cGs5CHrsQNp/g9yJ6nlUsiLfAV2Az27cIXzQtiWmmBBdZkPoPS3h5yRWQ/3+1S5PJA==~1; QuantumMetricSessionID=3653880ef56ad158f935cd061b568163'
}

base_url = "https://www.telegraph.co.uk"
filename = "./news/data/telegraph/list.json"
current_links = []
util = SpiderUtil()

def get_detail(link):
    util.info("link: {}".format(link))
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        resp = response.text
        if "Access Restricted" in resp:
            raise Exception("Connection reset by peer") 
        body = BeautifulSoup(resp, "lxml")
        content_wrappers = body.select(".tpl-article__layout--content")
        if len(content_wrappers) == 0:
            return ""
        else:
            soup = content_wrappers[0]
            ad_elements = soup.select("figure, .tpl-layout__mobile, .tpl-layout__mobile-comment, .teaser, .html-embed, #advert_tmg_nat_story_top, .advert-container, .u-separator-top--loose")
            for element in ad_elements:
                element.decompose()
        result = str(soup)
        result = result.replace('\n', '').replace('\r', '')
        return result
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""

def run(url):
    post_count = 0
    current_links = []
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        body = response.text
        soup = BeautifulSoup(body, "lxml")
        nodes = soup.select("h2.list-headline a")
        util.info("nodes: {}".format(len(nodes)))
        for node in nodes:
            if post_count >= 3:
                break
            link = base_url + str(node["href"])
            title = str(node.text)
            title = title.replace('\n', '')
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            description = ""
            try:
                description = get_detail(link)
            except Exception as e:
                util.error("request: {} error: {}".format(link, str(e)))
                if "Access Restricted" in str(e):
                    break
            if description != "":
                post_count = post_count + 1
                insert = True
                articles.insert(
                    0,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "author": "The telegraph",
                        "pub_date": util.current_time_string(),
                        "source": "The telegraph",
                        "kind": 1,
                        "language": "en",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 60:
                articles = articles[:60]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run, "https://www.telegraph.co.uk/business/companies/")
    # description = get_detail("https://www.telegraph.co.uk/business/2025/09/27/jaguar-land-rover-rescued-15bn-loan/")
    # util.info("description: {}".format(description))
