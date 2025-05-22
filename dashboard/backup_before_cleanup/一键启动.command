#!/bin/bash
# 超级简单版仪表盘启动脚本
# 双击此文件即可启动仪表盘

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
echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统 - 一键启动   ${NC}"
echo -e "${BLUE}====================================${NC}"
echo

# 检测Python
PYTHON_CMD=$(command -v python3)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}错误: 找不到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 检查是否在macOS上运行
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}macOS系统检测成功${NC}"
    
    # 使用AppleScript确保GUI能够正确显示
    echo -e "${GREEN}使用AppleScript启动图形界面...${NC}"
    
    # 创建AppleScript
    osascript <<EOF
    tell application "Terminal"
        do script "cd '$SCRIPT_DIR' && '$PYTHON_CMD' '超级简单版仪表盘.py'"
        activate
    end tell
EOF
    
    echo -e "${GREEN}已在新终端窗口中启动仪表盘，请查看新打开的窗口${NC}"
else
    # 非macOS系统直接运行Python脚本
    echo -e "${GREEN}直接启动仪表盘...${NC}"
    "$PYTHON_CMD" "超级简单版仪表盘.py"
fi

echo
echo "程序已在新窗口中启动，此窗口可以关闭"
read -p "按回车键关闭此窗口..."
