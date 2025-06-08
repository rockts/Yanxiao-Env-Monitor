#!/bin/bash

# 烟小环境监测系统 - 监控管理脚本
# Monitoring Management Script for Environment Monitoring System

PROJECT_DIR="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"
MONITOR_PID_FILE="$PROJECT_DIR/logs/monitor_daemon.pid"
LOG_DIR="$PROJECT_DIR/logs"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查监控守护进程状态
check_monitor_status() {
    if [[ -f "$MONITOR_PID_FILE" ]]; then
        PID=$(cat "$MONITOR_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo_success "监控守护进程正在运行 (PID: $PID)"
            return 0
        else
            echo_warning "PID文件存在但进程已停止 (PID: $PID)"
            rm -f "$MONITOR_PID_FILE"
            return 1
        fi
    else
        echo_info "监控守护进程未运行"
        return 1
    fi
}

# 启动监控守护进程
start_monitor() {
    if check_monitor_status > /dev/null 2>&1; then
        echo_warning "监控守护进程已在运行"
        return 1
    fi
    
    local interval=${1:-300}
    echo_info "启动监控守护进程 (检查间隔: ${interval}秒)..."
    
    cd "$PROJECT_DIR"
    nohup python3 monitoring_daemon.py start "$interval" > "$LOG_DIR/monitor_daemon.log" 2>&1 &
    echo $! > "$MONITOR_PID_FILE"
    
    sleep 2
    
    if check_monitor_status > /dev/null 2>&1; then
        echo_success "监控守护进程启动成功"
        echo_info "日志文件: $LOG_DIR/monitor_daemon.log"
        echo_info "监控日志: $LOG_DIR/production_monitor.log"
    else
        echo_error "监控守护进程启动失败"
        return 1
    fi
}

# 停止监控守护进程
stop_monitor() {
    if [[ -f "$MONITOR_PID_FILE" ]]; then
        PID=$(cat "$MONITOR_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo_info "停止监控守护进程 (PID: $PID)..."
            kill "$PID"
            
            # 等待进程结束
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            if ps -p "$PID" > /dev/null 2>&1; then
                echo_warning "强制终止进程..."
                kill -9 "$PID"
            fi
            
            rm -f "$MONITOR_PID_FILE"
            echo_success "监控守护进程已停止"
        else
            echo_warning "进程已停止，清理PID文件"
            rm -f "$MONITOR_PID_FILE"
        fi
    else
        echo_info "监控守护进程未运行"
    fi
}

# 重启监控守护进程
restart_monitor() {
    echo_info "重启监控守护进程..."
    stop_monitor
    sleep 2
    start_monitor "$1"
}

# 快速健康检查
quick_check() {
    echo_info "执行快速健康检查..."
    cd "$PROJECT_DIR"
    python3 production_health_check.py quick
}

# 完整健康检查
full_check() {
    echo_info "执行完整健康检查..."
    cd "$PROJECT_DIR"
    python3 production_health_check.py
}

# 查看监控日志
view_logs() {
    local log_type=${1:-monitor}
    
    case $log_type in
        "monitor")
            echo_info "查看监控日志..."
            if [[ -f "$LOG_DIR/production_monitor.log" ]]; then
                tail -f "$LOG_DIR/production_monitor.log"
            else
                echo_warning "监控日志文件不存在"
            fi
            ;;
        "daemon")
            echo_info "查看守护进程日志..."
            if [[ -f "$LOG_DIR/monitor_daemon.log" ]]; then
                tail -f "$LOG_DIR/monitor_daemon.log"
            else
                echo_warning "守护进程日志文件不存在"
            fi
            ;;
        "production")
            echo_info "查看生产服务器日志..."
            ssh rockts@192.168.1.115 "tail -f /home/rockts/env-monitor/logs/production.log"
            ;;
        *)
            echo_error "未知日志类型: $log_type"
            echo_info "可用选项: monitor, daemon, production"
            ;;
    esac
}

# 生成监控报告
generate_report() {
    echo_info "生成监控报告..."
    cd "$PROJECT_DIR"
    python3 monitoring_daemon.py report
}

# 查看系统状态
show_status() {
    printf '=%.0s' {1..60}
    echo ""
    echo "🏥 烟小环境监测系统 - 监控状态"
    printf '=%.0s' {1..60}
    echo ""
    
    # 监控守护进程状态
    echo_info "监控守护进程状态:"
    check_monitor_status
    
    echo ""
    
    # 快速检查生产服务器
    echo_info "生产服务器快速检查:"
    quick_check
    
    echo ""
    
    # 日志文件状态
    echo_info "日志文件状态:"
    if [[ -f "$LOG_DIR/production_monitor.log" ]]; then
        lines=$(wc -l < "$LOG_DIR/production_monitor.log")
        last_line=$(tail -1 "$LOG_DIR/production_monitor.log" 2>/dev/null || echo "无内容")
        echo "   📄 监控日志: $lines 行"
        echo "   📝 最新记录: $last_line"
    else
        echo "   ⚠️  监控日志文件不存在"
    fi
    
    if [[ -f "$LOG_DIR/monitor_daemon.log" ]]; then
        lines=$(wc -l < "$LOG_DIR/monitor_daemon.log")
        echo "   📄 守护进程日志: $lines 行"
    else
        echo "   ⚠️  守护进程日志文件不存在"
    fi
    
    echo ""
    printf '=%.0s' {1..60}
    echo ""
}

# 显示帮助信息
show_help() {
    cat << EOF
🏥 烟小环境监测系统 - 监控管理工具

使用方法:
  $0 <命令> [参数]

可用命令:
  status                     显示系统状态
  start [interval]          启动监控守护进程 (默认300秒间隔)
  stop                      停止监控守护进程
  restart [interval]        重启监控守护进程
  check                     完整健康检查
  quick                     快速健康检查
  logs [type]              查看日志 (monitor/daemon/production)
  report                    生成监控报告
  help                      显示此帮助信息

示例:
  $0 start 180             每3分钟检查一次
  $0 logs monitor          查看监控日志
  $0 logs production       查看生产服务器日志
  $0 restart 600           重启守护进程，10分钟检查一次

文件位置:
  监控日志: $LOG_DIR/production_monitor.log
  守护进程日志: $LOG_DIR/monitor_daemon.log
  PID文件: $MONITOR_PID_FILE

EOF
}

# 主程序
main() {
    # 确保日志目录存在
    mkdir -p "$LOG_DIR"
    
    # 检查Python脚本是否存在
    if [[ ! -f "$PROJECT_DIR/production_health_check.py" ]]; then
        echo_error "找不到 production_health_check.py"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_DIR/monitoring_daemon.py" ]]; then
        echo_error "找不到 monitoring_daemon.py"  
        exit 1
    fi
    
    case "${1:-help}" in
        "status")
            show_status
            ;;
        "start")
            start_monitor "$2"
            ;;
        "stop")
            stop_monitor
            ;;
        "restart")
            restart_monitor "$2"
            ;;
        "check")
            full_check
            ;;
        "quick")
            quick_check
            ;;
        "logs")
            view_logs "$2"
            ;;
        "report")
            generate_report
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo_error "未知命令: $1"
            echo_info "使用 '$0 help' 查看可用命令"
            exit 1
            ;;
    esac
}

# 运行主程序
main "$@"
