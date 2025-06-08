#!/bin/bash

# 分支管理快速操作脚本
# 提供常用的分支管理命令

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}分支管理工具${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  status      - 显示当前分支状态和同步情况"
    echo "  sync        - 同步dev分支与master分支"
    echo "  sync-all    - 同步当前分支到所有远程仓库"
    echo "  dev         - 切换到dev分支并拉取最新代码"
    echo "  master      - 切换到master分支并拉取最新代码"
    echo "  release     - 将dev分支的稳定代码发布到master"
    echo "  hotfix      - 创建紧急修复分支"
    echo "  clean       - 清理本地分支"
    echo "  backup      - 创建当前状态的备份标签"
    echo "  help        - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status    # 查看分支状态"
    echo "  $0 dev       # 切换到开发分支"
    echo "  $0 sync-all  # 同步到所有远程仓库"
    echo "  $0 release   # 发布到生产分支"
}

# 显示分支状态
show_status() {
    echo -e "${BLUE}=== 分支状态检查 ===${NC}"
    
    # 当前分支
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    echo -e "当前分支: ${GREEN}$current_branch${NC}"
    
    # 检查工作区状态
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "工作区状态: ${YELLOW}有未提交的更改${NC}"
        git status --short
    else
        echo -e "工作区状态: ${GREEN}干净${NC}"
    fi
    
    # 检查分支同步状态
    echo ""
    echo -e "${BLUE}=== 分支同步状态 ===${NC}"
    
    # 获取远程分支信息
    git fetch origin
    
    # 检查dev分支与master分支的差异
    dev_ahead=$(git rev-list --count master..dev 2>/dev/null || echo "0")
    dev_behind=$(git rev-list --count dev..master 2>/dev/null || echo "0")
    
    echo "dev分支领先master: $dev_ahead 个提交"
    echo "dev分支落后master: $dev_behind 个提交"
    
    # 检查与远程分支的差异
    if [ "$current_branch" = "dev" ]; then
        local_ahead=$(git rev-list --count origin/dev..HEAD 2>/dev/null || echo "0")
        local_behind=$(git rev-list --count HEAD..origin/dev 2>/dev/null || echo "0")
        echo "本地dev领先远程: $local_ahead 个提交"
        echo "本地dev落后远程: $local_behind 个提交"
    fi
}

# 同步分支
sync_branches() {
    echo -e "${BLUE}=== 同步分支 ===${NC}"
    
    # 确保工作区干净
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}错误: 工作区有未提交的更改，请先提交或暂存${NC}"
        return 1
    fi
    
    # 获取最新远程信息
    git fetch origin
    
    # 如果当前在dev分支，同步master的更新
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" = "dev" ]; then
        echo "从master分支同步更新到dev分支..."
        git merge origin/master --no-ff -m "sync: 从master同步更新"
        echo -e "${GREEN}dev分支同步完成${NC}"
    else
        echo -e "${YELLOW}请切换到dev分支后再执行同步${NC}"
    fi
}

# 切换到dev分支
switch_to_dev() {
    echo -e "${BLUE}=== 切换到dev分支 ===${NC}"
    git checkout dev
    git pull origin dev
    echo -e "${GREEN}已切换到dev分支并更新到最新版本${NC}"
}

# 切换到master分支
switch_to_master() {
    echo -e "${BLUE}=== 切换到master分支 ===${NC}"
    git checkout master
    git pull origin master
    echo -e "${GREEN}已切换到master分支并更新到最新版本${NC}"
}

# 发布到master分支
release_to_master() {
    echo -e "${BLUE}=== 发布到master分支 ===${NC}"
    
    # 确保当前在dev分支
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "dev" ]; then
        echo -e "${RED}错误: 请在dev分支上执行发布操作${NC}"
        return 1
    fi
    
    # 确保工作区干净
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}错误: 工作区有未提交的更改，请先提交${NC}"
        return 1
    fi
    
    # 确认发布
    echo -e "${YELLOW}即将将dev分支的代码发布到master分支${NC}"
    echo "这将更新生产环境，请确认所有测试已通过。"
    read -p "确认发布? (y/N): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "发布已取消"
        return 0
    fi
    
    # 切换到master并合并
    git checkout master
    git pull origin master
    
    # 询问版本号
    read -p "请输入版本号 (如: v1.2.3): " version
    
    git merge dev --no-ff -m "release: 发布版本 $version"
    git push origin master
    
    # 创建标签
    if [ ! -z "$version" ]; then
        git tag -a "$version" -m "Release $version"
        git push origin "$version"
        echo -e "${GREEN}已创建版本标签: $version${NC}"
    fi
    
    # 切换回dev分支
    git checkout dev
    
    echo -e "${GREEN}发布完成！${NC}"
}

# 创建hotfix分支
create_hotfix() {
    echo -e "${BLUE}=== 创建hotfix分支 ===${NC}"
    
    read -p "请输入hotfix分支名称 (如: hotfix-critical-bug): " hotfix_name
    
    if [ -z "$hotfix_name" ]; then
        echo -e "${RED}错误: 分支名称不能为空${NC}"
        return 1
    fi
    
    # 从master创建hotfix分支
    git checkout master
    git pull origin master
    git checkout -b "$hotfix_name"
    
    echo -e "${GREEN}hotfix分支 '$hotfix_name' 创建完成${NC}"
    echo "请在此分支进行修复，完成后:"
    echo "1. 合并到master分支"
    echo "2. 合并到dev分支"
    echo "3. 删除hotfix分支"
}

# 清理本地分支
clean_branches() {
    echo -e "${BLUE}=== 清理本地分支 ===${NC}"
    
    # 显示已合并的分支
    merged_branches=$(git branch --merged | grep -v "\*\|master\|dev")
    
    if [ -z "$merged_branches" ]; then
        echo "没有需要清理的分支"
        return 0
    fi
    
    echo "以下分支已合并，可以安全删除:"
    echo "$merged_branches"
    
    read -p "是否删除这些分支? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "$merged_branches" | xargs -n 1 git branch -d
        echo -e "${GREEN}分支清理完成${NC}"
    fi
}

# 创建备份标签
create_backup() {
    echo -e "${BLUE}=== 创建备份标签 ===${NC}"
    
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_tag="backup_${current_branch}_${timestamp}"
    
    git tag -a "$backup_tag" -m "Backup of $current_branch at $timestamp"
    
    echo -e "${GREEN}备份标签创建完成: $backup_tag${NC}"
    
    read -p "是否推送备份标签到远程? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        git push origin "$backup_tag"
        echo -e "${GREEN}备份标签已推送到远程${NC}"
    fi
}

# 多远程仓库同步
sync_all_remotes() {
    echo -e "${BLUE}=== 多远程仓库同步 ===${NC}"
    
    # 检查工作区是否干净
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠️  工作区有未提交的更改，请先提交再同步${NC}"
        return 1
    fi
    
    # 运行多远程同步脚本
    script_dir="$(dirname "$(realpath "$0")")"
    sync_script="$script_dir/multi-remote-sync.sh"
    
    if [ -f "$sync_script" ]; then
        "$sync_script"
    else
        echo -e "${RED}❌ 多远程同步脚本不存在: $sync_script${NC}"
        return 1
    fi
}

# 主函数
main() {
    case "$1" in
        "status")
            show_status
            ;;
        "sync")
            sync_branches
            ;;
        "sync-all")
            sync_all_remotes
            ;;
        "dev")
            switch_to_dev
            ;;
        "master")
            switch_to_master
            ;;
        "release")
            release_to_master
            ;;
        "hotfix")
            create_hotfix
            ;;
        "clean")
            clean_branches
            ;;
        "backup")
            create_backup
            ;;
        "help"|"")
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 检查是否在git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误: 当前目录不是git仓库${NC}"
    exit 1
fi

main "$@"
