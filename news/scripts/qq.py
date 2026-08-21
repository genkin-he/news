# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
from typing import Dict, List, Optional, Any
import requests
import json
from util.spider_util import SpiderUtil
from bs4 import BeautifulSoup
import re

class QQNewsSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "content-type": "application/json;charset=UTF-8",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "cookie": "pgv_pvid=4789840291; _qimei_uuid42=1890d0b380a100ae7892a3d5634134a3f2ecf2bb0e; pac_uid=0_DmwAW53xw9Qb1; _qimei_fingerprint=aeabff70721dd0ba31bdff8e1e2ef645; _qimei_h38=bafb75bb7892a3d5634134a30300000f41890d; _qimei_q36=; _clck=3562680173|1|fp8|0; RK=QLclrsSTG8; ptcz=a70854edd76a5e859ffae97817e32974ded748c6500099d32734ab44388feaec; suid=user_0_DmwAW53xw9Qb1; o_cookie=625118164; RECENT_CODE=09988_100%7C600519_1; w_token=87_D8KSmeaBx1IaLiPDbm8iF1hdslHXroVsZiHuQNWWA6eKbXZ0d1yuFOkpHRVw-OCBVWuaiumKXQTS_sYb4pGiovB1fPbE7NgJjTfvLe7dQk0; current-city-name=chengdu; lcad_appuser=EAEBE1F6F8B08D84; lcad_o_minduid=WxwK8cqQoWprEO-JWAEj3GvWi_LMorte; lcad_LPPBturn=406; lcad_LPSJturn=694; lcad_LBSturn=342; lcad_LVINturn=859; lcad_LDERturn=773",
            "Referer": "https://news.qq.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        self.base_url = "https://new.qq.com"
        self.filename = "./news/data/qq/list.json"
        self.util = SpiderUtil()
        self.max_articles = 15
        self.batch_size = 5

    def get_detail(self, link: str) -> str:
        """获取新闻详情内容"""
        try:
            self.util.info(f"Fetching detail for link: {link}")
            response = requests.get(link, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            lxml = BeautifulSoup(response.text, "lxml")
            content_selectors = [".rich_media_content", ".article-content-wrap", "#article-content"]
            
            for selector in content_selectors:
                soup = lxml.select_one(selector)
                if soup:
                    self._clean_content(soup)
                    return str(soup).strip()
                    
            self.util.log_action_error(f"未找到内容元素: {link}")
            return ""
            
        except requests.RequestException as e:
            self.util.error(f"请求错误 {link}: {str(e)}")
            return ""
        except Exception as e:
            self.util.error(f"处理详情时发生错误 {link}: {str(e)}")
            return ""

    def _clean_content(self, soup: BeautifulSoup) -> None:
        """清理文章内容中的广告和无关元素"""
        # 移除样式和脚本标签
        for element in soup.select("style, script"):
            element.decompose()

        # 处理广告内容
        contentify_wrap = soup.select_one(".comps-contentify-wrap")
        if contentify_wrap:
            qnt_p_elements = contentify_wrap.select(".qnt-p")
            if qnt_p_elements:
                last_qnt_p = qnt_p_elements[-1]
                if last_qnt_p.find_all("img") and len(last_qnt_p.contents) == len(last_qnt_p.find_all("img")):
                    last_qnt_p.decompose()

    def _extract_article_info(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从文章数据中提取所需信息"""
        try:
            if not post.get("link_info", {}).get("url"):
                self.util.info(f"ignore article_info link_info: {post['title']}")
                return None

            if post.get("articletype") != '0':
                self.util.info(f"ignore article_info articletype: {post['title']}")
                return None

            pub_date = post.get("publish_time")
            if not pub_date:
                self.util.info(f"ignore article_info pubtime: {post['title']}")
                return None

            return {
                "id": post["id"],
                "title": post["title"],
                "image": post.get("pic_info", {}).get("big_img", [""])[0],
                "link": post["link_info"]["url"],
                "author": post.get("media_info", {}).get("medal_info", {}).get("medal_name", ""),
                "pub_date": pub_date,
            }
        except KeyError as e:
            self.util.error(f"提取文章信息时缺少必要字段: {str(e)}")
            return None

    def run(self) -> None:
        """运行爬虫主程序"""
        try:
            data = self.util.history_posts(self.filename)
            articles = data["articles"]
            links = data["links"]
            insert = False

            request_data = {
                "base_req": {"from": "pc"},
                "forward": "1",
                "qimei36": "0_PYwE5ijzdmaCM",
                "device_id": "0_PYwE5ijzdmaCM",
                "flush_num": 1,
                "channel_id": "news_news_finance",
                "item_count": 12,
                "is_local_chlid": "0",
            }

            response = requests.post(
                "https://i.news.qq.com/web_feed/getPCList",
                headers=self.headers,
                data=json.dumps(request_data),
                timeout=10
            )
            response.raise_for_status()
            
            posts = response.json()["data"]
            self.util.info(f"posts: {len(posts)}")
            for post in posts[:self.batch_size]:
                article_info = self._extract_article_info(post)
                if not article_info:
                    continue

                if article_info["link"] in ",".join(links):
                    self.util.info(f"文章已存在: {article_info['link']}")
                    continue

                description = self.get_detail(article_info["link"])
                if description:
                    insert = True
                    article_info.update({
                        "description": description,
                        "source": "qq",
                        "kind": 1,
                        "language": "zh-CN",
                    })
                    articles.insert(0, article_info)

            if articles and insert:
                articles = articles[:self.max_articles]
                self.util.write_json_to_file(articles, self.filename)

        except requests.RequestException as e:
            self.util.log_action_error(f"请求错误: {str(e)}")
        except Exception as e:
            self.util.log_action_error(f"运行错误: {str(e)}")

def main():
    spider = QQNewsSpider()
    spider.util.execute_with_timeout(spider.run)

if __name__ == "__main__":
    main()
