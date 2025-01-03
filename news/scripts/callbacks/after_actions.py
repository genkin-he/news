import os
import urllib.request
import json

def send_feishu_webhook(message):
    webhook_url = os.getenv("feishu_webhook")
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(webhook_url, data=data, headers=headers)
    response = urllib.request.urlopen(request)
    if response.status != 200:
        print(f"发送飞书消息失败: {response.status}, {response.read().decode('utf-8')}")

def check_and_send_action_errors():
    action_errors = os.getenv("ACTION_ERRORS")
    if action_errors:
        send_feishu_webhook(action_errors)
        print("飞书消息已发送")
    else:
        print("环境变量 ACTION_ERRORS 不存在或为空")

if __name__ == "__main__":
    try:
        check_and_send_action_errors()
    except Exception as e:
        print(f"发送飞书消息过程中发生错误: {str(e)}")
