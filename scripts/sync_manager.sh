#!/bin/bash

# 自动同步管理器
# 用于启动、停止、查看自动同步守护进程状态

PROJECT_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"
PID_FILE="$PROJECT_PATH/logs/auto_sync.pid"
LOG_FILE="$PROJECT_PATH/logs/auto_sync.log"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查守护进程状态
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}✓ 自动同步守护进程正在运行${NC} (PID: $PID)"
            return 0
        else
            echo -e "${RED}✗ PID文件存在但进程已停止${NC}"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${YELLOW}○ 自动同步守护进程未运行${NC}"
        return 1
    fi
}

# 启动守护进程
start_daemon() {
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}自动同步守护进程已在运行${NC}"
        return 1
    fi
    
    echo -e "${BLUE}启动自动同步守护进程...${NC}"
    nohup "$PROJECT_PATH/scripts/auto_sync_daemon.sh" > /dev/null 2>&1 &
    
    sleep 2
    
    if check_status > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 自动同步守护进程启动成功${NC}"
    else
        echo -e "${RED}✗ 自动同步守护进程启动失败${NC}"
        return 1
    fi
}

# 停止守护进程
stop_daemon() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${BLUE}停止自动同步守护进程...${NC}"
            kill "$PID"
            
            # 等待进程结束
            for i in {1..10}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}强制终止进程...${NC}"
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            echo -e "${GREEN}✓ 自动同步守护进程已停止${NC}"
        else
            rm -f "$PID_FILE"
            echo -e "${YELLOW}进程已停止，清理PID文件${NC}"
        fi
    else
        echo -e "${YELLOW}自动同步守护进程未运行${NC}"
    fi
}

# 重启守护进程
restart_daemon() {
    stop_daemon
    sleep 2
    start_daemon
}

# 查看日志
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${BLUE}=== 最近20条同步日志 ===${NC}"
        tail -20 "$LOG_FILE"
    else
        echo -e "${YELLOW}暂无同步日志${NC}"
    fi
}

# 实时监控日志
monitor_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${BLUE}=== 实时同步日志监控 (Ctrl+C退出) ===${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}暂无同步日志文件${NC}"
    fi
}

# 显示菜单
show_menu() {
    echo ""
    echo "========================================"
    echo "    自动同步管理器"
    echo "========================================"
    echo "1) 查看状态"
    echo "2) 启动自动同步"
    echo "3) 停止自动同步"
    echo "4) 重启自动同步"
    echo "5) 查看同步日志"
    echo "6) 实时监控日志"
    echo "7) 清理日志文件"
    echo "8) 退出"
    echo "========================================"
}

# 清理日志
clean_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        > "$LOG_FILE"
        echo -e "${GREEN}✓ 同步日志已清理${NC}"
    else
        echo -e "${YELLOW}没有日志文件需要清理${NC}"
    fi
}

# 主程序
main() {
    # 创建必要目录
    mkdir -p "$(dirname "$PID_FILE")"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # 如果有命令行参数，直接执行
    case "$1" in
        "start")
            start_daemon
            exit $?
            ;;
        "stop")
            stop_daemon
            exit $?
            ;;
        "restart")
            restart_daemon
            exit $?
            ;;
        "status")
            check_status
            exit $?
            ;;
        "logs")
            show_logs
            exit 0
            ;;
        "monitor")
            monitor_logs
            exit 0
            ;;
    esac
    
    # 交互模式
    while true; do
        show_menu
        read -p "请选择操作 (1-8): " choice
        
        case $choice in
            1) check_status ;;
            2) start_daemon ;;
            3) stop_daemon ;;
            4) restart_daemon ;;
            5) show_logs ;;
            6) monitor_logs ;;
            7) clean_logs ;;
            8) 
                echo -e "${BLUE}退出管理器${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重新输入${NC}"
                ;;
        esac
        
        if [[ "$choice" != "6" ]]; then
            echo ""
            read -p "按回车键继续..."
        fi
    done
}

main "$@"
