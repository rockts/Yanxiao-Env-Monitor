#!/bin/bash
# 智慧校园仪表盘依赖项更新脚本
# 此脚本用于更新/安装所有应用程序需要的依赖库

# 设置颜色用于输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}   烟铺小学智慧校园仪表盘 - 依赖项更新   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 确保使用Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # 检查Python版本
    PY_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    if [ "$PY_VERSION" -eq 3 ]; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}错误: 未找到Python 3.${NC}"
        echo -e "${YELLOW}请安装Python 3后再试.${NC}"
        echo "访问 https://www.python.org/downloads/ 下载安装Python 3"
        echo
        echo "按任意键退出..."
        read -n 1
        exit 1
    fi
else
    echo -e "${RED}错误: 未找到Python.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    echo "访问 https://www.python.org/downloads/ 下载安装Python 3"
    echo
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

# 显示Python版本
PY_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}使用: $PY_VERSION${NC}"
echo

# 确保pip已安装
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${YELLOW}正在安装pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $PYTHON_CMD get-pip.py
    rm get-pip.py
fi

# 更新pip本身
echo -e "${BLUE}更新pip...${NC}"
$PYTHON_CMD -m pip install --upgrade pip

# 定义要安装的依赖项列表
DEPENDENCIES=(
    "paho-mqtt>=1.6.1"
    "Pillow>=8.4.0"
    "matplotlib>=3.5.1"
    "requests>=2.27.1"
    "numpy>=1.22.0"
)

# 安装/更新所有依赖项
echo -e "${BLUE}安装/更新依赖项...${NC}"
for dep in "${DEPENDENCIES[@]}"; do
    echo -e "${YELLOW}安装/更新: $dep${NC}"
    $PYTHON_CMD -m pip install --upgrade $dep
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 成功安装/更新: $dep${NC}"
    else
        echo -e "${RED}✗ 安装/更新失败: $dep${NC}"
    fi
done

echo
echo -e "${GREEN}依赖项更新完成!${NC}"
echo

# 记录所有已安装的包
echo -e "${BLUE}已安装的依赖项:${NC}"
$PYTHON_CMD -m pip list

echo
echo -e "${GREEN}处理完成.${NC}"
echo "按任意键退出..."
read -n 1