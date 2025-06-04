#!/bin/bash

# 烟小智慧环境监测系统 - 服务启动脚本
# Start Services Script for Smart Environment Monitoring System

PROJECT_DIR="/Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard"

echo "🚀 启动烟小智慧环境监测系统服务..."

# 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 错误: 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "env" ]; then
    echo "❌ 错误: Python虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  警告: 端口 $port 已被占用，尝试停止占用进程..."
        local pid=$(lsof -t -i:$port)
        if [ ! -z "$pid" ]; then
            kill $pid
            sleep 2
        fi
    fi
}

# 检查并清理端口
check_port 5051
check_port 8080

# 启动后端服务
echo "📡 启动后端服务 (Flask Server)..."
source env/bin/activate
nohup python3 mqtt_flask_server.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动，PID: $BACKEND_PID"

# 等待后端服务启动
sleep 3

# 检查后端服务是否正常运行
if curl -s http://localhost:5051/api/status > /dev/null; then
    echo "✅ 后端服务启动成功 - http://localhost:5051"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 启动前端服务
echo "🌐 启动前端服务 (HTTP Server)..."
nohup python3 -m http.server 8080 --bind 0.0.0.0 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动，PID: $FRONTEND_PID"

# 等待前端服务启动
sleep 2

# 检查前端服务是否正常运行
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ 前端服务启动成功 - http://localhost:8080"
else
    echo "❌ 前端服务启动失败"
fi

# 保存进程ID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 服务启动完成!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 前端访问地址:"
echo "   本地访问: http://localhost:8080/index.html"
echo "   局域网访问: http://$(ipconfig getifaddr en0):8080/index.html"
echo ""
echo "🔧 后端API地址:"
echo "   状态检查: http://localhost:5051/api/status"
echo "   数据接口: http://localhost:5051/api/data"
echo ""
echo "📋 管理命令:"
echo "   停止服务: ./scripts/stop_services.sh"
echo "   查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
