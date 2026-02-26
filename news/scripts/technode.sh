#!/bin/bash
set -e

# 函数：处理 RSS feed，提取前10个 item
process_rss_feed() {
    local url="$1"
    local output_file="$2"
    local max_items="${3:-10}"  # 默认10个item，可以通过第三个参数自定义
    
    local user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    local temp_file="/tmp/rss_feed_$(basename "$output_file" .xml).xml"
    
    log() {
        local message="$1"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ${message}"
    }
    
    log "Starting request to RSS feed: $url"
    
    # 创建输出目录
    mkdir -p "$(dirname "$output_file")"
    
    # 下载完整的 XML feed
    curl --connect-timeout 10 -m 60 --globoff \
         --header "User-Agent: $user_agent" \
         "$url" > "$temp_file"
    
    log "Feed downloaded, processing XML..."
    
    # 检查是否安装了 xmlstarlet
    if ! command -v xmlstarlet &> /dev/null; then
        log "xmlstarlet not found, installing..."
        if command -v brew &> /dev/null; then
            brew install xmlstarlet
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y xmlstarlet
        else
            log "Please install xmlstarlet manually"
            return 1
        fi
    fi
    
    # 使用 xmlstarlet 提取指定数量的 item
    log "Extracting first $max_items items using xmlstarlet..."
    
    # 直接使用 xmlstarlet 重新构建 XML，只保留前N个 item
    xmlstarlet ed -d "//item[position() > $max_items]" "$temp_file" > "$output_file"
    
    # 清理临时文件
    rm -f "$temp_file"
    
    log "RSS feed processing completed. Output saved to: $output_file"
}

# 主程序
trap 'echo "$(date +%Y-%m-%d\ %H:%M:%S) - Error: $?"' ERR

# 调用函数处理 technode feed
process_rss_feed "https://technode.com/feed/" "./news/data/technode/technode.xml" 10
process_rss_feed "https://technode.global/category/news/feed/" "./news/data/technode/technode_global.xml" 10
