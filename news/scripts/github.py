import os
import time
import urllib.request
import json

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ.get('token')}", # 从环境变量获取 token
    "X-GitHub-Api-Version": "2022-11-28"
}

def delete_workflow_runs():
    # 获取所有工作流运行记录
    request = urllib.request.Request(
        "https://api.github.com/repos/genkin-he/news/actions/runs?per_page=20&page=2&order=asc", 
        headers=headers
    )
    response = urllib.request.urlopen(request)
    runs = json.loads(response.read().decode("utf-8"))

    if len(runs["workflow_runs"]) == 0:
        print("没有运行记录")

    # 遍历并删除每个运行记录
    for run in runs["workflow_runs"]:
        run_id = run["id"]
        # 构造删除请求
        delete_url = f"https://api.github.com/repos/genkin-he/news/actions/runs/{run_id}"
        delete_request = urllib.request.Request(
            delete_url,
            method="DELETE",
            headers=headers
        )
        try:
            urllib.request.urlopen(delete_request)
            print(f"已删除运行记录 ID: {run_id}")
        except urllib.error.URLError as e:
            print(f"删除运行记录 ID: {run_id} 失败: {str(e)}")

if __name__ == "__main__":
    delete_workflow_runs()
