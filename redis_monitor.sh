#!/bin/bash

# Redis 键监控脚本
# 用于监控键的生命周期和变化

REDIS_HOST="r-3nscd519f5981694.redis.rds.aliyuncs.com"
REDIS_PORT="6379"
REDIS_PASSWORD="OtZKUvj_21PJo6vQeG-m04X-qjBFTj"
REDIS_CLI_PATH="/home/core/redis-7.0.0/src/redis-cli"
REDIS_CA_CERT="/home/core/redis-7.0.0/ca.pem"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Redis 键监控工具 ===${NC}"

# 监控键的变化
monitor_keys() {
    echo -e "\n${YELLOW}开始监控键的变化 (按 Ctrl+C 停止)${NC}"
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD monitor | while read line; do
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] $line"
    done
}

# 检查特定键的状态
check_key_status() {
    local key=$1
    echo -e "\n${YELLOW}检查键: $key${NC}"
    
    # 检查键是否存在
    exists=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD exists "$key")
    if [ "$exists" -eq 1 ]; then
        echo -e "${GREEN}✓ 键存在${NC}"
        
        # 获取键类型
        type=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD type "$key")
        echo "类型: $type"
        
        # 获取过期时间
        ttl=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD ttl "$key")
        if [ "$ttl" -eq -1 ]; then
            echo "过期时间: 永不过期"
        elif [ "$ttl" -eq -2 ]; then
            echo "过期时间: 键不存在"
        else
            echo "过期时间: ${ttl}秒"
        fi
        
        # 获取内存使用量
        memory=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD memory usage "$key" 2>/dev/null)
        if [ ! -z "$memory" ]; then
            echo "内存使用: ${memory}字节"
        fi
        
        # 获取键值长度
        if [ "$type" = "string" ]; then
            length=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD strlen "$key")
            echo "值长度: ${length}字符"
        elif [ "$type" = "list" ]; then
            length=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD llen "$key")
            echo "列表长度: ${length}个元素"
        elif [ "$type" = "set" ]; then
            length=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD scard "$key")
            echo "集合大小: ${length}个元素"
        elif [ "$type" = "hash" ]; then
            length=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD hlen "$key")
            echo "哈希字段数: ${length}个"
        fi
    else
        echo -e "${RED}✗ 键不存在${NC}"
    fi
}

# 扫描所有键
scan_all_keys() {
    echo -e "\n${YELLOW}扫描所有键${NC}"
    count=0
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD --scan --pattern "*" | while read key; do
        count=$((count + 1))
        echo "键 $count: $key"
        check_key_status "$key"
        echo "---"
    done
    
    if [ $count -eq 0 ]; then
        echo "没有找到任何键"
    fi
}

# 主菜单
show_menu() {
    echo -e "\n${BLUE}请选择操作:${NC}"
    echo "1. 监控键的变化"
    echo "2. 检查特定键"
    echo "3. 扫描所有键"
    echo "4. 退出"
    echo -n "请输入选择 (1-4): "
}

# 主程序
main() {
    while true; do
        show_menu
        read choice
        
        case $choice in
            1)
                monitor_keys
                ;;
            2)
                echo -n "请输入键名: "
                read key_name
                if [ ! -z "$key_name" ]; then
                    check_key_status "$key_name"
                fi
                ;;
            3)
                scan_all_keys
                ;;
            4)
                echo "退出程序"
                exit 0
                ;;
            *)
                echo "无效选择，请重新输入"
                ;;
        esac
    done
}

# 运行主程序
main 