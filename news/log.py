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
    current_minute = current_time.minute
    current_hour = current_time.hour

    # 只在 10:30 - 10:39 之间执行
    if 30 <= current_minute <= 39 and current_hour == 10:
        with open(log_file, "w") as f:
            # 写入标题和当前时间
            f.write(f"文件夹最后修改时间 (超过一天) - {current_time.strftime('%Y-%m-%d %H:%M:%S')}<br>")
            for folder_name in os.listdir(directory):
                folder_path = os.path.join(directory, folder_name)
                if os.path.isdir(folder_path) and is_folder_older_than_one_day(folder_path):
                    f.write(f"【{folder_name}】最后修改时间: {get_folder_last_modified_time(folder_path)}<br>")
    else:
        # 打印中文说明并带上当前时间的小时和分钟部分
        print(f"不在执行时间范围内。当前时间: {current_time.hour}时{current_time.minute}分")

log_old_folders()
