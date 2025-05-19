#!/bin/zsh

# 带测试数据的启动脚本 - 改进版
# 注意：在macOS上，可能需要设置终端能够访问磁盘的权限

# 确定脚本所在目录
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "====== 智慧校园仪表盘测试环境启动 ======"
echo "当前工作目录: $SCRIPT_DIR"

# 定义清理函数，确保在脚本结束时杀掉所有子进程
cleanup() {
  echo "\n正在清理进程..."
  kill $BROKER_PID $DATA_PID $VIDEO_PID 2>/dev/null
  wait
  echo "所有测试进程已终止"
  exit 0
}

# 捕获终端信号
trap cleanup EXIT INT TERM

# 启动MQTT代理
echo "1. 启动MQTT代理服务器..."
cd "$SCRIPT_DIR/src"
python3 simple_mqtt_broker.py &
BROKER_PID=$!

# 等待MQTT代理启动
sleep 2
echo "   MQTT代理已启动，PID: $BROKER_PID"

# 启动传感器测试数据
echo "2. 启动传感器测试数据发送程序..."
python3 send_test_data.py --local &
DATA_PID=$!
echo "   传感器数据程序已启动，PID: $DATA_PID"

# 启动视频测试数据
echo "3. 启动视频测试数据发送程序..."
python3 send_video_test.py --fps 3 &
VIDEO_PID=$!
echo "   视频数据程序已启动，PID: $VIDEO_PID"

# 等待所有测试数据程序启动
sleep 2
echo "4. 启动智慧校园仪表盘主程序..."

# 启动主程序并等待它完成
python3 main.py

# 清理会在trap函数中自动执行
