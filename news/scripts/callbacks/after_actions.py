import os
import requests

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
    response = requests.post(webhook_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"发送飞书消息失败: {response.status_code}, {response.text}")

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
