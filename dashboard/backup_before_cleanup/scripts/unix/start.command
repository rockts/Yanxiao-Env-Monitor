#!/bin/zsh

# 智慧校园仪表盘主启动脚本 - 增强版
# 作用：启动仪表盘的同时提供更好的错误处理和日志记录

# 确定脚本所在目录
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

# 颜色定义，用于美化输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 标题输出
echo "${BLUE}=====================================${NC}"
echo "${GREEN}  智慧校园环境监测仪表盘启动工具  ${NC}"
echo "${BLUE}=====================================${NC}"
echo "${YELLOW}当前工作目录:${NC} $SCRIPT_DIR"

# 检查Python环境
echo -n "检查Python环境... "
if ! command -v python3 &> /dev/null; then
    echo "${RED}错误：未安装Python3${NC}"
    echo "请安装Python3后再试。可以使用 'brew install python3'（macOS）进行安装。"
    exit 1
fi

python_version=$(python3 --version 2>&1)
echo "${GREEN}找到 $python_version${NC}"

# 检查必要文件
echo -n "检查程序文件... "
if [ ! -f "$SCRIPT_DIR/src/main.py" ]; then
    echo "${RED}错误：未找到主程序文件 src/main.py${NC}"
    echo "请确认项目文件结构完整。"
    exit 1
fi

# 检查配置文件
if [ ! -d "$SCRIPT_DIR/config" ]; then
    echo -n "创建配置目录... "
    mkdir -p "$SCRIPT_DIR/config"
    echo "${GREEN}完成${NC}"
fi

if [ ! -d "$SCRIPT_DIR/logs" ]; then
    echo -n "创建日志目录... "
    mkdir -p "$SCRIPT_DIR/logs"
    echo "${GREEN}完成${NC}"
fi

echo "${GREEN}完成${NC}"

# 启动主程序
echo "${YELLOW}启动仪表盘主程序...${NC}"
echo "日志将保存在 logs 目录中"
echo "${BLUE}------------------------------${NC}"

# 切换到src目录并启动主程序
cd "$SCRIPT_DIR/src"
if python3 main.py; then
    echo "${BLUE}------------------------------${NC}"
    echo "${GREEN}仪表盘已正常关闭${NC}"
else
    EXIT_CODE=$?
    echo "${BLUE}------------------------------${NC}"
    echo "${RED}仪表盘异常退出，错误码: $EXIT_CODE${NC}"
    echo "请查看日志文件了解详细信息。"
fi

# 返回原目录
cd "$SCRIPT_DIR"
