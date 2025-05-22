#!/bin/bash
# 仪表盘macOS启动脚本
# 使用macOS终端来启动Python GUI应用程序

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检测Python
PYTHON_CMD=$(command -v python3)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}错误: 找不到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    exit 1
fi

# 显示标题
echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}   烟铺小学智慧校园仪表盘启动程序   ${NC}"
echo -e "${BLUE}====================================${NC}"
echo

# 检查是否在VS Code终端中运行
VSCODE_TERMINAL=false
if [[ -n "$TERM_PROGRAM" && "$TERM_PROGRAM" == *"vscode"* ]]; then
    VSCODE_TERMINAL=true
    echo -e "${YELLOW}检测到在VS Code终端中运行${NC}"
fi

# 使用osascript创建一个可以显示GUI的终端
if $VSCODE_TERMINAL; then
    echo -e "${YELLOW}在macOS终端中启动仪表盘...${NC}"
    
    # 创建AppleScript来在新的Terminal窗口中运行仪表盘
    APPLESCRIPT=$(cat << EOF
    tell application "Terminal"
        do script "cd '$SCRIPT_DIR' && $PYTHON_CMD launch_dashboard.py"
        activate
    end tell
EOF
)
    
    # 运行AppleScript
    osascript -e "$APPLESCRIPT"
    echo -e "${GREEN}仪表盘已在macOS终端中启动${NC}"
else
    # 直接运行
    echo -e "${GREEN}启动仪表盘...${NC}"
    $PYTHON_CMD run_full_dashboard.py
fi

echo
echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}   仪表盘启动命令已执行   ${NC}"
echo -e "${BLUE}====================================${NC}"
