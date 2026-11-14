import datetime
import os
import json
import requests
import time
from typing import List, Dict
import asyncio
import aiohttp


def fetch_proxies() -> List[Dict[str, str]]:
    """
    从代理网站爬取代理IP列表
    """
    # proxies.extend(
    #     from_kuaidaili(url="https://free.kuaidaili.com/free/fps/", region="GLOBAL")
    # )
    # proxies.extend(
    #     from_kuaidaili(url="https://free.kuaidaili.com/free/", region="CN")
    # )
    proxies = []
    proxies.extend(from_shark_free())
    return proxies


kuaidaili_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_gcl_au=1.1.584344619.1739515050; _gcl_aw=GCL.1739515197.EAIaIQobChMI3pyUiMfCiwMV7NYWBR0EfRTMEAAYAiAAEgKkefD_BwE; _gcl_gs=2.1.k1$i1739515196$u89030785; _gid=GA1.2.1302795015.1739515257; Hm_lvt_7ed65b1cc4b810e9fd37959c9bb51b31=1739515257; Hm_lpvt_7ed65b1cc4b810e9fd37959c9bb51b31=1739515257; HMACCOUNT=F2892E7D6508A4A8; channelid=0; sid=1739515282302469; _ga=GA1.1.1271020931.1739515050; _ss_s_uid=f441f3887cb316f8addec4aa38097047; _ga_DC1XM0P4JL=GS1.1.1739515049.1.1.1739521349.60.0.0",
}


def verify_proxy(proxy: Dict[str, str]) -> bool:
    """
    验证代理是否可用
    """
    try:
        if proxy["region"] == "CN":
            test_url = "https://www.baidu.com/"
        else:
            test_url = "https://www.google.com/"

        response = requests.get(test_url, proxies=proxy, timeout=10)
        if response.status_code != 200:
            print(f"无效代理: {proxy}")
            return False

        print(f"有效代理: {proxy}")
        return True

    except Exception as e:
        print(f"代理验证失败: {proxy}, 错误: {str(e)}")
        return False


def from_shark_free() -> List[Dict[str, str]]:
    """
    从所有免费代理获取代理
    """
    proxies = []
    try:
        for page_no in range(1, 6):
            response = requests.get(
                f"https://proxy.010438.xyz/proxy/list?pageNo={page_no}", timeout=10
            )
            if response.status_code == 200:
                ip_pools = response.json()["data"]["list"]
                for ip_pool in ip_pools:
                    if ip_pool["type"] != 1:
                        continue
                    proxy = {
                        "http": f"http://{ip_pool['ip']}:{ip_pool['port']}",
                        "region": "CN" if ip_pool["country"] == "中国" else "GLOBAL",
                    }
                    # 只在支持 HTTPS 时添加 HTTPS 代理
                    if ip_pool["supportHttps"] == 1:
                        proxy["https"] = f"https://{ip_pool['ip']}:{ip_pool['port']}"
                    # 不添加 all 字段
                    proxies.append(proxy)
            time.sleep(1)
    except Exception as e:
        print(f"爬取代理时发生错误 from_all_free: {str(e)}")
    return proxies


def from_kuaidaili(url: str, region: str) -> List[Dict[str, str]]:
    """
    从快代理获取代理
    """
    proxies = []
    try:
        response = requests.get(url, headers=kuaidaili_headers, timeout=10)
        # 直接从 response.text 中获取 解析出 const fpsList = 字符串后面的数组值
        if "const fpsList = " in response.text:
            ip_pools = response.text.split("const fpsList = ")[1].split(";")[0]
            # ip_pools 是 [{ip: '1.1.1.1', port: '8080'}, {ip: '1.1.1.2', port: '8081'}] 这样的格式的字符串转为 Python 数组
            ip_pools = json.loads(ip_pools)
            for ip_pool in ip_pools:
                if "is_valid" in ip_pool and not ip_pool["is_valid"]:
                    continue
                ip = ip_pool["ip"]
                port = ip_pool["port"]
                proxies.append(
                    {
                        "https": f"https://{ip}:{port}",
                        "http": f"http://{ip}:{port}",
                        "region": region,
                    }
                )
        print("from_kuaidaili: ", proxies)
    except Exception as e:
        print(f"爬取代理时发生错误 from_kuaidaili: {str(e)}")
    return proxies


def get_valid_proxies() -> List[Dict[str, str]]:
    """
    获取有效的代理列表
    """
    all_proxies = fetch_proxies()
    valid_proxies = []

    # 不使用并发验证
    for proxy in all_proxies:
        if verify_proxy(proxy):
            valid_proxies.append(proxy)
            print(f"找到有效代理: {proxy}")

    return valid_proxies


def save_proxies_to_json(proxies: List[Dict[str, str]]) -> None:
    """
    将代理列表保存到JSON文件
    """
    json_path = os.path.join(os.path.dirname(__file__), "../util/proxy_pool.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(proxies, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), "../../config/proxy.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 检查上次运行时间和更新频率
            update_interval = config.get("interval", 1800)  # 默认30分钟更新一次
            last_run = config.get(
                "last_run",
                (
                    datetime.datetime.now()
                    - datetime.timedelta(seconds=update_interval + 1)
                ).isoformat(),
            )

            last_run_time = datetime.datetime.fromisoformat(last_run)
            current_time = datetime.datetime.now()
            time_diff = (current_time - last_run_time).total_seconds()

            if time_diff < update_interval:
                print(f"距离上次更新时间不足{update_interval}秒，跳过本次更新")
            else:
                print("开始更新代理池...")
                valid_proxies = get_valid_proxies()
                save_proxies_to_json(valid_proxies)

                # 更新最后运行时间
                config["last_run"] = datetime.datetime.now().isoformat()
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                    print(f"代理池更新完成，共保存 {len(valid_proxies)} 个有效代理")
        else:
            # 如果配置文件不存在，创建默认配置
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            config = {"interval": 1800}
    except Exception as e:
        print(f"更新代理池过程中发生错误: {str(e)}")
