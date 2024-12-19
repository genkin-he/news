from longport.openapi import HttpClient
http_cli = HttpClient.from_env()
resp = http_cli.request("get", "/v1/content/articles?slug=stock_news")
print("article list: \n",resp)

# 翻页, 翻页参数是上一次请求的 next_params
resp = http_cli.request("get", "/v1/content/articles?slug=stock_news&params=eyJ0YWlsX21hcmsiOjE3MjkyMTk4MjMwMDAwMDAsImxpbWl0IjoyMCwic29ydCI6IkRFU0MifQ")
print("article list2: \n",resp)

resp = http_cli.request("get", "/v1/content/detail?target_id=217179400&target_type=Post")
print("article detail: \n", resp)