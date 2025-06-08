#!/bin/bash

# 多远程仓库分支同步脚本
# 同时推送到GitHub、Gitee等多个远程仓库

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔄 多远程仓库分支同步工具"
echo "============================="

# 获取当前分支
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "📍 当前分支: $current_branch"

# 检查工作区是否干净
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  工作区有未提交的更改${NC}"
    echo "请先提交或暂存更改再进行同步"
    exit 1
fi

# 获取所有远程仓库
remotes=($(git remote))
echo "🌐 发现的远程仓库: ${remotes[*]}"

# 推送到所有远程仓库
echo ""
echo "🚀 开始推送到所有远程仓库..."

sync_success=0
sync_failed=0

for remote in "${remotes[@]}"; do
    echo ""
    echo -e "${BLUE}推送到 $remote...${NC}"
    
    if git push "$remote" "$current_branch"; then
        echo -e "${GREEN}✅ $remote 推送成功${NC}"
        ((sync_success++))
    else
        echo -e "${RED}❌ $remote 推送失败${NC}"
        ((sync_failed++))
    fi
done

echo ""
echo "📊 同步结果汇总:"
echo "✅ 成功: $sync_success 个远程仓库"
echo "❌ 失败: $sync_failed 个远程仓库"

if [ $sync_failed -eq 0 ]; then
    echo -e "${GREEN}🎉 所有远程仓库同步成功！${NC}"
else
    echo -e "${YELLOW}⚠️  部分远程仓库同步失败，请检查网络连接或权限${NC}"
fi

echo ""
echo "🔍 当前各远程仓库分支状态:"
for remote in "${remotes[@]}"; do
    echo "📍 $remote:"
    git ls-remote "$remote" | grep "refs/heads/$current_branch" | head -1 || echo "   (该远程没有此分支)"
done
