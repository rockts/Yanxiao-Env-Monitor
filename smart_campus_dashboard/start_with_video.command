#!/bin/bash
# 智慧校园仪表盘增强启动脚本 - 带视频测试

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}      智慧校园环境监测仪表盘启动脚本 (增强版)      ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo

# 检查并安装依赖项
echo -e "${YELLOW}[1/5] 检查并安装依赖项...${NC}"
pip_install() {
    package=$1
    python3 -c "import $package" >/dev/null 2>&1 || {
        echo -e "  ${YELLOW}安装 $package...${NC}"
        pip3 install $package
    }
}

pip_install paho.mqtt
pip_install matplotlib
pip_install Pillow
pip_install requests

echo -e "${GREEN}✓ 依赖项检查完成${NC}"
echo

# 启动MQTT代理
echo -e "${YELLOW}[2/5] 启动MQTT代理...${NC}"
if nc -z -w1 127.0.0.1 1883 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ MQTT代理已在运行${NC}"
else
    echo -e "  ${YELLOW}启动本地MQTT代理...${NC}"
    python3 simple_mqtt_broker.py &
    BROKER_PID=$!
    echo -e "  ${GREEN}➜ 本地MQTT代理已启动 (PID: $BROKER_PID)${NC}"
    sleep 2
fi
echo

# 启动测试数据发送器
echo -e "${YELLOW}[3/5] 启动传感器数据模拟...${NC}"
python3 send_test_data.py --local &
TEST_DATA_PID=$!
echo -e "${GREEN}✓ 传感器数据模拟程序已启动 (PID: $TEST_DATA_PID)${NC}"
echo

# 启动视频测试数据发送器
echo -e "${YELLOW}[4/5] 启动视频模拟数据发送器...${NC}"
python3 send_video_test.py --fps 3 &
VIDEO_TEST_PID=$!
echo -e "${GREEN}✓ 视频数据模拟程序已启动 (PID: $VIDEO_TEST_PID)${NC}"
echo

# 启动优化后的仪表盘程序
echo -e "${YELLOW}[5/5] 启动智慧校园环境监测仪表盘...${NC}"
echo -e "${GREEN}✓ 启动中，请稍候...${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}所有组件已启动。关闭仪表盘窗口后，后台进程将被清理。${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo

# 启动主程序
python3 main_all_fixed_optimized.py

# 清理后台进程
echo
echo -e "${YELLOW}正在清理后台进程...${NC}"

cleanup() {
    # 杀掉后台进程
    if [ ! -z "$TEST_DATA_PID" ]; then
        kill $TEST_DATA_PID 2>/dev/null || true
        echo -e "${GREEN}✓ 已停止传感器数据模拟器${NC}"
    fi
    
    if [ ! -z "$VIDEO_TEST_PID" ]; then
        kill $VIDEO_TEST_PID 2>/dev/null || true
        echo -e "${GREEN}✓ 已停止视频数据模拟器${NC}"
    fi
    
    if [ ! -z "$BROKER_PID" ]; then
        kill $BROKER_PID 2>/dev/null || true
        echo -e "${GREEN}✓ 已停止本地MQTT代理${NC}"
    fi
    
    # 查找并杀死所有相关的Python进程
    pkill -f "python3 simple_mqtt_broker.py" 2>/dev/null || true
    pkill -f "python3 send_test_data.py" 2>/dev/null || true
    pkill -f "python3 send_video_test.py" 2>/dev/null || true
}

# 注册清理函数
trap cleanup EXIT

# 执行清理
cleanup

echo -e "${GREEN}✓ 清理完成，程序已退出${NC}"
exit 0
