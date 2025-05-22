#!/bin/bash
# 智慧校园环境监测系统 - 简易启动脚本
# 针对macOS系统优化的启动脚本，确保GUI能够正确显示

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 简易启动器      ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo

# 检测Python
PYTHON_CMD=$(command -v python3)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}错误: 找不到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    read -p "按回车键退出..."
    exit 1
fi

echo -e "${GREEN}Python 3已找到: $PYTHON_CMD${NC}"

# 检查是否缺少必要的库
echo -e "${YELLOW}检查必要的Python库...${NC}"
$PYTHON_CMD -c "import tkinter; import paho.mqtt.client; import matplotlib; import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}缺少必要的Python库.${NC}"
    echo -e "${YELLOW}正在安装必要的Python库...${NC}"
    $PYTHON_CMD -m pip install paho-mqtt matplotlib pillow
    echo -e "${GREEN}库安装完成${NC}"
fi

# 直接执行Python脚本
echo -e "${GREEN}直接启动仪表盘...${NC}"
"$PYTHON_CMD" "easy_launch.py"
