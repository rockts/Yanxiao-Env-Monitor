#!/bin/bash
# 运行优化版智慧校园仪表盘

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
echo -e "${GREEN}   烟铺小学智慧校园仪表盘 - 优化版   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo

# 确保使用Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    echo "访问 https://www.python.org/downloads/ 下载安装Python 3"
    echo
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

# 显示Python版本
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}使用: $PYTHON_VERSION${NC}"

# MQTT默认配置
MQTT_HOST="127.0.0.1" # 更改为本地地址，方便测试
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
        echo -e "${BLUE}启动仪表盘应用(优化版)...${NC}"
        python3 main_all_fixed_optimized.py
        ;;
    2)
        echo -e "${BLUE}启动测试数据发送器...${NC}"
        python3 send_test_data.py --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS"
        ;;
    3|*)
        echo -e "${BLUE}启动仪表盘应用(优化版)...${NC}"
        python3 main_all_fixed_optimized.py &
        MAIN_PID=$!
        
        sleep 2  # 等待仪表盘初始化
        
        echo -e "${BLUE}启动测试数据发送器...${NC}"
        python3 send_test_data.py --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" &
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
