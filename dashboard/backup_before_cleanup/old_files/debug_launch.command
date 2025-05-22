#!/bin/bash
# 调试版本的启动脚本，提供更详细的错误输出

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色设置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统（调试模式）   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 环境诊断信息
echo -e "${BLUE}系统诊断信息:${NC}"
echo -e "${YELLOW}操作系统:${NC} $(uname -a)"
echo -e "${YELLOW}Python版本:${NC} $(python3 --version)"
echo -e "${YELLOW}工作目录:${NC} $(pwd)"
echo

# 检查Python和必要的库
echo -e "${BLUE}检查Python库:${NC}"
REQUIRED_PACKAGES=("tkinter" "paho.mqtt" "pillow" "matplotlib" "json" "base64" "io" "datetime" "threading" "random" "collections")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if [ "$package" = "tkinter" ]; then
        # 特殊检查tkinter
        if ! python3 -c "import tkinter" &> /dev/null; then
            echo -e "${RED}✗ tkinter 未安装或无法导入${NC}"
        else
            echo -e "${GREEN}✓ tkinter 已安装${NC}"
        fi
    elif [ "$package" = "paho.mqtt" ]; then
        # 特殊检查paho.mqtt
        if ! python3 -c "import paho.mqtt.client" &> /dev/null; then
            echo -e "${RED}✗ paho-mqtt 未安装${NC}"
            echo -e "${YELLOW}尝试安装 paho-mqtt...${NC}"
            pip3 install paho-mqtt
        else
            echo -e "${GREEN}✓ paho.mqtt 已安装${NC}"
        fi
    elif [ "$package" = "pillow" ]; then
        # 特殊检查pillow
        if ! python3 -c "from PIL import Image" &> /dev/null; then
            echo -e "${RED}✗ pillow 未安装${NC}"
            echo -e "${YELLOW}尝试安装 pillow...${NC}"
            pip3 install pillow
        else
            echo -e "${GREEN}✓ PIL (pillow) 已安装${NC}"
        fi
    elif [ "$package" = "matplotlib" ]; then
        # 特殊检查matplotlib
        if ! python3 -c "import matplotlib" &> /dev/null; then
            echo -e "${RED}✗ matplotlib 未安装${NC}"
            echo -e "${YELLOW}尝试安装 matplotlib...${NC}"
            pip3 install matplotlib
        else
            echo -e "${GREEN}✓ matplotlib 已安装${NC}"
        fi
    elif [ "$package" = "json" ] || [ "$package" = "base64" ] || [ "$package" = "io" ] || [ "$package" = "datetime" ] || [ "$package" = "threading" ] || [ "$package" = "random" ] || [ "$package" = "collections" ]; then
        # 这些是Python标准库，应该已经安装
        echo -e "${GREEN}✓ $package 已内置于Python${NC}"
    fi
done

echo
echo -e "${BLUE}运行主程序(调试模式)...${NC}"
echo -e "${YELLOW}日志文件将保存在logs目录${NC}"
echo

# 创建配置目录（如果不存在）
mkdir -p config

# 生成模拟配置文件
if [ ! -f "config/config.json" ]; then
    echo '{
    "siot_server_http": "http://192.168.1.129:8080",
    "siot_username": "siot",
    "siot_password": "dfrobot",
    "mqtt_broker_host": "192.168.1.129",
    "mqtt_broker_port": 1883,
    "mqtt_client_id": "smart_campus_dashboard_client_debug",
    "mqtt_camera_topic": "sc/camera/stream",
    "mqtt_weather_topic": "sc/weather/data"
}' > config/config.json
    echo -e "${GREEN}已创建默认配置文件${NC}"
fi

# 使用Python的-v选项，启用详细模式
cd "$SCRIPT_DIR"
echo -e "${YELLOW}程序输出开始 -----------------------------${NC}"
python3 -v src/simple_dashboard.py 2>&1 | tee logs/debug_output_$(date +"%Y%m%d_%H%M%S").log
echo -e "${YELLOW}程序输出结束 -----------------------------${NC}"

echo
echo -e "${GREEN}调试执行完成.${NC}"
echo -e "${BLUE}日志文件已保存，可查阅详细错误信息.${NC}"
echo "按任意键关闭此窗口..."
read -n 1
