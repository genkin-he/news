#!/bin/bash

# Redis 连接测试脚本
# 用于测试您的 Redis 连接配置

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

echo -e "${BLUE}=== Redis 连接测试 ===${NC}"

# 测试连接
echo -e "\n${YELLOW}测试 Redis 连接...${NC}"
if $REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 连接成功${NC}"
else
    echo -e "${RED}✗ 连接失败${NC}"
    echo "请检查以下配置："
    echo "1. Redis CLI 路径: $REDIS_CLI_PATH"
    echo "2. 主机地址: $REDIS_HOST"
    echo "3. 端口: $REDIS_PORT"
    echo "4. CA 证书路径: $REDIS_CA_CERT"
    echo "5. 密码是否正确"
    exit 1
fi

# 测试基本命令
echo -e "\n${YELLOW}测试基本命令...${NC}"
echo "PING 命令:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD ping

echo -e "\nINFO 命令:"
$REDIS_CLI_PATH -h $REDIS_HOST -p $REDIS_PORT --tls --cacert $REDIS_CA_CERT -a $REDIS_PASSWORD info server | head -5

echo -e "\n${GREEN}✓ 连接测试完成${NC}" 