#!/bin/bash
# 智慧校园环境监测系统 - 改进版AQI处理启动脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色设置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN} 智慧校园环境监测系统（改进版AQI处理） ${NC}"
echo -e "${BLUE}============================================${NC}"

# 检查Python是否安装
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}使用Python解释器: $PYTHON_CMD $(python3 --version)${NC}"
else
    echo -e "${RED}错误: 未找到Python 3.${NC}"
    echo -e "${YELLOW}请安装Python 3后再试.${NC}"
    exit 1
fi

# 检查必要的包
echo -e "${BLUE}检查必要的Python包...${NC}"
PACKAGES=("tkinter" "paho-mqtt" "pillow")

for package in "${PACKAGES[@]}"; do
    if [ "$package" = "tkinter" ]; then
        # 特殊检查tkinter
        if ! python3 -c "import tkinter" &>/dev/null; then
            echo -e "${RED}错误: tkinter未安装或无法导入.${NC}"
            echo -e "${YELLOW}tkinter通常随Python一起安装，但某些系统可能需要单独安装.${NC}"
            echo "在macOS上，可以尝试重新安装Python或使用brew install python-tk"
            exit 1
        else
            echo -e "${GREEN}✓ tkinter 已安装${NC}"
        fi
    elif [ "$package" = "paho-mqtt" ]; then
        if ! python3 -c "import paho.mqtt.client" &>/dev/null; then
            echo -e "${YELLOW}正在安装 $package...${NC}"
            pip3 install paho-mqtt
            if [ $? -ne 0 ]; then
                echo -e "${RED}安装失败，将使用模拟数据模式${NC}"
            fi
        else
            echo -e "${GREEN}✓ paho-mqtt 已安装${NC}"
        fi
    elif [ "$package" = "pillow" ]; then
        if ! python3 -c "from PIL import Image" &>/dev/null; then
            echo -e "${YELLOW}正在安装 $package...${NC}"
            pip3 install pillow
            if [ $? -ne 0 ]; then
                echo -e "${RED}安装失败，部分图像功能可能不可用${NC}"
            fi
        else
            echo -e "${GREEN}✓ pillow 已安装${NC}"
        fi
    fi
done

# 检查本地配置文件
if [ ! -f "$SCRIPT_DIR/config/local_config.json" ]; then
    echo -e "${YELLOW}创建本地配置文件...${NC}"
    mkdir -p "$SCRIPT_DIR/config"
    cat > "$SCRIPT_DIR/config/local_config.json" << 'EOL'
{
    "siot_server_http": "http://localhost:8080",
    "siot_username": "siot",
    "siot_password": "dfrobot",
    "mqtt_broker_host": "localhost",
    "mqtt_broker_port": 1883,
    "mqtt_client_id": "smart_campus_dashboard_client_local",
    "mqtt_camera_topic": "sc/camera/stream",
    "mqtt_weather_topic": "sc/weather/data"
}
EOL
    echo -e "${GREEN}已创建本地配置文件${NC}"
fi

# 创建临时MQTT服务器脚本
echo -e "${BLUE}创建临时MQTT服务器脚本...${NC}"
cat > "$SCRIPT_DIR/temp_mqtt_server.py" << 'EOL'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时MQTT服务器和数据发送器 - 改进版AQI处理
"""
import time
import random
import json
import threading
import os
import signal
import sys
import socket

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("警告: MQTT库未安装，无法启动MQTT服务")
    sys.exit(1)

# MQTT服务器配置
MQTT_PORT = 1883
MQTT_TOPICS = {
    "环境温度": {"min": 18, "max": 30, "step": 0.1},
    "环境湿度": {"min": 30, "max": 80, "step": 1},
    "aqi": {"min": 20, "max": 200, "step": 1, "formats": ["raw", "json", "string"]},
    "tvoc": {"min": 100, "max": 500, "step": 10},
    "eco2": {"min": 400, "max": 2000, "step": 50},
    "紫外线指数": {"min": 0, "max": 10, "step": 0.1},
    "uv风险等级": {"values": ["低", "中", "高", "很高"]},
    "噪音": {"min": 30, "max": 70, "step": 0.5}
}

# 模拟数据
data_values = {
    "环境温度": 25.6,
    "环境湿度": 60,
    "aqi": 52,
    "tvoc": 250,
    "eco2": 800,
    "紫外线指数": 2.5,
    "uv风险等级": "低",
    "噪音": 45.0
}

# 停止标志
stop_flag = False

def generate_random_value(config):
    """根据配置生成随机值"""
    if "values" in config:
        return random.choice(config["values"])
    else:
        min_val = config["min"]
        max_val = config["max"]
        step = config["step"]
        if isinstance(step, float):
            return round(random.uniform(min_val, max_val), 1)
        else:
            return random.randint(min_val, max_val)

def update_values():
    """更新模拟数据值"""
    for key, config in MQTT_TOPICS.items():
        # 更新数据，有一定几率变化
        if random.random() > 0.7:  # 30%的概率更新数据
            new_value = generate_random_value(config)
            data_values[key] = new_value

def format_aqi_data(value):
    """格式化AQI数据，使用不同的格式"""
    formats = MQTT_TOPICS["aqi"].get("formats", ["raw"])
    format_type = random.choice(formats)
    
    if format_type == "raw":
        return str(value)
    elif format_type == "json":
        json_formats = [
            {"value": value},
            {"data": value},
            {"aqi": value},
            {"reading": value}
        ]
        return json.dumps(random.choice(json_formats))
    elif format_type == "string":
        return f"AQI: {value}"
    else:
        return str(value)

def send_data_periodically(client):
    """定期发送模拟数据"""
    global stop_flag
    
    while not stop_flag:
        # 更新数据值
        update_values()
        
        # 发送数据
        for topic, value in data_values.items():
            topic_str = f"siot/{topic}"
            
            # 特殊处理AQI数据，使用不同的格式
            if topic == "aqi":
                payload = format_aqi_data(value)
            else:
                payload = str(value)
                
            client.publish(topic_str, payload)
            print(f"发送: {topic_str} = {payload}")
        
        # 等待下一次发送
        time.sleep(3)

def on_connect(client, userdata, flags, rc):
    print(f"已连接到MQTT代理，结果代码: {rc}")

def signal_handler(sig, frame):
    global stop_flag
    print("\n接收到终止信号，正在关闭...")
    stop_flag = True
    time.sleep(1)  # 给线程一点时间结束
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("启动临时MQTT模拟服务器...")
    
    # 创建客户端
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mqtt_simulator")
    client.on_connect = on_connect
    
    # 连接到本地MQTT代理
    try:
        # 创建自己的MQTT服务器
        try:
            host = 'localhost'
            port = MQTT_PORT
            
            # 检查端口是否已经被占用
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((host, port))
            s.close()
            
            if result == 0:
                print(f"警告: 端口 {port} 已被占用，可能有其他MQTT代理正在运行")
            else:
                print(f"端口 {port} 可用，启动内置MQTT代理")
                # 这里可以启动内置代理，但需要额外库支持
        except:
            pass
        
        client.connect("localhost", MQTT_PORT, 60)
        client.loop_start()
        
        # 启动定期发送数据的线程
        sender_thread = threading.Thread(target=send_data_periodically, args=(client,))
        sender_thread.daemon = True
        sender_thread.start()
        
        print("MQTT模拟器已启动，按Ctrl+C退出")
        
        # 保持主线程运行
        while not stop_flag:
            time.sleep(1)
    
    except Exception as e:
        print(f"MQTT模拟器错误: {e}")
    
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("MQTT模拟器已关闭")

if __name__ == "__main__":
    main()
EOL

# 设置执行权限
chmod +x "$SCRIPT_DIR/temp_mqtt_server.py"

# 启动临时MQTT代理
echo -e "${BLUE}正在启动临时MQTT代理和数据模拟器...${NC}"
python3 "$SCRIPT_DIR/temp_mqtt_server.py" &
MQTT_PID=$!

# 等待MQTT服务器启动
echo -e "${YELLOW}等待MQTT服务器启动...${NC}"
sleep 3

# 启动仪表盘应用
echo -e "${BLUE}启动智慧校园环境监测系统...${NC}"
python3 "$SCRIPT_DIR/src/simple_dashboard.py" &
DASHBOARD_PID=$!

echo -e "${GREEN}所有服务已启动:${NC}"
echo -e "${YELLOW}- MQTT服务器和数据模拟器 (PID: $MQTT_PID)${NC}"
echo -e "${YELLOW}- 智慧校园环境监测系统 (PID: $DASHBOARD_PID)${NC}"
echo -e "${BLUE}按 Ctrl+C 终止所有服务${NC}"

# 等待用户按下Ctrl+C
trap "echo -e '\n${RED}正在关闭所有服务...${NC}'; kill $MQTT_PID 2>/dev/null; kill $DASHBOARD_PID 2>/dev/null; echo -e '${GREEN}服务已关闭${NC}'; exit 0" INT TERM

# 保持脚本运行
wait
