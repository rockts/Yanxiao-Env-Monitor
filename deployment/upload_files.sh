#!/bin/bash

set -e  # 一出错自动退出

SERVER="192.168.1.115"
USER="rockts"
REMOTE_PATH="/home/rockts/env-monitor"

echo "🚀 准备上传文件到生产服务器..."
echo "服务器: $USER@$SERVER"
echo "远程路径: $REMOTE_PATH"
echo ""

# 1. 确保远程目录都已创建
ssh $USER@$SERVER "mkdir -p $REMOTE_PATH/dashboard $REMOTE_PATH/scripts"

# 2. 上传核心文件
echo "📤 上传dashboard文件..."
scp dashboard/mqtt_flask_server_production.py $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/config_production.py $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/index.html $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/requirements.txt $USER@$SERVER:$REMOTE_PATH/dashboard/

# 3. 上传脚本文件
echo "📤 上传脚本文件..."
scp dashboard/scripts/*.sh $USER@$SERVER:$REMOTE_PATH/scripts/ || true  # 若无sh文件不报错

echo "✅ 文件上传完成!"
echo ""
echo "🔧 接下来请手动登录服务器执行安装:"
echo "ssh $USER@$SERVER"
echo "cd $REMOTE_PATH/dashboard"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo ""
echo "📝 注意: 生产环境使用端口5052 (避免与SIOT的8080端口冲突)"
echo "🚀 启动服务:"
echo "nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &"
echo ""
echo "📊 检查服务状态:"
echo "tail -f ../logs/production.log"
echo "ps aux | grep mqtt_flask_server_production"
echo "netstat -tlnp | grep 5052"
