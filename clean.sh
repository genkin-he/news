#!/bin/zsh
set -e  # 如果任何命令失败，立即退出脚本
cd ~/coding/gocode/news
# 检查本地是否存在 backup 标签，如果存在则删除
if git tag -l | grep -q "backup"; then
    echo "删除本地 backup 标签..."
    git tag -d backup
fi
git pull origin main
git tag backup && git push origin backup -f && rm -rf .git
git config --global init.defaultBranch main
git init .
git remote add origin git@github.com:genkin-he/news.git
git add .
git commit -am "clean"
git push origin -f
git branch --set-upstream-to=origin/main