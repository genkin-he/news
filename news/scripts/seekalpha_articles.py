# -*- coding: UTF-8 -*-
import logging
import urllib.request  # 发送请求
import json
from util.util import history_posts, parse_time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=7082545252313; _sasource=; _gcl_au=1.1.1311499048.1728974860; _ga=GA1.1.811649761.1728974935; pxcts=92fc3a60-8ac1-11ef-8c11-8526ce5c7f16; _pxvid=92fc2a83-8ac1-11ef-8c11-735aad4ac3e3; hubspotutk=aacf8193fcc536210fa859f8f96025b1; __hssrc=1; _fbp=fb.1.1728974967880.601552600193935146; session_id=a77edde8-f357-4002-af0d-40007c789323; _clck=mixvur%7C2%7Cfq1%7C0%7C1749; __hstc=234155329.aacf8193fcc536210fa859f8f96025b1.1728974965776.1728974965776.1728981567594.2; _sapi_session_id=mSIe9q%2B38znRl%2BJC%2Bcwasb89IGXnz20r%2F9FuZ9LWK2Urk2FY5BNfA0Lym5jqhzu1XY6hfu%2F%2BtjrHyLpR5KJuSm4wvZaYW8lM%2FsMRlM85NcxTEdLr%2FLZMuWGZuaRvqSGHniwR7GTgqaZx4KzOzh1v970Iy9chgkSCpOjDDrdcIKKFlZLbo7G5zsfmXsA17uZlQlgKyEsfCPEdQ8meSGVa27jYGxFYFzRw0J3XSrdLpfBcUplSIlnK0tm8jpLmpRn7cLotcmTJ9PKxfXgNg8Ik9opTQA7avIilvFbbJHY5s48RoPfZHpXwPbd%2FKdKuC0FetbW1HzshO0rtKqRHPuF53xvTKznvfDpeBdxkL0JtWz8iCT6l5raVxsbQ6YXYjwOPKxuMECDHLpID0RKSLmgoayKS0glq2j7jtWUFxwxWE09aGm6GrjxtbD1NPa28nk9D1qVaER%2B8YLdbm68%2FGQ58AirbpC3hfroPxe4bFWJWnVqwjgQx8ye9oXFlt3NKC2HtbIpPnCPR6IyDuoAw%2FCB3Vzcf1NCZlx8dGCHxtFfMxuJ%2BGDbJe3av52%2F0IajJ920P5%2BmhC%2FNDM9fylfnzLFnZ5bnPEZ7jj84Hyfrft3Nt9FnY9h2az%2FSHurO%2FqQbUGmmgrLF6e0T6OYGwGivxNJiDOPHWiw5KKzY83YhdD5Rz07W1Lj4xlxmckXvAqEa7B8uFtSk5ECyjQVYiNJ1x--X7ca%2F1cRIFKyijQV--lIyiqHfuen6SykXQM85F9w%3D%3D; sailthru_hid=39b04d7c8e25d63b5e45e1150895dd0066b463a8da7c1f8f4b0510de06f5a2bed999b02abf867b7ee4da86f9; _ig=60795435; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fnews%2F4158383-aw-revenue-royalties-income-fund-reports-q3-results%22%2C%22pageKey%22%3A%22416af850-756e-481b-8f4d-687c0b650a3f%22%7D; sailthru_pageviews=16; sailthru_content=c5c2ea9708c5a29f0beab2731e45144274a1308ca14ee6552050275e8352f3ee93e28c6c185bf2e5f1449a6bdc218af162fce2a6c550abd7887dfa78d618b00ee8e17c15c9ddaeb241027e3ab58f5c9e; sailthru_visitor=e7385dcb-8aa7-4e8f-8603-e0bfc4df2614; _ga_KGRFF2R2C5=GS1.1.1728981562.2.1.1728983783.60.0.0; _uetsid=8beec1608ac111ef9b8a993f33d53106; _uetvid=8bef1eb08ac111efb141350bed2cd183; __hssc=234155329.15.1728981567594; _clsk=1o4q3c%7C1728983788517%7C10%7C0%7Cr.clarity.ms%2Fcollect; _px3=acd64004441676058092f28435e92b4af19dc7cf9949e808fafe31df7dfa4138:5WQL2QoxKCmkBaO6WIiqGJL7vUEm3S7F19//3S3K/JOuuECTrK3pUMFOrItyDi9Mo0CMLW95m+L9MiY2/lxh7w==:1000:pBbSmK95qrBGY7IIxuFJeqosDMwSxpjfOLRptlDVUCu+MXylBPbQl0Qd1N6ie639DFHfpBI0OR/YZOg/oKqIr9MFEHm+m71dx1T1P62l7VT29mMUqFkdUEqdSBaoFMpE2VDDEzamsGt2BY5W60zSTTEqS/PWRnD8obJGazXdfqLjP+9vm4WZ2dsktWuhOw982SN0EEKqYxAM7o/azX7uaUKDlm+lSO/m65RqdpahH7Q=; _pxde=80df35614aacb5ff7b1b8c3162051b30eeea5e0f8d567770f6cfe5e969da3e36:eyJ0aW1lc3RhbXAiOjE3Mjg5ODQxMDQxMDYsImZfa2IiOjB9; userLocalData_mone_session_lastSession=%7B%22machineCookie%22%3A%227082545252313%22%2C%22machineCookieSessionId%22%3A%227082545252313%261728981560924%22%2C%22sessionStart%22%3A1728981560924%2C%22sessionEnd%22%3A1728985949900%2C%22firstSessionPageKey%22%3A%2238a05a7a-dfb3-4852-be27-5f1d78443201%22%2C%22isSessionStart%22%3Afalse%2C%22lastEvent%22%3A%7B%22event_type%22%3A%22mousemove%22%2C%22timestamp%22%3A1728984149900%7D%7D",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"


def get_detail(id):
    link = "https://seekingalpha.com/api/v3/articles/{}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cauthor.userBioTags%2Cco_authors%2CpromotedService%2Csentiments".format(
        id
    )
    request = urllib.request.Request(
        link,
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        content = json.loads(body)["data"]["attributes"]["content"]
        return content

def run():
    data = history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=5&page[number]=1",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 1:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = base_url + post["links"]["self"]
                pub_date = parse_time(
                    post["attributes"]["publishOn"], "%Y-%m-%dT%H:%M:%S-04:00"
                )
                if link in ",".join(links):
                    print("seekalpha_articles exists link: ", link)
                    break
                description = get_detail(id)
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
        print("seekalpha_articles request error: ", response)

try:
    run()
except Exception as e:
    print("seekalpha_articles exec error: ", e)
    logging.exception(e)
