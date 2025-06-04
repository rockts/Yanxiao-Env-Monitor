#!/bin/bash

# 生产环境部署脚本
# Deploy to Production Server: rockts@192.168.1.115

set -e

# 配置变量
PRODUCTION_SERVER="rockts@192.168.1.115"
PRODUCTION_PATH="/home/rockts/env-monitor"
LOCAL_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"

echo "🚀 开始部署到生产服务器..."

# 1. 创建生产环境目录
echo "📁 创建生产环境目录..."
ssh $PRODUCTION_SERVER "mkdir -p $PRODUCTION_PATH/{dashboard,logs,scripts}"

# 2. 上传核心文件
echo "📤 上传核心文件..."
scp "$LOCAL_PATH/dashboard/mqtt_flask_server_production.py" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"
scp "$LOCAL_PATH/dashboard/config_production.py" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"
scp "$LOCAL_PATH/dashboard/index.html" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"
scp "$LOCAL_PATH/dashboard/requirements.txt" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"

# 3. 上传脚本文件
echo "📤 上传脚本文件..."
scp "$LOCAL_PATH/dashboard/scripts/install_dependencies.sh" "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/"
scp "$LOCAL_PATH/dashboard/scripts/start_services.sh" "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/"
scp "$LOCAL_PATH/dashboard/scripts/stop_services.sh" "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/"
scp "$LOCAL_PATH/dashboard/scripts/check_status.sh" "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/"

# 4. 创建生产环境启动脚本
echo "📝 创建生产环境启动脚本..."
cat > /tmp/start_production.sh << 'EOF'
#!/bin/bash
# 生产环境启动脚本

cd /home/rockts/env-monitor/dashboard

# 检查Python环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 启动服务
echo "启动生产环境服务..."
nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &

echo "生产环境服务已启动"
echo "日志文件: /home/rockts/env-monitor/logs/production.log"
echo "访问地址: http://192.168.1.115:5052"
EOF

scp /tmp/start_production.sh "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/"
ssh $PRODUCTION_SERVER "chmod +x $PRODUCTION_PATH/scripts/start_production.sh"

# 5. 创建systemd服务文件
echo "📝 创建systemd服务文件..."
cat > /tmp/env-monitor.service << 'EOF'
[Unit]
Description=Environment Monitor Dashboard
After=network.target

[Service]
Type=simple
User=rockts
WorkingDirectory=/home/rockts/env-monitor/dashboard
Environment=PATH=/home/rockts/env-monitor/dashboard/venv/bin
ExecStart=/home/rockts/env-monitor/dashboard/venv/bin/python mqtt_flask_server_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

scp /tmp/env-monitor.service "$PRODUCTION_SERVER:/tmp/"
ssh $PRODUCTION_SERVER "sudo mv /tmp/env-monitor.service /etc/systemd/system/"

# 6. 远程安装和启动
echo "🔧 远程安装和配置..."
ssh $PRODUCTION_SERVER << 'EOF'
cd /home/rockts/env-monitor/dashboard

# 创建Python虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable env-monitor
sudo systemctl start env-monitor

# 检查服务状态
sudo systemctl status env-monitor --no-pager
EOF

# 7. 验证部署
echo "✅ 验证部署结果..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -s http://192.168.1.115:5052/api/status | grep -q "mqtt_connected"; then
    echo "✅ 服务部署成功！"
    echo "🌐 访问地址: http://192.168.1.115:5052"
    echo "📊 大屏地址: http://192.168.1.115:5052/index.html"
else
    echo "❌ 服务可能存在问题，请检查日志"
fi

# 8. 显示管理命令
echo "
🎯 生产环境管理命令:
- 查看服务状态: sudo systemctl status env-monitor
- 重启服务: sudo systemctl restart env-monitor
- 查看日志: sudo journalctl -u env-monitor -f
- 手动启动: /home/rockts/env-monitor/scripts/start_production.sh
- 检查API: curl http://192.168.1.115:5052/api/status
"

echo "🎉 部署完成！"

# 清理临时文件
rm -f /tmp/start_production.sh /tmp/env-monitor.service
