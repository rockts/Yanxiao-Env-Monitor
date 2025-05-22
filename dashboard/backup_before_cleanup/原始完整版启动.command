#!/bin/bash
# 烟铺小学智慧校园环境监测系统 - 原始完整版启动脚本
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
echo -e "${GREEN}   烟铺小学智慧校园环境监测系统 - 【原始完整版】   ${NC}"
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

# macOS特定处理
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}检测到macOS系统${NC}"
    echo -e "${GREEN}使用AppleScript确保GUI正确显示...${NC}"
    
    # 使用AppleScript启动新终端
    osascript <<EOF
    tell application "Terminal"
        do script "cd '$SCRIPT_DIR' && '$PYTHON_CMD' '原始完整版启动.py'"
        activate
    end tell
EOF
    
    echo -e "${GREEN}已在新终端窗口中启动原始完整版仪表盘${NC}"
    echo -e "${YELLOW}请查看新打开的终端窗口${NC}"
else
    # 非macOS系统
    echo -e "${YELLOW}非macOS系统，直接启动...${NC}"
    "$PYTHON_CMD" "原始完整版启动.py"
fi

echo
echo "仪表盘已在新窗口中启动，此窗口可以关闭"
echo "如果新窗口没有打开，请尝试手动运行: python3 原始完整版启动.py"
read -p "按回车键关闭此窗口..."
