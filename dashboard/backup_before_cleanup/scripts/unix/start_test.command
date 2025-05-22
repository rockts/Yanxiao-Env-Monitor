#!/bin/zsh

# 智慧校园仪表盘测试环境启动脚本 - 增强版
# 作用：启动完整测试环境，包括MQTT代理、传感器模拟器和视频模拟器

# 确定脚本所在目录
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

# 颜色定义，用于美化输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 标题输出
echo "${BLUE}=====================================${NC}"
echo "${CYAN} 智慧校园仪表盘测试环境启动工具 ${NC}"
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

if [ ! -f "$SCRIPT_DIR/src/simple_mqtt_broker.py" ] || [ ! -f "$SCRIPT_DIR/src/sensor_data_simulator.py" ] || [ ! -f "$SCRIPT_DIR/src/video_stream_simulator.py" ]; then
    echo "${YELLOW}警告：部分测试组件文件可能已重命名或不存在${NC}"
    echo "检查测试组件:"
    
    if [ ! -f "$SCRIPT_DIR/src/simple_mqtt_broker.py" ]; then
        if [ -f "$SCRIPT_DIR/src/mqtt_broker.py" ]; then
            echo "  找到 mqtt_broker.py 替代 simple_mqtt_broker.py"
            BROKER_SCRIPT="mqtt_broker.py"
        else
            echo "${RED}  未找到MQTT代理脚本${NC}"
            exit 1
        fi
    else
        BROKER_SCRIPT="simple_mqtt_broker.py"
    fi
    
    if [ ! -f "$SCRIPT_DIR/src/sensor_data_simulator.py" ]; then
        if [ -f "$SCRIPT_DIR/src/send_test_data.py" ]; then
            echo "  找到 send_test_data.py 替代 sensor_data_simulator.py"
            SENSOR_SCRIPT="send_test_data.py"
        else
            echo "${RED}  未找到传感器数据模拟脚本${NC}"
            exit 1
        fi
    else
        SENSOR_SCRIPT="sensor_data_simulator.py"
    fi
    
    if [ ! -f "$SCRIPT_DIR/src/video_stream_simulator.py" ]; then
        if [ -f "$SCRIPT_DIR/src/send_video_test.py" ]; then
            echo "  找到 send_video_test.py 替代 video_stream_simulator.py"
            VIDEO_SCRIPT="send_video_test.py"
        else
            echo "${RED}  未找到视频流模拟脚本${NC}"
            exit 1
        fi
    else
        VIDEO_SCRIPT="video_stream_simulator.py"
    fi
else
    BROKER_SCRIPT="simple_mqtt_broker.py"
    SENSOR_SCRIPT="sensor_data_simulator.py"
    VIDEO_SCRIPT="video_stream_simulator.py"
    echo "${GREEN}完成${NC}"
fi

# 创建必要目录
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

# 定义清理函数，确保在脚本结束时杀掉所有子进程
cleanup() {
  echo "\n${YELLOW}正在清理测试进程...${NC}"
  # 使用-9强制杀死进程，确保彻底清理
  kill -9 $BROKER_PID $DATA_PID $VIDEO_PID 2>/dev/null
  wait
  echo "${GREEN}所有测试进程已终止${NC}"
  exit 0
}

# 捕获终端信号
trap cleanup EXIT INT TERM

# 启动MQTT代理
echo "${BLUE}------------------------------${NC}"
echo "${CYAN}1. 启动MQTT代理服务器...${NC}"
cd "$SCRIPT_DIR/src"
python3 $BROKER_SCRIPT &
BROKER_PID=$!

# 等待MQTT代理启动
sleep 2
if ps -p $BROKER_PID > /dev/null; then
    echo "${GREEN}   MQTT代理已启动，PID: $BROKER_PID${NC}"
else
    echo "${RED}   MQTT代理启动失败${NC}"
    exit 1
fi

# 启动传感器测试数据
echo "${BLUE}------------------------------${NC}"
echo "${CYAN}2. 启动传感器测试数据发送程序...${NC}"
python3 $SENSOR_SCRIPT --local &
DATA_PID=$!

# 检查传感器数据程序是否成功启动
sleep 1
if ps -p $DATA_PID > /dev/null; then
    echo "${GREEN}   传感器数据程序已启动，PID: $DATA_PID${NC}"
else
    echo "${RED}   传感器数据程序启动失败${NC}"
    kill $BROKER_PID 2>/dev/null
    exit 1
fi

# 启动视频测试数据
echo "${BLUE}------------------------------${NC}"
echo "${CYAN}3. 启动视频测试数据发送程序...${NC}"
python3 $VIDEO_SCRIPT --fps 3 &
VIDEO_PID=$!

# 检查视频数据程序是否成功启动
sleep 1
if ps -p $VIDEO_PID > /dev/null; then
    echo "${GREEN}   视频数据程序已启动，PID: $VIDEO_PID${NC}"
else
    echo "${YELLOW}   警告：视频数据程序可能未正确启动${NC}"
    echo "   仪表盘仍将启动，但可能不会显示视频"
fi

# 等待所有测试数据程序就绪
sleep 2
echo "${BLUE}------------------------------${NC}"
echo "${CYAN}4. 启动智慧校园仪表盘主程序...${NC}"
echo "${YELLOW}注意：关闭此窗口将终止所有测试程序${NC}"
echo "${BLUE}------------------------------${NC}"

# 启动主程序并等待它完成
if python3 main.py; then
    echo "${BLUE}------------------------------${NC}"
    echo "${GREEN}仪表盘已正常关闭${NC}"
else
    EXIT_CODE=$?
    echo "${BLUE}------------------------------${NC}"
    echo "${RED}仪表盘异常退出，错误码: $EXIT_CODE${NC}"
    echo "请查看日志文件了解详细信息。"
fi

# 清理会在trap函数中自动执行
