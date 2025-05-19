#!/bin/bash
# 智慧校园仪表盘启动脚本
# 可以启动主应用程序和/或测试数据发送器

# 设置颜色用于输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 应用路径
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
MAIN_APP="${APP_DIR}/main_all_fixed.py"
TEST_DATA_APP="${APP_DIR}/send_test_data.py"

# MQTT服务器设置
DEFAULT_MQTT_HOST="192.168.1.129"
DEFAULT_MQTT_PORT="1883"
DEFAULT_MQTT_USER="siot"
DEFAULT_MQTT_PASS="dfrobot"

# 检查依赖项
check_dependency() {
    echo -e "${YELLOW}检查依赖项: $1...${NC}"
    if ! python3 -c "import $1" &>/dev/null; then
        echo -e "${RED}未找到模块 $1. ${NC}"
        read -p "是否安装? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}安装 $1...${NC}"
            python3 -m pip install $1
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}安装成功!${NC}"
            else
                echo -e "${RED}安装失败. 请手动安装: pip install $1${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}警告: 没有安装 $1. 程序可能无法正常工作.${NC}"
        fi
    else
        echo -e "${GREEN}已安装 $1.${NC}"
    fi
}

# 显示帮助
show_help() {
    echo -e "${GREEN}烟铺小学智慧校园仪表盘启动脚本${NC}"
    echo "使用方法: $0 [选项]"
    echo
    echo "选项:"
    echo "  --app-only        仅启动主应用程序"
    echo "  --test-only       仅启动测试数据发送器"
    echo "  --both            同时启动主应用和测试数据发送器 (默认)"
    echo "  --mqtt-host HOST  设置MQTT服务器地址 (默认: $DEFAULT_MQTT_HOST)"
    echo "  --mqtt-port PORT  设置MQTT服务器端口 (默认: $DEFAULT_MQTT_PORT)"
    echo "  --mqtt-user USER  设置MQTT用户名 (默认: $DEFAULT_MQTT_USER)"
    echo "  --mqtt-pass PASS  设置MQTT密码"
    echo "  --help, -h        显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 --app-only                      # 仅启动主应用程序" 
    echo "  $0 --test-only --mqtt-host 10.0.0.1  # 仅启动测试数据发送器并指定MQTT服务器"
    echo
}

# 启动主应用程序
start_main_app() {
    echo -e "${BLUE}启动智慧校园仪表盘...${NC}"
    python3 "$MAIN_APP" &
    MAIN_APP_PID=$!
    echo -e "${GREEN}智慧校园仪表盘已启动，进程 ID: $MAIN_APP_PID${NC}"
}

# 启动测试数据发送器
start_test_data_sender() {
    echo -e "${BLUE}启动测试数据发送器...${NC}"
    python3 "$TEST_DATA_APP" --host "$MQTT_HOST" --port "$MQTT_PORT" --username "$MQTT_USER" --password "$MQTT_PASS" &
    TEST_DATA_PID=$!
    echo -e "${GREEN}测试数据发送器已启动，进程 ID: $TEST_DATA_PID${NC}"
}

# 初始化参数
MODE="both"
MQTT_HOST="$DEFAULT_MQTT_HOST"
MQTT_PORT="$DEFAULT_MQTT_PORT"
MQTT_USER="$DEFAULT_MQTT_USER"
MQTT_PASS="$DEFAULT_MQTT_PASS"

# 处理命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --app-only)
            MODE="app-only"
            shift
            ;;
        --test-only)
            MODE="test-only"
            shift
            ;;
        --both)
            MODE="both"
            shift
            ;;
        --mqtt-host)
            MQTT_HOST="$2"
            shift 2
            ;;
        --mqtt-port)
            MQTT_PORT="$2"
            shift 2
            ;;
        --mqtt-user)
            MQTT_USER="$2"
            shift 2
            ;;
        --mqtt-pass)
            MQTT_PASS="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 检查文件是否存在
if [ ! -f "$MAIN_APP" ]; then
    echo -e "${RED}错误: 找不到主应用程序文件: $MAIN_APP${NC}"
    exit 1
fi

if [ ! -f "$TEST_DATA_APP" ]; then
    echo -e "${RED}错误: 找不到测试数据发送器文件: $TEST_DATA_APP${NC}"
    exit 1
fi

# 检查Python和主要依赖项
echo -e "${YELLOW}检查Python版本...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Python 3未找到，请先安装Python 3${NC}"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}$PYTHON_VERSION 已安装.${NC}"
fi

# 检查关键依赖项
check_dependency "tkinter"
check_dependency "paho.mqtt.client"
check_dependency "matplotlib"
check_dependency "PIL.Image"

# 根据选择的模式启动程序
case "$MODE" in
    app-only)
        start_main_app
        # 等待主应用程序退出
        wait $MAIN_APP_PID
        ;;
    test-only)
        start_test_data_sender
        # 等待测试数据发送器退出
        wait $TEST_DATA_PID
        ;;
    both)
        start_main_app
        sleep 2  # 短暂延迟，让主应用程序有时间初始化
        start_test_data_sender
        
        # 等待两个进程
        echo -e "${BLUE}两个程序已启动. 按 Ctrl+C 终止.${NC}"
        wait $MAIN_APP_PID $TEST_DATA_PID
        ;;
esac

# 处理退出
echo -e "${YELLOW}程序已终止.${NC}"
exit 0