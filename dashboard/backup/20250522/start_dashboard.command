#!/bin/bash
# 智慧校园环境监测系统 - 智能启动器
# 自动选择适当的Python版本并启动系统

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
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 智能启动器      ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}     自动选择Python版本并启动系统      ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 检查Python版本
echo -e "${BLUE}[信息]${NC} 检查Python环境..."

# 首选命令顺序：python3, python
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version)
        echo -e "${GREEN}[成功]${NC} 找到 $version"
        
        # 检查是Python 3
        if [[ $version == *"Python 3"* ]]; then
            PYTHON_CMD=$cmd
            break
        else
            echo -e "${YELLOW}[警告]${NC} 检测到Python 2，尝试寻找Python 3..."
        fi
    fi
done

# 如果没有找到任何Python
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[错误]${NC} 未找到Python 3。请安装Python 3后再试。"
    echo -e "可以从 https://www.python.org/downloads/ 下载安装"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖项
echo -e "${BLUE}[信息]${NC} 检查依赖项..."

# 检查paho-mqtt
if ! $PYTHON_CMD -c "import paho.mqtt" 2>/dev/null; then
    echo -e "${YELLOW}[警告]${NC} 未安装paho-mqtt库，尝试安装..."
    if ! $PYTHON_CMD -m pip install paho-mqtt; then
        echo -e "${RED}[错误]${NC} 安装paho-mqtt失败，请手动安装:"
        echo -e "    $PYTHON_CMD -m pip install paho-mqtt"
        echo ""
        read -p "按回车键退出..."
        exit 1
    fi
else
    echo -e "${GREEN}[成功]${NC} paho-mqtt已安装"
fi

# 检查PIL
if ! $PYTHON_CMD -c "from PIL import Image" 2>/dev/null; then
    echo -e "${YELLOW}[警告]${NC} 未安装Pillow库，尝试安装..."
    if ! $PYTHON_CMD -m pip install Pillow; then
        echo -e "${YELLOW}[警告]${NC} 安装Pillow失败，视频功能可能不可用。"
        echo -e "可以手动安装: $PYTHON_CMD -m pip install Pillow"
    fi
else
    echo -e "${GREEN}[成功]${NC} Pillow已安装"
fi

# 启动仪表盘
echo -e "${BLUE}[信息]${NC} 启动智慧校园环境监测系统..."
echo -e "${YELLOW}[提示]${NC} 请勿关闭此窗口，关闭会导致系统停止运行！"
echo -e "${BLUE}=======================================================${NC}"

# 启动程序
$PYTHON_CMD simple_working_dashboard.py

# 如果程序意外终止，等待用户确认
echo ""
echo -e "${RED}[信息]${NC} 程序已终止运行"
read -p "按回车键退出..."
