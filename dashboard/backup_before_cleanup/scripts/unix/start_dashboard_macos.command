#!/bin/bash
# 智慧校园仪表盘 macOS 启动脚本 - 双击可直接运行
# 此脚本会自动检测并使用正确的Python版本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 设置颜色用于输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}   烟铺小学智慧校园仪表盘启动程序   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 确定要使用的Python解释器
# 首先检查是否有已保存的配置
if [ -f "./python_config.env" ]; then
    source "./python_config.env"
    echo -e "${BLUE}加载已保存的Python配置...${NC}"
    if [ -n "$PYTHON_INTERPRETER" ] && [ -x "$PYTHON_INTERPRETER" ]; then
        echo -e "${GREEN}使用已配置的Python解释器: $PYTHON_INTERPRETER${NC}"
        PYTHON_CMD="$PYTHON_INTERPRETER"
    else
        echo -e "${YELLOW}已保存的Python配置无效，将重新检测...${NC}"
    fi
fi

# 如果没有有效的已保存配置，则尝试检测
if [ -z "$PYTHON_CMD" ]; then
    # 尝试找到Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        # 检查python命令是否为Python 3
        PY_VER=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
        if [ "$PY_VER" = "3" ]; then
            PYTHON_CMD="python"
        else
            echo -e "${RED}错误: 系统默认Python不是版本3.${NC}"
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
fi

# 显示Python版本
PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}使用: $PYTHON_VERSION${NC}"

# 保存当前使用的Python解释器路径以供将来使用
which $PYTHON_CMD > /dev/null 2>&1
if [ $? -eq 0 ]; then
    PYTHON_PATH=$(which $PYTHON_CMD)
    echo "PYTHON_INTERPRETER=\"$PYTHON_PATH\"" > ./python_config.env
    echo "# 此文件由启动脚本自动生成 - $(date)" >> ./python_config.env
    echo -e "${BLUE}已保存Python配置到 python_config.env${NC}"
fi

# 检查并安装主要依赖
echo -e "${BLUE}检查依赖项...${NC}"
PACKAGES=("tkinter" "paho.mqtt.client" "matplotlib" "PIL.Image")

for package in "${PACKAGES[@]}"; do
    if ! python3 -c "import $package" &>/dev/null; then
        echo -e "${YELLOW}正在安装 $package...${NC}"
        python3 -m pip install $package
    else
        echo -e "${GREEN}✓ $package 已安装${NC}"
    fi
done

# 主程序和测试程序路径
MAIN_APP="${SCRIPT_DIR}/main_all_fixed.py"
TEST_DATA_APP="${SCRIPT_DIR}/send_test_data.py"

# MQTT默认配置
MQTT_HOST="192.168.1.129"
MQTT_PORT="1883"
MQTT_USER="siot"
MQTT_PASS="dfrobot"

# 询问用户启动模式
echo
echo "请选择启动模式:"
echo "1) 仅启动仪表盘应用"
echo "2) 仅启动测试数据发送器"
echo "3) 同时启动仪表盘和测试数据发送器"
echo
read -p "请选择 [1-3] (默认: 3): " choice
echo

case "${choice:-3}" in
    1)
        echo -e "${BLUE}启动仪表盘应用...${NC}"
        $PYTHON_CMD "$MAIN_APP"
        ;;
    2)
        echo -e "${BLUE}启动测试数据发送器...${NC}"
        $PYTHON_CMD "$TEST_DATA_APP" --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS"
        ;;
    3|*)
        echo -e "${BLUE}启动仪表盘应用...${NC}"
        $PYTHON_CMD "$MAIN_APP" &
        MAIN_PID=$!
        
        sleep 2  # 等待仪表盘初始化
        
        echo -e "${BLUE}启动测试数据发送器...${NC}"
        $PYTHON_CMD "$TEST_DATA_APP" --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" &
        TEST_PID=$!
        
        echo -e "${GREEN}两个程序已成功启动!${NC}"
        echo -e "${YELLOW}按 Ctrl+C 终止程序${NC}"
        
        # 等待两个程序结束
        wait $MAIN_PID $TEST_PID
        ;;
esac

echo
echo -e "${GREEN}程序已退出.${NC}"
echo "按任意键关闭此窗口..."
read -n 1
