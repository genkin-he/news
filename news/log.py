import os
import subprocess
from datetime import datetime, timezone, timedelta

directory = "./news/data"
log_file = "./news/log.md"

def get_folder_last_modified_time(folder):
    try:
        # 查找文件的 git 最后提交时间
        result = subprocess.run(["git", "log", "-1", "--pretty=format:%cd", "--", folder], capture_output=True, text=True)
        last_modified_time_str = result.stdout.strip().split('\n')[-1]
        if last_modified_time_str:
            # 解析日期时间字符串并设置为北京时间时区
            last_modified_time = datetime.strptime(last_modified_time_str, "%a %b %d %H:%M:%S %Y %z").astimezone(timezone(timedelta(hours=8)))
            return last_modified_time
        else:
            return None
    except Exception as e:
        print(f"获取文件夹 {folder} 最后修改时间失败: {e}")
        return None

def is_folder_older_than_one_day(folder):
    last_modified_time = get_folder_last_modified_time(folder)
    if last_modified_time is None:
        return False
    # 获取当前时间并设置为北京时间
    current_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    time_diff = current_time - last_modified_time
    return time_diff.total_seconds() > 86400

def log_old_folders():
    current_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    with open(log_file, "w") as f:
        # 写入标题和当前时间
        f.write(f"文件夹最后修改时间 (超过一天) - {current_time.strftime('%Y-%m-%d %H:%M:%S')}<br>")
        for folder_name in os.listdir(directory):
                folder_path = os.path.join(directory, folder_name)
                if os.path.isdir(folder_path) and is_folder_older_than_one_day(folder_path):
                    f.write(f"【{folder_name}】最后修改时间: {get_folder_last_modified_time(folder_path)}<br>")

log_old_folders()
