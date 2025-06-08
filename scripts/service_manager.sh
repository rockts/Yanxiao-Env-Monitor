#!/bin/bash
# 环境监测服务管理脚本
# Environment Monitoring Service Manager

SERVER="192.168.1.115"
USER="rockts"
REMOTE_PATH="/home/rockts/env-monitor"
SERVICE_NAME="mqtt_flask_server_production.py"

show_usage() {
    echo "使用方法: $0 {start|stop|restart|status|logs|deploy}"
    echo ""
    echo "命令说明:"
    echo "  start   - 启动环境监测服务"
    echo "  stop    - 停止环境监测服务"
    echo "  restart - 重启环境监测服务"
    echo "  status  - 查看服务状态"
    echo "  logs    - 查看服务日志"
    echo "  deploy  - 部署并启动服务"
    echo ""
    echo "服务信息:"
    echo "  服务器: $USER@$SERVER"
    echo "  端口: 5052 (避免与SIOT 8080端口冲突)"
    echo "  日志: $REMOTE_PATH/logs/production.log"
}

start_service() {
    echo "🚀 启动环境监测服务..."
    ssh $USER@$SERVER "cd $REMOTE_PATH/dashboard && source venv/bin/activate && nohup python $SERVICE_NAME > ../logs/production.log 2>&1 &"
    sleep 3
    check_status
}

stop_service() {
    echo "🛑 停止环境监测服务..."
    ssh $USER@$SERVER "pkill -f $SERVICE_NAME"
    echo "✅ 服务已停止"
}

restart_service() {
    echo "🔄 重启环境监测服务..."
    stop_service
    sleep 2
    start_service
}

check_status() {
    echo "📊 检查服务状态..."
    
    # 检查进程
    if ssh $USER@$SERVER "ps aux | grep $SERVICE_NAME | grep -v grep" > /dev/null; then
        echo "✅ 服务进程正在运行"
        ssh $USER@$SERVER "ps aux | grep $SERVICE_NAME | grep -v grep"
    else
        echo "❌ 服务进程未运行"
    fi
    
    # 检查端口
    echo ""
    echo "🔌 检查端口状态..."
    if curl -s -I http://$SERVER:5052/health | grep "200 OK" > /dev/null; then
        echo "✅ 端口5052可访问"
        echo "🌐 服务地址: http://$SERVER:5052"
    else
        echo "❌ 端口5052不可访问"
    fi
    
    # 检查SIOT端口
    if curl -s -I http://$SERVER:8080 > /dev/null; then
        echo "✅ SIOT服务运行正常 (端口8080)"
    else
        echo "⚠️  SIOT服务可能未运行 (端口8080)"
    fi
}

show_logs() {
    echo "📝 显示服务日志 (最近20行)..."
    ssh $USER@$SERVER "tail -n 20 $REMOTE_PATH/logs/production.log"
    echo ""
    echo "💡 实时查看日志: ssh $USER@$SERVER 'tail -f $REMOTE_PATH/logs/production.log'"
}

deploy_service() {
    echo "📦 部署环境监测服务..."
    
    # 上传文件
    echo "📤 上传文件..."
    ./upload_files.sh
    
    # 重启服务
    echo "🔄 重启服务..."
    restart_service
    
    echo "🎉 部署完成！"
}

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    deploy)
        deploy_service
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0