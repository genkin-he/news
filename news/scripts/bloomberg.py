# -*- coding: UTF-8 -*-

import logging
import urllib.request  # 发送请求
import json
import re
from util.util import history_posts

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Cookie": 'optimizelyEndUserId=oeu1719368342267r0.5409643801242132; bbgconsentstring=req1fun1pad1; bdfpc=004.8551514038.1719368343123; _gcl_au=1.1.1066353835.1719368343; agent_id=839dea2f-ec3a-490d-8a7d-0078131fd452; session_id=59d85f23-0ec6-4695-853e-c31b292bd77e; _session_id_backup=59d85f23-0ec6-4695-853e-c31b292bd77e; session_key=3d1f84e12bed4b26df76ebba91fd0a874040cd14; gatehouse_id=15f4b7a6-aa03-4931-861f-38291814092b; geo_info=%7B%22countryCode%22%3A%22HK%22%2C%22country%22%3A%22HK%22%2C%22field_n%22%3A%22cp%22%2C%22trackingRegion%22%3A%22Asia%22%2C%22cacheExpiredTime%22%3A1719973143143%2C%22region%22%3A%22Asia%22%2C%22fieldN%22%3A%22cp%22%7D%7C1719973143143; consentUUID=2432c828-fb05-4fbe-b79b-2f4b3ce62ea4; pxcts=751e9372-3362-11ef-9f15-7b0825140bd8; _pxvid=751e81d6-3362-11ef-9f15-6207a5d97dfe; _ga=GA1.1.1344463728.1719368344; usnatUUID=6554c8d4-3252-42ab-992d-1bd04a17d1a9; _reg-csrf=s%3A7EPWbfyEhZ7j7qW5P85jU4wb.XjNUjzvsGjF86MhZ3HzmwIgYEi8j%2FofaadTika7zbXI; exp_pref=APAC; country_code=HK; seen_uk=1; _clck=13gp4nu%7C2%7Cfmy%7C0%7C1638; _gcl_aw=GCL.1719368357.EAIaIQobChMI85bgl5r4hgMVAlQPAh2WPAruEAAYASAAEgIeMPD_BwE; _gcl_dc=GCL.1719368357.EAIaIQobChMI85bgl5r4hgMVAlQPAh2WPAruEAAYASAAEgIeMPD_BwE; _gcl_gs=2.1.k1$i1719368356; _scid=e3e9ed24-1963-4f2b-93f0-a089b831b4f4; _sctr=1%7C1719331200000; AMP_MKTG_4c214fdb8b=JTdCJTdE; __stripe_mid=e8ba704e-b610-4fcb-86f1-076ebe9124e464337c; __stripe_sid=cf3e2f23-5310-4a9b-9ebd-fd7a57fa8dfa5e052c; _scid_r=e3e9ed24-1963-4f2b-93f0-a089b831b4f4; _pxff_tm=1; g_state={"i_l":0}; _breg-uid=A4A08DB9444B418F866D5C7F8AB56382; _breg-user=%7B%22email%22%3A%22hemengzhi88%40gmail.com%22%2C%22firstName%22%3A%22genkin%22%2C%22lastName%22%3A%22he%22%2C%22createTimestamp%22%3A%222024-06-26T04%3A00%3A31%22%7D; _user-data=%7B%22userRole%22%3A%22Consumer%22%2C%22linkedAccounts%22%3A%22%22%2C%22status%22%3A%22logged_in%22%2C%22subscriberData%22%3A%7B%22subscriber%22%3Afalse%7D%7D; _user-role=Consumer; _last-refresh=2024-6-26%204%3A1; __gads=ID=cef820c0dea4ca20:T=1719368392:RT=1719374491:S=ALNI_MY3gsdtBzajv8jPv0F6_ARExnl2tQ; __gpi=UID=00000e64742456ae:T=1719368392:RT=1719374491:S=ALNI_Mb3km0pGGK270iFGecA1GSTk8mc0w; __eoi=ID=a9bf8e6723530616:T=1719368392:RT=1719374491:S=AA-Afjb8blBkgYeoUgqD3NKBoAhQ; _uetsid=74f92be0336211ef90cf63693e236251; _uetvid=74f93800336211ef818105752ca5f0a3; _rdt_uuid=1719368343488.a4100c42-c8f6-42d3-9559-b3fa17963bba; _clsk=9upwll%7C1719374499683%7C4%7C0%7Cu.clarity.ms%2Fcollect; panoramaId_expiry=1719460899819; _px3=6b26d7a0642cca407d77c28d43d858accafdcb6d7d855fc45e61be85820babd1:UqSAQis6kEwKZails0M2yc3a9wg3AnyyPnEF4sw+Ef1TKEJ5i3wqXZz4GPb1ZKgZPtcz2udjfZDfpY3Z+vHycQ==:1000:lGcJ5nrqaDyXTdvZ9EKN7nHxoPdi8tLRk7xOxcwVh5TU+Z6XcbAja6P4k3QMKKzH/Ox5vVcoOPQZkBN7DEYlEZuD6kz0hBgWbd2GhLCvo+jmhVbtu8bJ5633ObqfyhNgWtC77S52QvVcLZSo5NzP/o5IqnhZdnyEjVAW50OwcEY05hWwYvRG7PaRZJ9yYioE6vEO6G5g8vjaQXkZ/3I+D6JyYrglo1WYo6odgUFsr0E=; _px2=eyJ1IjoiYzlhNTkzNDAtMzM3MC0xMWVmLTk2ZjMtNzM2ZGJlNmU3NTQ5IiwidiI6Ijc1MWU4MWQ2LTMzNjItMTFlZi05ZjE1LTYyMDdhNWQ5N2RmZSIsInQiOjE3MTkzNzQ3OTk5NTUsImgiOiI1ZWEyYmYzYTEzYWQ4M2UxNDZlZWEwZjc5ZTNhZGJlMGNiN2I2NDY0MDlmZmRiODM1YTc4NWY0YjdiM2Q3MGQzIn0=; _ga_GQ1PBLXZCT=GS1.1.1719373614.2.1.1719374502.0.0.0; AMP_4c214fdb8b=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjIxZmI5MGUwZi1lZWM4LTRkODktYWExMC0wNGVmOWYyYTdkOWUlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjJBNEEwOERCOTQ0NEI0MThGODY2RDVDN0Y4QUI1NjM4MiUyMiUyQyUyMnNlc3Npb25JZCUyMiUzQTE3MTkzNzM2MTQzODglMkMlMjJvcHRPdXQlMjIlM0FmYWxzZSUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNzE5Mzc0NTAyMTc2JTJDJTIybGFzdEV2ZW50SWQlMjIlM0E1MyUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBNCU3RA==; _pxde=b0936640331ff5230a186c148e033b60791f4044e6c99624e8cf786921759a28:eyJ0aW1lc3RhbXAiOjE3MTkzNzQ1MDI3OTAsImZfa2IiOjAsImlwY19pZCI6W119; _reg-csrf-token=WaVvzSaT-xRIwqTgnMtZPVrSRN496YyHWwAk',
}

base_url = "https://www.bloomberg.com"
filename = "./news/data/bloomberg/list.json"


def get_detail(link):
    print("bloomberg news: ", link)
    request = urllib.request.Request(link, None, headers)
    response = urllib.request.urlopen(request)
    body = (
        response.read()
        .decode("utf-8")
        .split('<script id="__NEXT_DATA__" type="application/json">')[1]
        .split("</script></body></html>")[0]
    )
    elements = json.loads(body)["props"]["pageProps"]
    if "story" not in elements:
        return ""
    elements = elements["story"]["body"]["content"]
    html = "<div>"
    for element in elements:
        paragraph = ""
        text_count = 0
        if element["type"] == "paragraph":
            for sentence in element["content"]:
                if sentence["type"] == "text" and (
                    sentence["value"].startswith("Read more")
                    or sentence["value"].startswith("Read More")
                    or sentence["value"].startswith("More From ")
                    or "Want more Bloomberg" in sentence["value"]
                    or "You can follow Bloomberg" in sentence["value"]
                ):
                    break
                elif sentence["type"] == "text" and sentence["value"].lstrip() != "":
                    paragraph = paragraph + sentence["value"]
                    text_count = text_count + 1
                elif sentence["type"] == "link":
                    for ele in sentence["content"]:
                        if ele["type"] == "text" and ele["value"].lstrip() != "":
                            paragraph = paragraph + ele["value"]
                elif sentence["type"] == "entity" and sentence["subType"] == "security":
                  for ele in sentence["content"]:
                        if ele["type"] == "text" and ele["value"].lstrip() != "":
                            text_count = text_count + 1
                            paragraph = paragraph + ele["value"]
                elif sentence["type"] == "br":
                    paragraph = paragraph + "<br />"
        if paragraph.lstrip() != "" and text_count > 0:
            html = html + "<p>" + paragraph + "</p>"
    return html + "</div>"


def run():
    # 读取保存的文件
    data = history_posts(filename)
    articles = data["articles"]
    urls = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request("https://www.bloomberg.com/lineup-next/api/paginate?id=archive_story_list&page=phx-markets&variation=archive&type=lineup_content", None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        items = json.loads(body)["archive_story_list"]["items"]
        posts = []
        for index in range(len(items)):
            link = base_url + items[index]["url"]
            if "/news/articles/" in link:
                posts.append({"title": items[index]["headline"], "link": link})

        for index in range(len(posts)):
            if index < 3:
                link = posts[index]["link"]
                if link in ",".join(urls):
                    print("bloomberg exists link: ", link)
                    break

                title = posts[index]["title"]
                description = get_detail(link)
                if description != "":
                    insert = True
                    articles.insert(
                        0, {"title": title, "description": description, "link": link}
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("bloomberg request error: ", response)


try:
    run()
except Exception as e:
    print("bloomberg exec error: ", repr(e))
    logging.exception(e)
