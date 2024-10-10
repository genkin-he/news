#!/bin/bash

directory="./news/data"
log_file="./news/log.md"

current_hour=$(date +%H)
current_minute=$(date +%M)

# if [ $current_hour -eq 11 ] && [ $current_minute -ge 0 ] && [ $current_minute -le 9 ]; then
    # 清空 log.md 文件，如果文件不存在则创建
    > $log_file

    current_time=$(date +%s)

    for item in "$directory"/*; do
        if [ -e "$item" ]; then
            # 获取文件或文件夹的最后修改时间戳
            modification_info=$(stat -f "%m %Sp %N" "$item")
            if [ -z "$modification_info" ]; then
                echo "Error getting modification time for $item"
                continue
            fi
            modification_time=$(echo "$modification_info" | awk '{print $1}')
            time_diff=$((current_time - modification_time))
            # 一天的秒数为 86400
            if [ $time_diff -gt 86400 ]; then
                modification_time_formatted=$(date -r $modification_time +"%Y-%m-%d %H:%M:%S")
                echo "**$item** 最后修改时间： $modification_time_formatted <br>" >> $log_file
            fi
        fi
    done
# fi