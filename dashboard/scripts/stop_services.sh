#!/bin/bash

# 烟小智慧环境监测系统 - 服务停止脚本
# Stop Services Script for Smart Environment Monitoring System

PROJECT_DIR="/Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard"

echo "🛑 停止烟小智慧环境监测系统服务..."

cd "$PROJECT_DIR"

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "📡 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在或已停止"
    fi
    rm -f .backend.pid
else
    echo "⚠️  未找到后端服务PID文件，尝试通过端口停止..."
    if lsof -i :5051 > /dev/null 2>&1; then
        PID=$(lsof -t -i:5051)
        kill $PID
        echo "✅ 后端服务已通过端口停止"
    fi
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🌐 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在或已停止"
    fi
    rm -f .frontend.pid
else
    echo "⚠️  未找到前端服务PID文件，尝试通过端口停止..."
    if lsof -i :8080 > /dev/null 2>&1; then
        PID=$(lsof -t -i:8080)
        kill $PID
        echo "✅ 前端服务已通过端口停止"
    fi
fi

# 额外清理：确保端口被释放
sleep 2

# 检查端口是否仍被占用
if lsof -i :5051 > /dev/null 2>&1; then
    echo "⚠️  端口5051仍被占用，强制停止..."
    lsof -t -i:5051 | xargs kill -9
fi

if lsof -i :8080 > /dev/null 2>&1; then
    echo "⚠️  端口8080仍被占用，强制停止..."
    lsof -t -i:8080 | xargs kill -9
fi

echo ""
echo "🎉 所有服务已停止!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 可用命令:"
echo "   重新启动: ./scripts/start_services.sh"
echo "   查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
