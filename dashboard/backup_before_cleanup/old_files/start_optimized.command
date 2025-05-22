#!/bin/bash
# 优化版仪表盘启动脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查并安装依赖项
echo "检查依赖项..."
python3 -c "import paho.mqtt.client" >/dev/null 2>&1 || pip3 install paho-mqtt
python3 -c "import matplotlib" >/dev/null 2>&1 || pip3 install matplotlib
python3 -c "import PIL" >/dev/null 2>&1 || pip3 install Pillow
python3 -c "import requests" >/dev/null 2>&1 || pip3 install requests

# 如果MQTT代理未在运行，则启动本地MQTT代理
echo "检查MQTT代理状态..."
(nc -z -w1 127.0.0.1 1883 && echo "MQTT代理已在运行") || (
    echo "正在启动本地MQTT代理..."
    python3 simple_mqtt_broker.py &
    sleep 2
)

# 检查测试数据发送器是否应该启动
read -p "是否要启动测试数据发送器？(y/n): " START_TEST_DATA
if [[ "$START_TEST_DATA" == "y" || "$START_TEST_DATA" == "Y" ]]; then
    echo "启动测试数据发送器..."
    python3 send_test_data.py --local &
fi

# 启动优化后的仪表盘程序
echo "启动智慧校园环境监测仪表盘 (优化版)..."
python3 main_all_fixed_optimized.py

# 清理后台进程
echo "清理后台进程..."
pkill -f "python3 simple_mqtt_broker.py"
pkill -f "python3 send_test_data.py"
echo "清理完成。"
