#!/bin/bash
# 调试启动脚本 - 同时启动仪表盘和测试数据发送器
# 作者：GitHub Copilot

# 确保脚本在正确的目录中运行
cd "$(dirname "$0")"

# 颜色设置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${GREEN}   烟铺小学智慧校园仪表盘 - 调试模式   ${NC}"
echo "--------------------------------"
echo -e "${YELLOW}此脚本将同时启动仪表盘和测试数据发送器${NC}"

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

# 检查依赖
echo "检查依赖..."
$PYTHON_CMD -c "import PIL" 2>/dev/null || { echo -e "${YELLOW}警告: 未安装Pillow库，视频显示功能将不可用。运行 'pip install pillow' 安装。${NC}"; }
$PYTHON_CMD -c "import paho.mqtt.client" 2>/dev/null || { echo -e "${RED}错误: 未安装paho-mqtt库。运行 'pip install paho-mqtt' 安装。${NC}"; exit 1; }
$PYTHON_CMD -c "import matplotlib" 2>/dev/null || { echo -e "${YELLOW}警告: 未安装matplotlib库，图表功能将不可用。运行 'pip install matplotlib' 安装。${NC}"; }

# 默认MQTT设置
DEFAULT_MQTT_HOST="127.0.0.1"
DEFAULT_MQTT_PORT="1883"
DEFAULT_MQTT_USER="siot"
DEFAULT_MQTT_PASS="dfrobot"

# 设置MQTT参数
MQTT_HOST="$DEFAULT_MQTT_HOST"
MQTT_PORT="$DEFAULT_MQTT_PORT"
MQTT_USER="$DEFAULT_MQTT_USER"
MQTT_PASS="$DEFAULT_MQTT_PASS"

# 解析命令行参数
while [ $# -gt 0 ]; do
    case "$1" in
        --mqtt-host)
            MQTT_HOST="$2"
            shift 2
            ;;
        --mqtt-port)
            MQTT_PORT="$2"
            shift 2
            ;;
        --mqtt-user)
            MQTT_USER="$2"
            shift 2
            ;;
        --mqtt-pass)
            MQTT_PASS="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            shift
            ;;
    esac
done

# 确保日志目录存在
mkdir -p logs

# 启动测试数据发送器在后台运行
echo -e "${GREEN}启动测试数据发送器...${NC}"
$PYTHON_CMD send_test_data.py --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" &
SENDER_PID=$!
echo "测试数据发送器PID: $SENDER_PID"

# 启动优化版本的仪表盘
echo -e "${GREEN}启动仪表盘优化版...${NC}"
$PYTHON_CMD main_all_fixed_optimized.py

# 当仪表盘关闭时，终止测试数据发送器
echo -e "${YELLOW}仪表盘已关闭，终止测试数据发送器...${NC}"
kill $SENDER_PID 2>/dev/null || true

echo -e "${GREEN}程序运行完毕${NC}"

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
