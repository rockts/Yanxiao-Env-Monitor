#!/bin/bash

# Git 多电脑同步工具
# 作者: GitHub Copilot
# 用途: 解决通过云盘同步文件但Git提交记录不一致的问题

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Git状态
check_git_status() {
    cd "$PROJECT_PATH" || exit 1
    
    log_info "检查Git状态..."
    
    # 检查是否是Git仓库
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        return 1
    fi
    
    # 检查工作区状态
    if [[ -n $(git status --porcelain) ]]; then
        log_warning "工作区有未提交的更改"
        git status --short
        return 2
    fi
    
    log_success "Git状态正常"
    return 0
}

# 获取当前分支
get_current_branch() {
    git branch --show-current
}

# 同步前准备
prepare_sync() {
    log_info "准备同步..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 获取当前分支
    CURRENT_BRANCH=$(get_current_branch)
    log_info "当前分支: $CURRENT_BRANCH"
    
    # 检查远程仓库
    if ! git remote | grep -q origin; then
        log_warning "未配置远程仓库"
        setup_remote_repo
    fi
}

# 设置远程仓库
setup_remote_repo() {
    log_info "设置远程仓库..."
    
    echo "请选择远程仓库类型:"
    echo "1) GitHub"
    echo "2) GitLab"
    echo "3) Gitee"
    echo "4) 其他"
    echo "5) 跳过（使用Bundle方式）"
    
    read -p "请输入选择 (1-5): " choice
    
    case $choice in
        1|2|3|4)
            read -p "请输入远程仓库URL: " repo_url
            git remote add origin "$repo_url"
            log_success "远程仓库已添加"
            ;;
        5)
            log_info "跳过远程仓库设置，将使用Bundle方式"
            return 1
            ;;
        *)
            log_error "无效选择"
            return 1
            ;;
    esac
}

# 推送到远程仓库
push_to_remote() {
    log_info "推送到远程仓库..."
    
    CURRENT_BRANCH=$(get_current_branch)
    
    # 首次推送需要设置上游分支
    if ! git push origin "$CURRENT_BRANCH" 2>/dev/null; then
        log_info "首次推送，设置上游分支..."
        git push -u origin "$CURRENT_BRANCH"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "推送成功"
    else
        log_error "推送失败"
        return 1
    fi
}

# 从远程仓库拉取
pull_from_remote() {
    log_info "从远程仓库拉取..."
    
    CURRENT_BRANCH=$(get_current_branch)
    
    git pull origin "$CURRENT_BRANCH"
    
    if [ $? -eq 0 ]; then
        log_success "拉取成功"
    else
        log_error "拉取失败"
        return 1
    fi
}

# 创建Git Bundle
create_bundle() {
    log_info "创建Git Bundle..."
    
    cd "$PROJECT_PATH" || exit 1
    
    BUNDLE_PATH="../yanxiao-env-monitor-$(date +%Y%m%d_%H%M%S).bundle"
    
    git bundle create "$BUNDLE_PATH" --all
    
    if [ $? -eq 0 ]; then
        log_success "Bundle创建成功: $BUNDLE_PATH"
        echo "请将Bundle文件复制到其他电脑的云盘同步目录中"
    else
        log_error "Bundle创建失败"
        return 1
    fi
}

# 应用Git Bundle
apply_bundle() {
    log_info "应用Git Bundle..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 查找Bundle文件
    BUNDLE_FILES=$(find .. -name "yanxiao-env-monitor-*.bundle" -type f)
    
    if [[ -z "$BUNDLE_FILES" ]]; then
        log_error "未找到Bundle文件"
        return 1
    fi
    
    echo "找到的Bundle文件:"
    echo "$BUNDLE_FILES" | nl
    
    read -p "请选择要应用的Bundle文件编号: " choice
    
    SELECTED_BUNDLE=$(echo "$BUNDLE_FILES" | sed -n "${choice}p")
    
    if [[ -z "$SELECTED_BUNDLE" ]]; then
        log_error "无效选择"
        return 1
    fi
    
    log_info "应用Bundle: $SELECTED_BUNDLE"
    
    # 添加Bundle作为远程仓库
    git remote add bundle "$SELECTED_BUNDLE" 2>/dev/null || true
    git fetch bundle
    
    # 获取Bundle中的分支
    BUNDLE_BRANCHES=$(git branch -r | grep bundle/)
    
    echo "Bundle中的分支:"
    echo "$BUNDLE_BRANCHES"
    
    CURRENT_BRANCH=$(get_current_branch)
    BUNDLE_BRANCH="bundle/$CURRENT_BRANCH"
    
    if git show-ref --verify --quiet "refs/remotes/$BUNDLE_BRANCH"; then
        log_info "合并分支: $BUNDLE_BRANCH"
        git merge "$BUNDLE_BRANCH"
        
        if [ $? -eq 0 ]; then
            log_success "Bundle应用成功"
        else
            log_error "合并失败，可能存在冲突"
            return 1
        fi
    else
        log_warning "Bundle中未找到对应分支: $CURRENT_BRANCH"
    fi
    
    # 清理Bundle远程
    git remote remove bundle 2>/dev/null || true
}

# 提交当前更改
commit_changes() {
    cd "$PROJECT_PATH" || exit 1
    
    if [[ -z $(git status --porcelain) ]]; then
        log_info "没有需要提交的更改"
        return 0
    fi
    
    log_info "发现未提交的更改:"
    git status --short
    
    read -p "是否要提交这些更改? (y/n): " confirm
    
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        read -p "请输入提交信息: " commit_message
        
        git add .
        git commit -m "$commit_message"
        
        if [ $? -eq 0 ]; then
            log_success "提交成功"
        else
            log_error "提交失败"
            return 1
        fi
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo "========================================"
    echo "    烟小环境监测 Git 同步工具"
    echo "========================================"
    echo "1) 检查Git状态"
    echo "2) 提交当前更改"
    echo "3) 推送到远程仓库"
    echo "4) 从远程仓库拉取"
    echo "5) 创建Git Bundle"
    echo "6) 应用Git Bundle"
    echo "7) 完整同步流程"
    echo "8) 设置远程仓库"
    echo "9) 退出"
    echo "========================================"
}

# 完整同步流程
full_sync() {
    log_info "开始完整同步流程..."
    
    # 检查Git状态
    check_git_status
    status=$?
    
    if [ $status -eq 2 ]; then
        commit_changes
    elif [ $status -eq 1 ]; then
        log_error "Git状态异常，请检查"
        return 1
    fi
    
    # 准备同步
    prepare_sync
    
    # 检查是否有远程仓库
    if git remote | grep -q origin; then
        log_info "使用远程仓库同步..."
        pull_from_remote && push_to_remote
    else
        log_info "使用Bundle方式同步..."
        create_bundle
    fi
    
    log_success "同步流程完成"
}

# 主程序
main() {
    # 检查项目路径
    if [[ ! -d "$PROJECT_PATH" ]]; then
        log_error "项目路径不存在: $PROJECT_PATH"
        exit 1
    fi
    
    while true; do
        show_menu
        read -p "请选择操作 (1-9): " choice
        
        case $choice in
            1) check_git_status ;;
            2) commit_changes ;;
            3) push_to_remote ;;
            4) pull_from_remote ;;
            5) create_bundle ;;
            6) apply_bundle ;;
            7) full_sync ;;
            8) setup_remote_repo ;;
            9) 
                log_info "退出程序"
                exit 0
                ;;
            *)
                log_error "无效选择，请重新输入"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 运行主程序
main "$@"
