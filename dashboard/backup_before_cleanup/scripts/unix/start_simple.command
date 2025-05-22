#!/bin/bash
# 简化版智慧校园环境监测系统启动脚本

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
echo -e "${GREEN}   简化版智慧校园环境监测系统   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 确定Python解释器
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}使用Python解释器: $PYTHON_CMD $(python3 --version)${NC}"
else
    echo -e "${RED}错误: 未找到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    exit 1
fi

# 检查tkinter包
echo -e "${BLUE}检查tkinter包...${NC}"
if ! python3 -c "import tkinter" &>/dev/null; then
    echo -e "${RED}错误: tkinter未安装或无法导入.${NC}"
    echo -e "${YELLOW}tkinter通常随Python一起安装，但某些系统可能需要单独安装.${NC}"
    echo "在macOS上，可以尝试重新安装Python或使用brew install python-tk"
    exit 1
else
    echo -e "${GREEN}✓ tkinter 已安装${NC}"
fi

echo
echo -e "${BLUE}运行简化版智慧校园环境监测系统...${NC}"
cd "$SCRIPT_DIR"
$PYTHON_CMD src/simple_dashboard.py

echo
echo -e "${GREEN}程序已退出.${NC}"
echo "按任意键关闭此窗口..."
read -n 1
