#!/bin/bash

# 烟小智慧环境监测系统 - 服务状态检查脚本
# Service Status Check Script for Smart Environment Monitoring System

PROJECT_DIR="/Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard"

echo "🔍 检查烟小智慧环境监测系统服务状态..."
echo ""

# 检查后端服务状态
echo "📡 后端服务状态 (端口5051):"
if lsof -i :5051 > /dev/null 2>&1; then
    PID=$(lsof -t -i:5051)
    echo "   ✅ 运行中 (PID: $PID)"
    
    # 检查API响应
    if curl -s http://localhost:5052/api/status > /dev/null; then
        echo "   ✅ API响应正常"
        # 获取API状态详情
        STATUS=$(curl -s http://localhost:5052/api/status)
        echo "   📊 状态详情: $STATUS"
    else
        echo "   ❌ API响应异常"
    fi
else
    echo "   ❌ 未运行"
fi

echo ""

# 检查前端服务状态
echo "🌐 前端服务状态 (端口8080):"
if lsof -i :8080 > /dev/null 2>&1; then
    PID=$(lsof -t -i:8080)
    echo "   ✅ 运行中 (PID: $PID)"
    
    # 检查HTTP响应
    if curl -s http://localhost:8080 > /dev/null; then
        echo "   ✅ HTTP响应正常"
    else
        echo "   ❌ HTTP响应异常"
    fi
else
    echo "   ❌ 未运行"
fi

echo ""

# 检查进程文件
echo "📋 进程文件状态:"
if [ -f "$PROJECT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_DIR/.backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "   ✅ 后端PID文件有效 ($BACKEND_PID)"
    else
        echo "   ⚠️  后端PID文件存在但进程已停止 ($BACKEND_PID)"
    fi
else
    echo "   ⚠️  后端PID文件不存在"
fi

if [ -f "$PROJECT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_DIR/.frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "   ✅ 前端PID文件有效 ($FRONTEND_PID)"
    else
        echo "   ⚠️  前端PID文件存在但进程已停止 ($FRONTEND_PID)"
    fi
else
    echo "   ⚠️  前端PID文件不存在"
fi

echo ""

# 检查日志文件
echo "📄 日志文件状态:"
if [ -f "$PROJECT_DIR/logs/backend.log" ]; then
    BACKEND_LOG_SIZE=$(wc -l < "$PROJECT_DIR/logs/backend.log")
    echo "   📡 后端日志: $BACKEND_LOG_SIZE 行"
    echo "   📡 最近日志: $(tail -1 "$PROJECT_DIR/logs/backend.log" 2>/dev/null || echo '无内容')"
else
    echo "   ⚠️  后端日志文件不存在"
fi

if [ -f "$PROJECT_DIR/logs/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(wc -l < "$PROJECT_DIR/logs/frontend.log")
    echo "   🌐 前端日志: $FRONTEND_LOG_SIZE 行"
    echo "   🌐 最近日志: $(tail -1 "$PROJECT_DIR/logs/frontend.log" 2>/dev/null || echo '无内容')"
else
    echo "   ⚠️  前端日志文件不存在"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 访问地址:"
echo "   前端: http://localhost:8080/index.html"
echo "   API:  http://localhost:5052/api/status"
echo ""
echo "📋 管理命令:"
echo "   启动: ./scripts/start_services.sh"
echo "   停止: ./scripts/stop_services.sh"
echo "   日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
