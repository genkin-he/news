import os
import subprocess
from datetime import datetime, timezone

directory = "./news/data"
log_file = "./news/log.md"

def get_folder_last_modified_time(folder):
    try:
        result = subprocess.run(["git", "log", "--pretty=format:%cd", "--", folder], capture_output=True, text=True)
        last_modified_time_str = result.stdout.strip().split('\n')[-1]
        if last_modified_time_str:
            # 解析日期时间字符串并设置为 UTC 时区
            last_modified_time = datetime.strptime(last_modified_time_str, "%a %b %d %H:%M:%S %Y %z").astimezone(timezone.utc)
            return last_modified_time
        else:
            return None
    except Exception as e:
        return None

def is_folder_older_than_one_day(folder):
    last_modified_time = get_folder_last_modified_time(folder)
    if last_modified_time is None:
        return False
    # 获取当前时间并设置为 UTC 时区
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - last_modified_time
    one_day_in_seconds = 86400
    return time_diff.total_seconds() > one_day_in_seconds

current_time = datetime.now()
current_minute = current_time.minute
current_hour = current_time.hour

if 0 <= current_minute <= 9 and current_hour == 11:
    with open(log_file, "w") as f:
        f.write("文件夹最后修改时间 (超过一天)\n")
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            if os.path.isdir(folder_path):
                if is_folder_older_than_one_day(folder_path):
                    f.write(f"【{folder_name}】最后修改时间: {get_folder_last_modified_time(folder_path)}\n")
else:
    # 打印中文说明并带上当前时间的小时和分钟部分
    print(f"不在执行时间范围内。当前时间: {current_time.hour}时{current_time.minute}分")
