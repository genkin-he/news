# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET

headers = {
    "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "accept-language": 'en;q=0.9',
    "cache-control": 'max-age=0',
    "priority": 'u=0, i',
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    "referer": 'https://www.investors.com/',
    "cookie": '_pxhd=qFf3JM9-14kiqEtLZXzztRNHlklOXWdp9WJ42KlfHZpWNJVLM6QN59O81cAJ5RrHd7BzF/bw6Jc45AIAWETqsg==:htkWlCWFHIOa9d4Alm/Uu-ueAG0MK81vWNb8zvmJucQ20/PkaGFN-nYJ6GfAUORMKwvIuMl/PyRgRcQ26057OD5-u8XxgbXT13YDe-IC3/g=; adOu=N; ibdVC=1; ibdFV=1; _lr_geo_location_state=SC; _lr_geo_location=CN; _pubcid=0c0a5f74-de38-43a6-8ad3-3e71da88caeb; _pubcid_cst=DCwOLBEsaQ%3D%3D; _lr_retry_request=true; _lr_env_src_ats=false; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-08-26T09%3A32%3A46%22%7D; pbjs-unifiedid_cst=CyzZLLwsaQ%3D%3D; consentUUID=b5dba01c-2acf-417a-bce4-f02ac150e886; usnatUUID=1b4ab8e0-6008-4567-b9e3-513ed2bab609; at_check=true; AMCVS_56B3E406563CC6B77F000101%40AdobeOrg=1; _gcl_au=1.1.2135900068.1758879168; s_ecid=MCMID%7C04513491947116553392413420119601909976; AMCV_56B3E406563CC6B77F000101%40AdobeOrg=-127034327%7CMCIDTS%7C20358%7CMCMID%7C04513491947116553392413420119601909976%7CMCAAMLH-1759483968%7C11%7CMCAAMB-1759483968%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1758886368s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.1.0; s_visit=1; s_cc=true; _ga=GA1.1.710504930.1758879172; _scid=G2uOa0pDf0UoIMOC8WsjSzxwSuzc3wg6; _ncg_sp_ses.0bcc=*; _ncg_id_=8125645c-7075-416e-b254-3f42a06ea8fd; _lr_sampling_rate=100; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.investors.com/tag/all-news-and-stock-ideas/%22%2C%22sref%22:%22%22%2C%22sts%22:1758879172725%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=f0576ba6-21be-4242-8089-072f3a1462c2%22%2C%22session_count%22:1%2C%22last_session_ts%22:1758879172725}; pxcts=c69e90b3-9abb-11f0-a902-e598a0ee9668; _pxvid=1b26be26-91d7-11f0-946f-c6ed38be50fe; _ScCbts=%5B%5D; _scor_uid=60203a6471b34fadae046c9103722c68; _cb=DYqGVnuG0E9FFflG; _ncg_domain_id_=8125645c-7075-416e-b254-3f42a06ea8fd.1.1758879172338.1821951172338; _sctr=1%7C1758816000000; _ncg_g_id_=4242e437-d7b0-4340-b2f5-7e91cd536bbc.3.1758879175.1821951172338; permutive-id=39042867-9adb-4b49-bd69-467a324fdc10; ab_uuid=f8a76b88-3a11-4597-a3a7-9f43ee4ebcb5; connect.sid=s%3AEIasVOqxVz1JKYPKJlv7vyREBRmEhyXY.axqDEs6sbpbnTF58Glnp28ceQQMHURNJrQh7tvd5owc; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIEYBmAVi4HYALFwCcAjvwBMANmk8AHF0EgAvkA; _pcid=%7B%22browserId%22%3A%22mg0nhqatgcn1egc1%22%7D; __pat=-14400000; xbc=%7Bkpcd%7DChBtZzBuaHFhdGdjbjFlZ2MxEgpmeGg4UHRFSnB1GjxUeHZhM0VpanFXZXY1Y1llUmtrelhmYkR6RWk1SjFwblJlVnNkVTNTRGlYZ0hIR24wRWlpZFlYTGR5dTkgAA; cX_P=mg0nhqatgcn1egc1; QSI_SI_b3B9jsfbYnFoklL_intercept=true; usr_prof_v2=eyJpYyI6M30%3D; s_sq=%5B%5BB%5D%5D; _awl=2.1758880363.5-1fc2420f653089410efb7e7ecde208ee-6763652d75732d7765737431-0; cto_bundle=8kJTYl9uM3pGMDIwa00xUGxJYk1DbFFnaHdRQiUyRjNlWmxYaDJzNyUyRldNSFVHMVA4Y0V0M0VzcG05UE1ydlk2NEtLU2hCUXU0eHZxd1VtUERDMmtDdGhxU1p0VlAzNExtWjhpbDAlMkZnUGJ5ZnJ1MUtkNSUyRmg0VE9ZM2NMeFhKUVhmdUVYemVxRkRBY1lyMXBvOFJBNXBJMGhsTG9tRkFCMVdVOFFUMWZmdTlZbG5hc0klMkZpJTJGZUpTQnlVMmlpRHZOYWR0MHNsbXRubjdBN0xyYkoyRFpObGpJQlRvS0xBJTNEJTNE; QSI_HistorySession=https%3A%2F%2Fwww.investors.com%2Ftag%2Fall-news-and-stock-ideas%2F~1758879401643%7Chttps%3A%2F%2Fwww.investors.com%2Fnews%2Ftechnology%2Fgoogle-stock-meta-gemini-ai-digital-ads%2F~1758879798628%7Chttps%3A%2F%2Fwww.investors.com%2Fresearch%2Fwhich-hot-stocks-just-joined-the-ibd-50-list-big-cap-20-more%2F~1758879804489%7Chttps%3A%2F%2Fwww.investors.com%2Fibd-videos%2Fvideos%2Findexes-fall-but-hold-support~1758880395105%7Chttps%3A%2F%2Fwww.investors.com%2Fresearch%2Fwhich-hot-stocks-just-joined-the-ibd-50-list-big-cap-20-more%2F~1758880517614; __cf_bm=oZmV7FLDHHfjxy8FW0FjSwwno3OCyGJinhV3S_rxTXQ-1758880590-1.0.1.1-Jw2MZsvZtT39DdUW_fn5PfTJmf8VstMdsUnQBE2V0nZV.NH1ZSwVzJAZ00Xv7EtkKlqqfq0kucm1s4Wes5.FtiS8Jckj8jwb8jz0QOH5gd8; ibdVS=638944775710795679; mbox=session#4a8e84b835454b01918d4cb03e3023da#1758881028|PC#4a8e84b835454b01918d4cb03e3023da.38_0#1822125574; _scid_r=KOuOa0pDf0UoIMOC8WsjSzxwSuzc3wg6vFMwjg; _ncg_sp_id.0bcc=8125645c-7075-416e-b254-3f42a06ea8fd.1758879172.1.1758880775.1758879172.5c6200b6-5265-403f-bcce-97c0e9fe2e86; _rdt_uuid=1758880364743.6b02edbe-07cc-4134-bf9f-4c8e5fa56c7d; __pvi=eyJpZCI6InYtbWcwbmhxYXhuZThoNWd2NyIsImRvbWFpbiI6Ii5pbnZlc3RvcnMuY29tIiwidGltZSI6MTc1ODg4MDc4MDQ3NH0%3D; ua-wn-pv=5; _chartbeat2=.1758879174535.1758880780773.1.g5fLDCt72ROCGLvW7DcMLvSBMYTT0.1; _cb_svref=external; _uetsid=c70bedf09abb11f0a06ceb0830141b68; _uetvid=c70bf2f09abb11f09de797d2713420a1; __tbc=%7Bkpcd%7DChBtZzBuaHFhdGdjbjFlZ2MxEgpmeGg4UHRFSnB1GjxUeHZhM0VpanFXZXY1Y1llUmtrelhmYkR6RWk1SjFwblJlVnNkVTNTRGlYZ0hIR24wRWlpZFlYTGR5dTkgAA; _px3=7dcdc08a93bcc3f1ee4eb2985f9902f1fc4301c313ad1cdd6d9d92048278f340:5fwzeV+4N6onDq+9xQueliVXIrMSm2ceVZb5MFTnow48KEfCSfc6VlN7eh6U4Fm9tAyal2v/r0JGKrWM0PrEVg==:1000:bEp5KCE2z7q2c9Cbl/tZulKRTgxOaLLX8FdLcYxsO5PwwEtXslEldcuCfloLlrh1ciuKbcWRu11f+0zfP2BYJ9LCUx6O/aAM2g5vW0NsP1eETOVnNKCoBY2jMWiIKmdPEc+TJnv6PAm+VJkig2/EpKCwxLSwqlXOcTYjNtA2/Z7qLIh9ejrnyMnYE7d9aBsc9b+QWthUkaeqJpGs+nlf6tlCec4sR0lcpj3isckRD9c=; _ga_K2H7B9JRSS=GS2.1.s1758879171$o1$g1$t1758880876$j43$l0$h522574813; _chartbeat4=t=BofTBrCvVVB0DnR8BexxMyBtLGAx&E=2&x=0&c=1.6&y=6321&w=471',
}

base_url = "https://www.investors.com/"
filename = "./news/data/investors/list.json"
current_links = []
post_count = 0
util = SpiderUtil()

def parse_rss_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)

        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'wfw': 'http://wellformedweb.org/CommentAPI/',
            'sy': 'http://purl.org/rss/1.0/modules/syndication/',
            'slash': 'http://purl.org/rss/1.0/modules/slash/'
        }

        items = []

        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')

            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text.strip() if link_elem.text else ""

                if title and link:
                    items.append({
                        'title': title,
                        'link': link
                    })

        return items
    except Exception as e:
        util.error("解析 RSS 时发生错误：{}".format(e))
        return []

def get_detail(link):
    util.info("link: {}".format(link))
    request = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        lxml = BeautifulSoup(resp, "lxml")
        soup = lxml.select_one("div.post-content")
        if soup is None:
            return ""
        ad_elements = soup.select(".video-player-container, script, .adunit, .subscribe-widget")
        for element in ad_elements:
            element.decompose()
        p_elements = soup.select("p")
        for p in p_elements:
            a_tags = p.select("a")
            if len(a_tags) == 1 and len(p.get_text(strip=True)) == len(a_tags[0].get_text(strip=True)):
                p.decompose()
        p_elements = soup.select("p")
        if len(p_elements) > 2:
            p_elements[-1].decompose()

        return str(soup).strip()
    else:
        util.error("request: {} error: {}".format(link, response))
        return ""


def run(url):
    post_count = 0
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    if response.status == 200:
        resp = response.read().decode("utf-8")
        rss_items = parse_rss_xml(resp)
        for item in rss_items:
            if post_count >= 2:
                break
            link = item['link']
            title = item['title']
            util.info("link: {}".format(link))
            if link in ",".join(links):
                util.info("exists link: {}".format(link))
                continue
            util.info("title: {}".format(title))
            if title == "":
                continue
            post_count = post_count + 1
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
                        "source": "investors",
                        "kind": 1,
                        "language": "en-US",
                    },
                )
        if len(articles) > 0 and insert:
            if len(articles) > 20:
                articles = articles[:20]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("request error: {}".format(response))


if __name__ == "__main__":
    # util.execute_with_timeout(run, "https://www.investors.com/tag/all-news-and-stock-ideas/feed/")
