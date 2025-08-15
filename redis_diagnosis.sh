#!/bin/bash

# Redis 诊断脚本
# 用于检查内存使用情况和数据清理问题

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
NC='\033[0m' # No Color

echo -e "${BLUE}=== Redis 内存诊断工具 ===${NC}"

# 检查 Redis 连接
echo -e "\n${YELLOW}1. 检查 Redis 连接状态${NC}"
if $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis 连接正常${NC}"
else
    echo -e "${RED}✗ Redis 连接失败${NC}"
    echo "请检查 Redis 服务是否运行"
    exit 1
fi

# 内存使用情况
echo -e "\n${YELLOW}2. 内存使用情况${NC}"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD info memory | grep -E "(used_memory|used_memory_human|used_memory_peak|used_memory_peak_human|used_memory_rss|used_memory_rss_human|maxmemory|maxmemory_human)"

# 内存策略
echo -e "\n${YELLOW}3. 内存策略配置${NC}"
echo "最大内存设置:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD config get maxmemory
echo "内存策略:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD config get maxmemory-policy

# 数据库统计
echo -e "\n${YELLOW}4. 数据库统计${NC}"
echo "键总数:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD dbsize
echo "数据库数量:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD config get databases

# 内存碎片率
echo -e "\n${YELLOW}5. 内存碎片率${NC}"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD info memory | grep mem_fragmentation_ratio

# 过期键统计
echo -e "\n${YELLOW}6. 过期键统计${NC}"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD info keyspace

# 检查特定键（如果提供）
if [ ! -z "$1" ]; then
    echo -e "\n${YELLOW}7. 检查特定键: $1${NC}"
    echo "键是否存在:"
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD exists "$1"
    echo "键类型:"
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD type "$1"
    echo "过期时间 (秒):"
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD ttl "$1"
    echo "键值大小:"
    $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD memory usage "$1" 2>/dev/null || echo "无法获取内存使用量"
fi

# 内存使用警告
echo -e "\n${YELLOW}8. 内存使用分析${NC}"
USED_MEMORY=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD info memory | grep used_memory: | cut -d: -f2)
MAX_MEMORY=$($REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD config get maxmemory | tail -1)

if [ "$MAX_MEMORY" != "0" ] && [ "$USED_MEMORY" -gt 0 ]; then
    USAGE_PERCENT=$((USED_MEMORY * 100 / MAX_MEMORY))
    if [ $USAGE_PERCENT -gt 80 ]; then
        echo -e "${RED}⚠️  内存使用率较高: ${USAGE_PERCENT}%${NC}"
        echo "这可能导致数据被提前清理"
    elif [ $USAGE_PERCENT -gt 60 ]; then
        echo -e "${YELLOW}⚠️  内存使用率中等: ${USAGE_PERCENT}%${NC}"
    else
        echo -e "${GREEN}✓ 内存使用率正常: ${USAGE_PERCENT}%${NC}"
    fi
fi

echo -e "\n${BLUE}=== 诊断完成 ===${NC}" 