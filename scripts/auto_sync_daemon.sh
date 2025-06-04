#!/bin/bash

# 自动同步守护进程
# 用于定时自动执行Git同步（可选功能）

# 配置
PROJECT_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"
SYNC_INTERVAL=1800  # 30分钟同步一次（秒）
LOG_FILE="$PROJECT_PATH/logs/auto_sync.log"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 日志函数
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否有更改需要同步
has_changes() {
    cd "$PROJECT_PATH" || return 1
    [[ -n $(git status --porcelain) ]]
}

# 执行自动同步
auto_sync() {
    cd "$PROJECT_PATH" || return 1
    
    if has_changes; then
        log_with_timestamp "检测到文件更改，开始自动同步..."
        
        # 执行快速同步
        if ./scripts/quick_sync.sh "自动同步 - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1; then
            log_with_timestamp "自动同步成功完成"
        else
            log_with_timestamp "自动同步失败，请手动检查"
        fi
    else
        log_with_timestamp "没有检测到更改，跳过同步"
    fi
}

# 创建PID文件
PID_FILE="$PROJECT_PATH/logs/auto_sync.pid"
echo $$ > "$PID_FILE"

# 主循环
main() {
    log_with_timestamp "启动自动同步守护进程 (PID: $$)"
    log_with_timestamp "同步间隔: ${SYNC_INTERVAL}秒"
    log_with_timestamp "项目路径: $PROJECT_PATH"
    
    while true; do
        auto_sync
        sleep "$SYNC_INTERVAL"
    done
}

# 清理函数
cleanup() {
    log_with_timestamp "正在停止自动同步守护进程..."
    rm -f "$PID_FILE"
    exit 0
}

# 设置信号处理
trap cleanup SIGTERM SIGINT

# 检查是否已经运行
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "自动同步守护进程已在运行 (PID: $OLD_PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 运行主程序
main
