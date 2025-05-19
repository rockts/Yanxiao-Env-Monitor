#!/bin/bash

# 改进的带测试数据的启动脚本
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/test_script_$(date +%Y%m%d_%H%M%S).log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"
echo "====== 智慧校园仪表盘测试环境 ======" 
echo "启动时间: $(date)" 
echo "工作目录: $SCRIPT_DIR" 
echo "" 

# 启动MQTT代理
echo "1. 启动MQTT代理服务器..." 
cd "$SCRIPT_DIR/src"
python3 simple_mqtt_broker.py &
BROKER_PID=$!
echo "   MQTT代理进程ID: $BROKER_PID" 

# 等待MQTT代理启动
echo "   等待MQTT代理启动..." 
sleep 2

# 检查MQTT代理是否运行
if ! ps -p $BROKER_PID > /dev/null; then
    echo "ERROR: MQTT代理启动失败！" 
    exit 1
fi
echo "   MQTT代理已成功启动" 

# 启动传感器测试数据
echo "2. 启动传感器测试数据发送程序..." 
python3 send_test_data.py --local &
DATA_PID=$!
echo "   传感器数据进程ID: $DATA_PID" 

# 启动视频测试数据
echo "3. 启动视频测试数据发送程序..." 
python3 send_video_test.py --fps 3 &
VIDEO_PID=$!
echo "   视频数据进程ID: $VIDEO_PID" 

# 等待所有测试数据程序启动
echo "   等待测试数据程序初始化..." 
sleep 2

echo "4. 启动智慧校园仪表盘主程序..." 
python3 main.py

echo "5. 清理测试环境..." 
# 正常关闭所有进程
kill $BROKER_PID $DATA_PID $VIDEO_PID 2>/dev/null

echo "测试运行结束，时间: $(date)" 
