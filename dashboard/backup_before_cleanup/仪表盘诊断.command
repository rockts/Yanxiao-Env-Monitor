#!/bin/bash
# 智慧校园环境监测系统 - 诊断工具启动脚本
# 针对macOS系统优化的启动脚本

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
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 诊断工具      ${NC}"
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

# 运行诊断工具
if [ -f "仪表盘诊断.py" ]; then
    "$PYTHON_CMD" "仪表盘诊断.py"
else
    echo -e "${RED}错误: 找不到诊断工具脚本 (仪表盘诊断.py)${NC}"
    read -p "按回车键退出..."
    exit 1
fi

read -p "按回车键关闭此窗口..."
