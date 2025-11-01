import requests
import json


class FX168NewsAPI:
    def __init__(self):
        self.base_url = "https://centerapi.fx168api.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': 'https://www.fx168news.com',
            'Referer': 'https://www.fx168news.com/',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Storage-Access': 'active',
            'Site-Channel': '001',
            'Priority': 'u=1, i'
        })

    def get_json_by_url(self, url, params={}, pcc_value=None):
        if pcc_value:
            self.session.headers['_pcc'] = pcc_value
        else:
            default_pcc = "mxx52hRTGLfIdgFccnkJ7dnGJqv91ktFjgyu3Ud0gvuAykMs0Xm00vXMJJBcwd/DGCL4CH7O8ziW0DYqHVWcGUneH/NlXUeKLe3w2h6cr/iJnaWvH0hzF/ypcqhOnES8YqVUUxpe7UQHAvprGVD1hoVMwY/2HV/bE9SXhTtM85Q="
            self.session.headers['_pcc'] = default_pcc
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except json.JSONDecodeError as e:
                    return None
            else:
                return None
        except requests.exceptions.RequestException as e:
            return None
