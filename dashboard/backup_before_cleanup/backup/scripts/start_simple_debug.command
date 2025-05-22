#!/bin/bash
# 简易调试启动脚本 - 使用本地MQTT中继和测试数据发送器
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
echo -e "${GREEN}   烟铺小学智慧校园仪表盘 - 简易调试模式   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${YELLOW}此脚本将启动本地MQTT中继、测试数据发送器和仪表盘${NC}"
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

# MQTT服务器设置
MQTT_HOST="127.0.0.1"
MQTT_PORT="1883"
MQTT_USER="siot"
MQTT_PASS="dfrobot"

# 确保日志目录存在
mkdir -p logs

# 启动MQTT中继
echo -e "${GREEN}启动MQTT中继...${NC}"
$PYTHON_CMD mqtt_relay.py --host "$MQTT_HOST" --port "$MQTT_PORT" &
MQTT_RELAY_PID=$!
echo "MQTT中继PID: $MQTT_RELAY_PID"

# 等待MQTT中继启动
echo "等待MQTT中继启动..."
sleep 2

# 启动测试数据发送器在后台运行
echo -e "${GREEN}启动测试数据发送器...${NC}"
$PYTHON_CMD send_test_data.py --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" --local &
SENDER_PID=$!
echo "测试数据发送器PID: $SENDER_PID"

# 等待测试数据发送器启动
sleep 1

# 启动优化版本的仪表盘
echo -e "${GREEN}启动仪表盘...${NC}"
$PYTHON_CMD main_all_fixed_optimized.py

# 当仪表盘关闭时，终止数据发送器
echo -e "${YELLOW}仪表盘已关闭，终止数据发送器...${NC}"
kill $SENDER_PID 2>/dev/null || true

echo -e "${GREEN}程序运行完毕${NC}"
echo -e "${YELLOW}注意: MQTT中继仍在另一个终端窗口中运行${NC}"
echo -e "${YELLOW}请手动关闭该窗口以完全退出${NC}"

# 保持终端窗口打开，直到用户按下任意键
read -n 1 -s -r -p "按任意键退出..."
