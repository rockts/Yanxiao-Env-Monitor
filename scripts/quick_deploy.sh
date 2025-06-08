#!/bin/bash
# 快速部署脚本 - 避免8080端口冲突
# Quick Deploy Script - Avoiding port 8080 conflict

set -e

SERVER="192.168.1.115"
USER="rockts"
REMOTE_PATH="/home/rockts/env-monitor"

echo "🚀 快速部署环境监测系统到生产服务器..."
echo "服务器: $USER@$SERVER"
echo "远程路径: $REMOTE_PATH"
echo "服务端口: 5052 (避免与SIOT 8080端口冲突)"
echo ""

# 1. 检查服务器连接
echo "🔗 检查服务器连接..."
if ! ssh -o ConnectTimeout=10 $USER@$SERVER "echo '服务器连接成功'"; then
    echo "❌ 无法连接到服务器，请检查网络连接"
    exit 1
fi

# 2. 停止现有服务（如果存在）
echo "🛑 停止现有服务..."
ssh $USER@$SERVER "pkill -f mqtt_flask_server_production.py || true"

# 3. 创建目录结构
echo "📁 创建目录结构..."
ssh $USER@$SERVER "mkdir -p $REMOTE_PATH/{dashboard,logs,scripts}"

# 4. 上传核心文件
echo "📤 上传应用文件..."
scp dashboard/mqtt_flask_server_production.py $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/config_production.py $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/index.html $USER@$SERVER:$REMOTE_PATH/dashboard/
scp dashboard/requirements.txt $USER@$SERVER:$REMOTE_PATH/dashboard/

# 5. 上传管理脚本
echo "📤 上传管理脚本..."
scp dashboard/scripts/*.sh $USER@$SERVER:$REMOTE_PATH/scripts/ 2>/dev/null || echo "脚本文件不存在，跳过..."

# 6. 在服务器上执行部署
echo "🔧 在服务器上执行部署..."
ssh $USER@$SERVER << 'REMOTE_SCRIPT'
cd /home/rockts/env-monitor/dashboard

# 创建Python虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "安装依赖包..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 检查端口使用情况
echo "检查端口使用情况..."
if netstat -tlnp | grep ":8080 "; then
    echo "⚠️  端口8080已被占用（可能是SIOT）"
fi

if netstat -tlnp | grep ":5052 "; then
    echo "⚠️  端口5052已被占用，将终止占用进程..."
    pkill -f ":5052" || true
    sleep 2
fi

echo "🚀 启动环境监测服务..."
nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务状态
if ps aux | grep mqtt_flask_server_production.py | grep -v grep; then
    echo "✅ 服务启动成功！"
    echo "📊 服务运行在端口 5052"
    echo "📝 日志文件：../logs/production.log"
else
    echo "❌ 服务启动失败，请检查日志："
    tail -n 20 ../logs/production.log
fi
REMOTE_SCRIPT

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 服务信息："
echo "  - 服务地址：http://$SERVER:5052"
echo "  - 日志查看：ssh $USER@$SERVER 'tail -f $REMOTE_PATH/logs/production.log'"
echo "  - 服务管理："
echo "    启动：ssh $USER@$SERVER 'cd $REMOTE_PATH/dashboard && source venv/bin/activate && nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &'"
echo "    停止：ssh $USER@$SERVER 'pkill -f mqtt_flask_server_production.py'"
echo "    状态：ssh $USER@$SERVER 'ps aux | grep mqtt_flask_server_production'"
echo ""
echo "💡 提示：SIOT服务继续在8080端口运行，环境监测系统在5052端口运行"
