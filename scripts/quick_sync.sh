#!/bin/bash

# Git 快速同步脚本
# 用于日常快速提交和同步

# 项目路径
PROJECT_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$PROJECT_PATH" || exit 1

echo -e "${GREEN}=== 烟小环境监测 Git 快速同步 ===${NC}"

# 检查是否有更改
if [[ -z $(git status --porcelain) ]]; then
    echo "没有需要提交的更改"
else
    echo "发现以下更改:"
    git status --short
    
    # 获取提交信息
    if [[ -n "$1" ]]; then
        COMMIT_MESSAGE="$1"
    else
        echo ""
        read -p "请输入提交信息 (或按回车使用默认信息): " COMMIT_MESSAGE
        if [[ -z "$COMMIT_MESSAGE" ]]; then
            COMMIT_MESSAGE="更新项目文件 - $(date '+%Y-%m-%d %H:%M:%S')"
        fi
    fi
    
    # 提交更改
    echo -e "${YELLOW}正在提交更改...${NC}"
    git add .
    git commit -m "$COMMIT_MESSAGE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 提交成功${NC}"
    else
        echo -e "${RED}✗ 提交失败${NC}"
        exit 1
    fi
fi

# 检查是否配置了远程仓库
if git remote | grep -q origin; then
    echo -e "${YELLOW}正在推送到远程仓库...${NC}"
    CURRENT_BRANCH=$(git branch --show-current)
    git push origin "$CURRENT_BRANCH" 2>/dev/null || git push -u origin "$CURRENT_BRANCH"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 推送成功${NC}"
    else
        echo -e "${RED}✗ 推送失败${NC}"
        echo "提示: 如果这是首次推送，请先设置远程仓库"
    fi
else
    echo -e "${YELLOW}未配置远程仓库，创建Bundle文件...${NC}"
    BUNDLE_PATH="../yanxiao-env-monitor-sync-$(date +%Y%m%d_%H%M%S).bundle"
    git bundle create "$BUNDLE_PATH" --all
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Bundle创建成功: $BUNDLE_PATH${NC}"
        echo "请将此文件复制到其他电脑使用"
    else
        echo -e "${RED}✗ Bundle创建失败${NC}"
    fi
fi

echo -e "${GREEN}=== 同步完成 ===${NC}"
