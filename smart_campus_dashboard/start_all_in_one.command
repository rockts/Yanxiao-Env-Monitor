#!/bin/bash
# 智慧校园仪表盘一体化启动脚本
# 同时启动mosquitto代理、测试数据发送器和仪表盘应用
# 作者：GitHub Copilot

# 确保脚本在正确的目录中运行
cd "$(dirname "$0")"

# 颜色设置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}   烟铺小学智慧校园仪表盘 - 一体化启动   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 检查Python版本
echo "检查Python版本..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
    echo "使用 python3 命令"
elif command -v python &>/dev/null; then
    # 检查python命令的版本
    PY_VER=$(python --version 2>&1 | awk '{print $2}' | cut -d'.' -f1)
    if [ "$PY_VER" -ge 3 ]; then
        PYTHON_CMD=python
        echo "使用 python 命令 (Python $PY_VER)"
    else
        echo -e "${RED}未找到Python 3。请安装Python 3.6+${NC}"
        exit 1
    fi
else
    echo -e "${RED}未找到Python。请安装Python 3.6+${NC}"
    exit 1
fi

# 检查必要依赖
echo "检查依赖..."
$PYTHON_CMD -c "import PIL" 2>/dev/null || { echo -e "${YELLOW}警告: 未安装Pillow库，视频显示功能将不可用。正在安装...${NC}"; $PYTHON_CMD -m pip install pillow; }
$PYTHON_CMD -c "import paho.mqtt.client" 2>/dev/null || { echo -e "${YELLOW}警告: 未安装paho-mqtt库。正在安装...${NC}"; $PYTHON_CMD -m pip install paho-mqtt; }
$PYTHON_CMD -c "import matplotlib" 2>/dev/null || { echo -e "${YELLOW}警告: 未安装matplotlib库，图表功能将不可用。正在安装...${NC}"; $PYTHON_CMD -m pip install matplotlib; }

# MQTT设置
MQTT_HOST="127.0.0.1"
MQTT_PORT="1883"
MQTT_USER="siot"
MQTT_PASS="dfrobot"

# 确保日志目录存在
mkdir -p logs

# 检查并启动MQTT代理
echo -e "${GREEN}检查MQTT代理...${NC}"
if command -v mosquitto &>/dev/null; then
    echo "找到mosquitto命令，将启动本地MQTT代理"
    
    # 创建临时配置文件
    echo "listener 1883" > mosquitto_temp.conf
    echo "allow_anonymous true" >> mosquitto_temp.conf
    
    # 启动mosquitto
    echo "启动mosquitto MQTT代理..."
    mosquitto -c mosquitto_temp.conf &
    MQTT_BROKER_PID=$!
    echo "MQTT代理PID: $MQTT_BROKER_PID"
    
    # 给代理一点时间启动
    sleep 1
else
    echo -e "${YELLOW}未找到mosquitto，将使用Python MQTT桥接器...${NC}"
    
    # 检查mqtt_bridge.py是否存在
    if [ -f "mqtt_bridge.py" ]; then
        echo "启动MQTT桥接器..."
        $PYTHON_CMD mqtt_bridge.py --host "$MQTT_HOST" --port "$MQTT_PORT" &
        MQTT_BROKER_PID=$!
        echo "MQTT桥接器PID: $MQTT_BROKER_PID"
        
        # 给桥接器一点时间启动
        sleep 2
    else
        echo -e "${RED}未找到mqtt_bridge.py，将使用mqtt_relay.py...${NC}"
        
        # 启动MQTT中继
        echo "启动MQTT中继..."
        $PYTHON_CMD mqtt_relay.py --host "$MQTT_HOST" --port "$MQTT_PORT" &
        MQTT_BROKER_PID=$!
        echo "MQTT中继PID: $MQTT_BROKER_PID"
        
        # 等待MQTT中继启动
        sleep 2
    fi
fi

# 启动测试数据发送器在后台运行
echo -e "${GREEN}启动测试数据发送器...${NC}"
$PYTHON_CMD send_test_data.py --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" --local &
SENDER_PID=$!
echo "测试数据发送器PID: $SENDER_PID"

# 等待测试数据发送器启动
sleep 1

# 启动仪表盘
echo -e "${GREEN}启动智慧校园仪表盘...${NC}"
$PYTHON_CMD main_all_fixed_optimized.py

# 当仪表盘关闭时，终止其他进程
echo -e "${YELLOW}仪表盘已关闭，终止所有相关进程...${NC}"
kill $SENDER_PID 2>/dev/null || true
kill $MQTT_BROKER_PID 2>/dev/null || true

# 清理临时文件
if [ -f "mosquitto_temp.conf" ]; then
    rm mosquitto_temp.conf
fi

echo -e "${GREEN}所有进程已终止${NC}"

# 询问用户是否查看日志
read -p "是否查看最新的日志文件? (y/n): " VIEW_LOG
if [ "$VIEW_LOG" = "y" ] || [ "$VIEW_LOG" = "Y" ]; then
    LATEST_LOG=$(ls -t logs/dashboard_*.log | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${GREEN}显示日志: $LATEST_LOG${NC}"
        cat "$LATEST_LOG"
    else
        echo -e "${RED}未找到日志文件${NC}"
    fi
fi

# 保持终端窗口打开，直到用户按下任意键
read -n 1 -s -r -p "按任意键退出..."