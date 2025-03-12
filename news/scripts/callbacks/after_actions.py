import os
import urllib.request
import json

def send_feishu_webhook(message):
    webhook_url = os.getenv("feishu_webhook")
    if not webhook_url:
        print("错误: 未设置环境变量 'feishu_webhook'")
        return
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
    try:
        request = urllib.request.Request(webhook_url, data=data, headers=headers)
        response = urllib.request.urlopen(request)
        if response.status != 200:
            print(f"错误: 发送飞书消息失败，状态码: {response.status}, 响应: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"异常: 发送飞书消息时发生异常，错误信息: {str(e)}")

def check_and_send_action_errors():
    try:
        with open("./tmp/action_errors.log", "r") as file:
            action_errors = file.read().strip()
        if action_errors:
            send_feishu_webhook(action_errors)
            print("信息: 飞书消息已成功发送")
        else:
            print("警告: action_errors.log 文件不存在或为空")
    except FileNotFoundError:
        print("错误: 未找到 action_errors.log 文件")
    except Exception as e:
        print(f"异常: 读取 action_errors.log 文件时发生错误，错误信息: {str(e)}")

if __name__ == "__main__":
    try:
        check_and_send_action_errors()
        with open("./tmp/action_errors.log", "w") as file:
            file.write("")
        print("信息: action_errors.log 文件内容已清空")
    except Exception as e:
        print(f"异常: 发送飞书消息过程中发生错误，错误信息: {str(e)}")
