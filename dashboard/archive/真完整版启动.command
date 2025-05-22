#!/bin/bash
# 智慧校园环境监测系统 - 真·完整版启动脚本
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
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 真·完整版      ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}    显示所有传感器数据、图表和监控画面的完整版     ${NC}"
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
    echo -e "${YELLOW}安装必要的Python库...${NC}"
    $PYTHON_CMD -m pip install paho-mqtt matplotlib pillow
fi

# macOS特定处理
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}检测到macOS系统${NC}"
    echo -e "${GREEN}使用AppleScript确保GUI正确显示...${NC}"
    
    # 使用AppleScript启动新终端
    osascript <<EOF
    tell application "Terminal"
        do script "cd '$SCRIPT_DIR' && '$PYTHON_CMD' '真完整版启动.py'"
        set current settings of window 1 to settings set "Homebrew"
        set background color of window 1 to {0, 0, 0}
        set normal text color of window 1 to {50000, 50000, 50000}
        set the number of rows to 30
        set the number of columns to 100
        set the title of window 1 to "烟铺小学智慧校园环境监测系统 - 真·完整版"
        activate
    end tell
EOF
    
    echo -e "${GREEN}已在新终端窗口中启动真·完整版仪表盘${NC}"
    echo -e "${YELLOW}请查看新打开的终端窗口${NC}"
else
    # 非macOS系统
    echo -e "${YELLOW}非macOS系统，直接启动...${NC}"
    "$PYTHON_CMD" "真完整版启动.py"
fi

echo
echo "仪表盘已在新窗口中启动，此窗口可以关闭"
echo "如果新窗口没有打开，请尝试手动运行: python3 真完整版启动.py"
read -p "按回车键关闭此窗口..."
