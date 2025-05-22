#!/bin/bash
# 烟铺小学智慧校园环境监测系统 - 启动文件
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
echo -e "${GREEN}   烟铺小学智慧校园仪表盘启动程序   ${NC}"
echo -e "${BLUE}====================================${NC}"
echo

# 执行启动脚本
if [ -f "$SCRIPT_DIR/run_dashboard_macos.sh" ]; then
    echo -e "${GREEN}执行启动脚本...${NC}"
    $SCRIPT_DIR/run_dashboard_macos.sh
else
    echo -e "${RED}错误: 找不到启动脚本${NC}"
    echo -e "${YELLOW}请确保run_dashboard_macos.sh在同一目录下${NC}"
    
    # 尝试直接运行Python脚本
    if [ -f "$SCRIPT_DIR/launch_dashboard.py" ]; then
        echo -e "${YELLOW}尝试运行优化版启动器...${NC}"
        python3 "$SCRIPT_DIR/launch_dashboard.py"
    else
        # 回退到其他脚本
        if [ -f "$SCRIPT_DIR/run_simple_dashboard.py" ]; then
            echo -e "${YELLOW}尝试运行简化版仪表盘...${NC}"
            python3 "$SCRIPT_DIR/run_simple_dashboard.py"
        else
            echo -e "${RED}错误: 找不到run_simple_dashboard.py${NC}"
            
            # 最后尝试run_full_dashboard.py
            if [ -f "$SCRIPT_DIR/run_full_dashboard.py" ]; then
                echo -e "${YELLOW}尝试运行完整仪表盘...${NC}"
                python3 "$SCRIPT_DIR/run_full_dashboard.py"
            else
                echo -e "${RED}错误: 也找不到run_full_dashboard.py${NC}"
            fi
        fi
    fi
fi

echo
echo "按Enter键退出..."
read
