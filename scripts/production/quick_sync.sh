#!/bin/bash

# 快速同步修改到生产环境
# Quick sync changes to production environment

set -e

PRODUCTION_SERVER="rockts@192.168.1.115"
PRODUCTION_PATH="/home/rockts/env-monitor"
LOCAL_PATH="/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor"

echo "🚀 快速同步修改到生产环境..."

# 同步主要文件
echo "📤 同步主页面..."
scp "$LOCAL_PATH/dashboard/index.html" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"

echo "📤 同步调试页面..."
scp "$LOCAL_PATH/dashboard/mqtt_status_debug.html" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/" 2>/dev/null || echo "调试页面不存在，跳过"
scp "$LOCAL_PATH/dashboard/mqtt_debug.html" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/" 2>/dev/null || echo "MQTT调试页面不存在，跳过"
scp "$LOCAL_PATH/dashboard/port_detection_test.html" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/" 2>/dev/null || echo "端口检测页面不存在，跳过"

echo "📤 同步服务器代码..."
scp "$LOCAL_PATH/dashboard/mqtt_flask_server_production.py" "$PRODUCTION_SERVER:$PRODUCTION_PATH/dashboard/"

echo "📤 同步脚本..."
scp "$LOCAL_PATH/dashboard/scripts/"*.sh "$PRODUCTION_SERVER:$PRODUCTION_PATH/scripts/" 2>/dev/null || echo "脚本目录不存在，跳过"

echo "✅ 同步完成！"

# 验证
echo "🔍 验证生产环境..."
if curl -s "http://iot.lekee.cc:3000/api/status" | grep -q "mqtt_connected"; then
    echo "✅ 生产环境服务正常！"
    echo "🌐 主页面: http://iot.lekee.cc:3000/"
    echo "🔧 调试页面: http://iot.lekee.cc:3000/mqtt_status_debug.html"
else
    echo "❌ 生产环境可能存在问题"
fi

echo "📝 注意：如果修改了Python服务器代码，可能需要重启服务："
echo "   ssh $PRODUCTION_SERVER 'cd $PRODUCTION_PATH/dashboard && pkill -f mqtt_flask_server_production.py && nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &'"
