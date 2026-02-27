# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Domain-Id": "www",
    "Cookie": "__cf_bm=mznqRk.pFE0omrep8BTChfAu1O2BhJVjeNSKipJaxDw-1730282371-1.0.1.1-qLZgyWnoN6a_A2Ax5woyrNDmailf_TNla2OKZRlueeTYnIFELZuJ3IWeS1enHVmNJS77X2xixF_DqlaGaREXxyTlPLb1Kd.Yb1ATGzeAVms; gcc=HK; gsc=; udid=3e8e3eb81c24e42f3c24eea74668ea9b; smd=3e8e3eb81c24e42f3c24eea74668ea9b-1730282396; invab=popup_3; invpc=1; page_view_count=1; adBlockerNewUserDomains=1730282398; lifetime_page_view_count=1; cf_clearance=AG5H_4WOIJTlegKVtNT6DiLvJtiP16iOb.sY7.AzzuE-1730282399-1.2.1.1-ekSgBMNSJmUwv8oqzzHzXv79qtZLzzdVQ9NvGeq_.nVfSYgTTMXH3OJ9uR3IJhJwM0py.BRFMAnQMTRvg72GDEFRp7oCDUlZOAlGqjJDjSVNqpF4GlFHbC6iRfVh9pyf5KJ9hpnTf.il3JBlbjRYY9OITdPSdZBzUDnaYC4vA5MGkoLQFUNSoYmyyfrtmla3g4GqVDoj__6Km2VlHPOdVZfk_M9J312tpt5x7VV2opJuW8DODsWTAp_omL47rGpP5WxpPD3rRjtN2OCTEjxgLNpyADzBkInRhQ7JQbxCqKcR6YNGj7V.tLfQ7yaDfGMXNTZZ0_HwI2sEp7hJPkPlk2z74bKGfCh7cRIi9KX_dvNDSxgAO7UPCdEv9lYxss5Zl_vD9gtSJDt.fCijWWYe4g; __eventn_id=3e8e3eb81c24e42f3c24eea74668ea9b; _hjSessionUser_174945=eyJpZCI6IjViNzhkMDk1LTI0YWItNTM2MS1iMDdmLWE5N2YzZDNjOGFjNiIsImNyZWF0ZWQiOjE3MzAyODIzOTkyMzAsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_174945=eyJpZCI6IjVjMWQzYjQ4LTMwZWMtNGY2ZS04ZmFjLTI3OGQ3NWExYTA4NyIsImMiOjE3MzAyODIzOTkyMzIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; _ga=GA1.1.647139595.1730282400; _cc_id=9ad194eabf8e6b31261ef86026d37476; panoramaId_expiry=1730368800242; _au_1d=AU1D-0100-001730282401-6B98ERP9-ZHPL; reg_trk_ep=on%20mouse%20exit%20sign%20up; cto_bundle=mDsmml9jUjNueUtodkFHdUpXRGVzMlNQek9rbjRPJTJCV3h3dVpvd0NPSlFNZ2J1NnFkOTQlMkZCaXAwbEpReUJtelM3MXh4UFRIWlhPVWdaR0ZUVTZNQjkwZTlBcXhTSHdJWmJ1VWJYcGI0VUF0YUNJTXBDemRna3U0eCUyRk9RMXV2WUNLejRRQlJWWXZXRW1zSUtCbkplUXpOOSUyRkhPdVc4ZnI4Vkd1Y2xxNVVzMjh2eU9pWSUzRA; _ga_C4NDLGKVMK=GS1.1.1730282400.1.0.1730282413.47.0.0; firstUdid=0; _ga_FVWZ0RM4DH=GS1.1.1730282414.1.0.1730282414.60.0.0",
}
base_url = "https://www.investing.com"
filename = "./news/data/investing/list_us.json"
util = SpiderUtil()

def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request 中放入参数，请求头信息
    request = urllib.request.Request(
        "https://api.investing.com/api/news/homepage/21/5?is-ad-free-user=false&is-pro-user=false&max-pro-news-updated-hours=12",
        None,
        headers,
    )

    # urlopen 打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["items"]

        for index in range(len(posts)):
            if index < 10:
                post = posts[index]
                link = base_url + post["href"]
                title = post["headline"]
                id = post["id"]
                if link in ",".join(links):
                    util.info("exists link: {}".format(link))
                    break

                description = post["body"]
                pub_date = util.current_time_string()
                if post["updated_date"]:
                    pub_date = util.parse_time(post["updated_date"], "%Y-%m-%dT%H:%M:%SZ")
                if description != "":
                    description = f"<div>{description.replace('\n', '<br>')}</div>"
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "investing_us",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 4:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))

if __name__ == "__main__":
    util.execute_with_timeout(run)
