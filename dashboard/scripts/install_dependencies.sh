#!/bin/bash

# 烟小智慧环境监测系统 - 依赖安装脚本
# Dependencies Installation Script for Smart Environment Monitoring System

PROJECT_DIR="/Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard"

echo "📦 安装烟小智慧环境监测系统依赖..."

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

cd "$PROJECT_DIR"

# 创建虚拟环境（如果不存在）
if [ ! -d "env" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv env
    if [ $? -eq 0 ]; then
        echo "✅ 虚拟环境创建成功"
    else
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source env/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "⚠️  未找到requirements.txt，手动安装核心依赖..."
    pip install flask flask-cors paho-mqtt requests markdown
fi

# 创建日志目录
if [ ! -d "logs" ]; then
    echo "📁 创建日志目录..."
    mkdir logs
fi

# 设置脚本执行权限
echo "🔑 设置脚本执行权限..."
chmod +x scripts/*.sh

echo ""
echo "🎉 安装完成!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 下一步:"
echo "   启动服务: ./scripts/start_services.sh"
echo "   或手动启动："
echo "   1. source env/bin/activate"
echo "   2. python3 mqtt_flask_server.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
