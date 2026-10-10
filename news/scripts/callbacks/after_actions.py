import os
import requests
import json

def send_slack_webhook(message):
    webhook_url = os.getenv("slack_webhook")
    if not webhook_url:
        print("错误: 未设置环境变量 'slack_webhook'")
        return
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "text": message
    }
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"错误: 发送 Slack 消息失败，状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"异常: 发送 Slack 消息时发生异常，错误信息: {str(e)}")

def check_and_send_action_errors():
    try:
        with open("./tmp/action_errors.log", "r") as file:
            action_errors = file.read().strip()
        if action_errors:
            send_slack_webhook(action_errors)
            print("信息: Slack 消息已成功发送")
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
        print(f"异常: 发送 Slack 消息过程中发生错误，错误信息: {str(e)}")
