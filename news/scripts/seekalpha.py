# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
from util.util import history_posts, parse_time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Cookie": 'machine_cookie=3978862239667; session_id=243c3fbe-a69d-4a2d-9bd8-b7e39281a3f6; _sasource=; _gcl_au=1.1.1283166948.1722996096; _ga=GA1.1.457798332.1722996097; _pcid=%7B%22browserId%22%3A%22lzj7e159e8cutjf8%22%7D; __pat=-14400000; pxcts=fb668a7e-5460-11ef-80cc-68ecde033fbf; _pxvid=fb667b72-5460-11ef-80cc-44e358429ce6; __hstc=234155329.4d0ed87af960a706ca6875d6110f5cc1.1722996099076.1722996099076.1722996099076.1; hubspotutk=4d0ed87af960a706ca6875d6110f5cc1; __hssrc=1; user_id=60486164; user_nick=; user_devices=; user_cookie_key=1tk59i3; u_voc=; sapu=101; user_remember_token=1f8873d77024a27f47ce38241145e05304e82a08; gk_user_access=1**1722996485; gk_user_access_sign=56e0db6bad2b9cbdadbae6b1f911bfe9b8568cd5; _sapi_session_id=cVMaIbmQWrv6isHEDZBDIc2Kh7C7%2FOe3kt0PWlHUlbo8vLr%2BDXv7I3WV7bG%2BM66O8FckpmLxZy%2B5Hhz2XojIgQfIty7oHcD%2FPceNOcEba1%2FOOSGuBWndaKuimOzQcaUI8lNvlgRr73XU%2FgNl5B6bMabeszueEYQ%2BDrT1EdZitlxasEOy4jv1bxJ22ApZsqG9Ue0mePer3piCpTEk95BgB8e02yquvuvDgy%2Fmq0blbRFlNeymLkSEFIty9iOK1%2FWv1yATLzzzg16SZCgaedBLyrKwmYG4nL9PoJRH7z5IbTdeVFZEoEBRvViVqYZZkLFG03rYwFCKO9FIfALB7Xq%2BACRfWoOIt0TtYMIglLbv9dvjwXRLGZE8WNynud1LAkzn49mapcORWXA%3D--dfLbNjwk9HNCAwCn--iOv4124FRMDMQjyWCjiczg%3D%3D; _pctx=%7Bu%7DN4IgrgzgpgThIC5QDYAMAWAHMgjM9ioADjFAGYCWAHoiCADQgAuAnkVLQGoAaIAvn0aRYAZSYBDJpFqkA5hQhNYUACYMQECkoCSahADswAGyN8gA; sailthru_hid=cd04a3350e81d2bd1ad549ac3030dce6665eab798920a91be60c7865e832e32deb6379925c9adcf901df80d3; __tae=1722997357725; __pvi=eyJpZCI6InYtMjAyNC0wOC0wNy0xMS0wMC0xMy0wMDEtTzRvY1pyZkhURHhQbGFUQi02YWVjNzY5NTNlYmQyMTBjYmJhZGNkZTVmOGU4ZDAyNiIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTcyMzAwMDQ2MTQ1N30%3D; _ig=60486164; sailthru_pageviews=30; sailthru_content=8e3fc505c79708c2af58fd764d5aeac19e32a6735f36b7454f5b8ac011f3fb4db6f09daf178879a54eed98528b6242aa669279a16509382ee19c0390d8f1213399d4ee9c59caa19844d9b474633e63b1b9849d18e7328aca7fe3e473f77f986b4f483ca447a6a56203c7a53e04022f884d11cd1a55e93afd6c3b23ad7b6a7c1a3c5f57e561d9315a8a9a86be8720511ed7c984bf2d33c5852dd2c81ee58d45acdc0bda7241724a24a91a0933c1941d81; sailthru_visitor=cc9a483d-4ed1-4caf-878d-2538ae0da809; __hssc=234155329.30.1722996099076; __tbc=%7Bkpex%7DS_Np1QdfRcQZmYJlYBExSmfawkheYS0TmZ3XsdZPGSzWrnT8_3kyf_rpvNSotnem; xbc=%7Bkpex%7DfMTQBeN6Cuo_-IU3OKGRf_nSp69gvqSXT6vBBf3xZqr7W5KNXQiQMi3AGsp3Vv05EL_Kaj5KkgEohXzFRT1Hg-SoNJflzx__uf7GT6jQeHBXKUKbiSYLqkgylZu7i_BwDu1z7CdUxYdTsdIV2kuA5Zo9Sde1wBBN4-Gp7RYuDvdUa_18sA1B0B_nr-Vh8CKscvmpcM2UGOwMay1owAyOapkJ7Hb6e5Vhedjk1y0ZO41uKfwWwwgvJaJ3Aa2doPhl; _px3=944e3155e8ac625a498fd408bfebc12d568ee6c2e2e35d97283adfa6c54dcc95:S1nn5tFe1nAA8pfj7lPr2dO81fcF9vwjxtF/qWzf9n0SF4I0bHgokQj4D1/PXYuXRXZ26zZ5SqHA53S+6IeRZw==:1000:uTh6HFrwvA/aQN6YEY86q9FmE/xmLJT6ouRR11fcq3N/QKXIOqqVeU32Vo9afl8jAcoThaERJmYLyUiIkMPFOrXO71QJH7S2OnNubzHd/rBgY1yK1h0k6m5wUCAN8o2G2ZrDGad0oCaGY4izRwchhv/nxZviPbUukrcEaVVrb0kLau+CX8u5RPsYC9oHlwtl1IGgRHsCvWTLN2JI/oBuj/dmwAJ8Shikt+yjdQiYwdE=; _pxde=a56213d65455d996df4a29a45e09d3d427acb9815f7cd2fd953065cb5f821599:eyJ0aW1lc3RhbXAiOjE3MjMwMDA4MjYxOTMsImZfa2IiOjB9; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fnews%2F4135600-emergent-biosolutions-plunges-37-q2-eps-miss-wider-projected-2024-net-loss%22%2C%22pageKey%22%3A%22f0671235-623a-4bc1-a02f-34acdcf5d9bc%22%7D; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A3978862239667%2C%22machineCookieSessionId%22%3A%223978862239667%261722996093818%22%2C%22sessionStart%22%3A1722996093818%2C%22sessionEnd%22%3A1723002963726%2C%22firstSessionPageKey%22%3A%2217c5e2ad-8ac4-41f9-af63-abc3ce2d0203%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1723001163726%7D%7D; _ga_KGRFF2R2C5=GS1.1.1722996096.1.1.1723001168.60.0.0',
}
base_url = "https://seekingalpha.com/"
filename = "./news/data/seekalpha/list.json"

def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False
    
    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/news?filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&isMounting=true&page[size]=5&page[number]=1", None, headers
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 3:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = post["links"]["canonical"]
                pub_date = parse_time(post["attributes"]["publishOn"], "%Y-%m-%dT%H:%M:%S-04:00")
                if link in ",".join(links):
                    print("seekalpha exists link: ", link)
                    break
                soup = BeautifulSoup(post["attributes"]["content"], 'lxml')
                ad_elements = soup.select('#more-links')
                # 移除这些元素
                for element in ad_elements:
                    element.decompose()
                description = str(soup)
                
                if description != "":
                  insert = True
                  articles.insert(
                      0,
                      {
                          "id": id,
                          "title": title,
                          "description": description,
                          "image": image,
                          "link": link,
                          "pub_date": pub_date,
                      },
                  )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            with open(filename, "w") as f:
                f.write(json.dumps({"data": articles}))
    else:
        print("seekalpha request error: ", response)


try:
    run()
except Exception as e:
    print("tipranks exec error: ", e)
    logging.exception(e)
