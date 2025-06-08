#!/bin/bash

# 分支管理工具

show_help() {
    echo "分支管理工具"
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  status  - 显示分支状态"
    echo "  dev     - 切换到dev分支"
    echo "  master  - 切换到master分支"
    echo "  sync    - 同步分支"
    echo "  help    - 显示帮助"
}

show_status() {
    echo "=== 分支状态 ==="
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    echo "当前分支: $current_branch"
    
    if [ -n "$(git status --porcelain)" ]; then
        echo "工作区状态: 有未提交更改"
        git status --short
    else
        echo "工作区状态: 干净"
    fi
}

switch_to_dev() {
    echo "切换到dev分支..."
    git checkout dev && git pull origin dev
}

switch_to_master() {
    echo "切换到master分支..."
    git checkout master && git pull origin master
}

sync_branches() {
    echo "同步分支..."
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" = "dev" ]; then
        git merge origin/master --no-ff -m "sync: 从master同步更新"
    else
        echo "请在dev分支执行同步"
    fi
}

case "$1" in
    "status") show_status ;;
    "dev") switch_to_dev ;;
    "master") switch_to_master ;;
    "sync") sync_branches ;;
    "help"|"") show_help ;;
    *) echo "未知命令: $1"; show_help ;;
esac
