#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据发送脚本，用于模拟传感器数据，发送到MQTT服务器
"""

import paho.mqtt.client as mqtt
import time
import random
import json
import datetime
import argparse
import base64
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import io
import threading

# --- MQTT配置 ---
MQTT_BROKER_HOST = "192.168.1.129"  # 默认MQTT服务器地址
MQTT_BROKER_PORT = 1883  # 默认MQTT服务器端口
MQTT_USERNAME = "siot"  # 默认用户名
MQTT_PASSWORD = "dfrobot"  # 默认密码
MQTT_CLIENT_ID = f"test_data_sender_{random.randint(1000, 9999)}"  # 随机客户端ID避免冲突

# --- 传感器主题 ---
# 确保这些主题与主程序中的panel_configs中的base_topic_name一致
SENSOR_TOPICS = {
    "环境温度": "siot/环境温度",
    "环境湿度": "siot/环境湿度",
    "aqi": "siot/aqi",
    "tvoc": "siot/tvoc",
    "eco2": "siot/eco2",
    "紫外线指数": "siot/紫外线指数",
    "uv风险等级": "siot/uv风险等级", 
    "噪音": "siot/噪音"
}

# 摄像头主题
CAMERA_TOPIC = "sc/camera/stream"

# 天气主题
WEATHER_TOPIC = "sc/weather/data"

# --- 传感器数据范围配置 ---
SENSOR_RANGES = {
    "环境温度": (18.0, 30.0, 0.1),  # 最小值，最大值，变化步长
    "环境湿度": (40.0, 80.0, 0.5),
    "aqi": (10, 150, 1),
    "tvoc": (100, 500, 5),
    "eco2": (400, 1500, 10),
    "紫外线指数": (0.0, 8.0, 0.1),
    "噪音": (30.0, 70.0, 0.5)
}

# UV风险等级映射
UV_LEVEL_MAP = {
    (0, 2): "低",
    (2, 5): "中",
    (5, 7): "高",
    (7, 10): "极高"
}

# 天气状况选项
WEATHER_CONDITIONS = [
    {"description": "晴朗", "icon": "01d"},
    {"description": "少云", "icon": "02d"},
    {"description": "多云", "icon": "03d"},
    {"description": "阴天", "icon": "04d"},
    {"description": "小雨", "icon": "09d"},
    {"description": "雨", "icon": "10d"},
    {"description": "雷雨", "icon": "11d"},
    {"description": "雪", "icon": "13d"},
    {"description": "雾", "icon": "50d"}
]

# 当前传感器值，全局变量用于模拟连续变化
current_values = {}


def on_connect(client, userdata, flags, rc, properties=None):
    """MQTT连接回调函数"""
    if rc == 0:
        print(f"已连接到MQTT服务器: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    else:
        print(f"无法连接到MQTT服务器，返回码: {rc}")


def init_sensor_values():
    """初始化传感器值到中间范围"""
    global current_values
    for sensor, (min_val, max_val, _) in SENSOR_RANGES.items():
        # 初始化为中间值附近的随机值
        mid = (min_val + max_val) / 2
        variation = (max_val - min_val) / 10  # 10%范围内的随机变化
        current_values[sensor] = round(random.uniform(mid - variation, mid + variation), 1)
    
    # 特别处理UV风险等级
    uv_index = current_values.get("紫外线指数", 3.0)
    current_values["uv风险等级"] = get_uv_risk_level(uv_index)


def get_uv_risk_level(uv_index):
    """根据紫外线指数获取风险等级"""
    for (lower, upper), level in UV_LEVEL_MAP.items():
        if lower <= uv_index < upper:
            return level
    return "未知"


def update_sensor_value(sensor):
    """更新单个传感器的值，模拟真实数据波动"""
    global current_values
    if sensor not in SENSOR_RANGES:
        return current_values.get(sensor, "0")
    
    min_val, max_val, step = SENSOR_RANGES[sensor]
    current = current_values.get(sensor, (min_val + max_val) / 2)
    
    # 生成-3到+3的随机步数
    steps = random.randint(-3, 3)
    new_value = current + steps * step
    
    # 确保在范围内
    new_value = max(min_val, min(new_value, max_val))
    
    # 对于温度、湿度等保留一位小数
    if isinstance(new_value, float):
        new_value = round(new_value, 1)
    
    current_values[sensor] = new_value
    
    # 特别处理：如果更新的是紫外线指数，也更新风险等级
    if sensor == "紫外线指数":
        current_values["uv风险等级"] = get_uv_risk_level(new_value)
    
    return new_value


def generate_test_image(width=640, height=480, text="烟铺小学智慧校园"):
    """生成测试图像，添加时间戳和文本"""
    # 创建彩色图像
    image = Image.new('RGB', (width, height), color=(40, 44, 52))
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体，如果失败则使用默认字体
    font = None
    try:
        # 尝试加载系统中的中文字体
        font_path = '/System/Library/Fonts/PingFang.ttc'  # macOS中文字体
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 36)
    except Exception as e:
        print(f"无法加载字体: {e}")
    
    # 获取当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 在图像上绘制信息
    # 绘制标题
    text_width = width // 2
    text_height = height // 2
    draw.text((width // 2 - text_width // 2, height // 2 - 50), text, 
             fill=(255, 255, 255), font=font)
    
    # 绘制时间戳
    timestamp_text = f"模拟摄像头 - {current_time}"
    draw.text((20, height - 40), timestamp_text, fill=(200, 200, 200), font=None)
    
    # 绘制随机颜色的小方块，模拟动态变化
    for i in range(10):
        x = random.randint(0, width - 50)
        y = random.randint(0, height - 50)
        size = random.randint(20, 50)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        draw.rectangle([x, y, x + size, y + size], fill=(r, g, b))
    
    # 转换为bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG', quality=80)
    img_bytes.seek(0)
    
    # Base64编码
    img_b64 = base64.b64encode(img_bytes.read()).decode('utf-8')
    return img_b64


def generate_weather_data():
    """生成模拟的天气数据"""
    # 随机选择天气条件
    weather_condition = random.choice(WEATHER_CONDITIONS)
    
    # 生成天气数据
    weather_data = {
        "weather": [
            {
                "description": weather_condition["description"],
                "icon": weather_condition["icon"]
            }
        ],
        "main": {
            "temp": round(random.uniform(15, 35), 1),  # 气温，单位摄氏度
            "humidity": random.randint(30, 90)  # 湿度百分比
        },
        "wind": {
            "speed": round(random.uniform(0, 10), 1)  # 风速，单位m/s
        },
        "dt": int(time.time())  # 数据时间戳
    }
    
    return weather_data


def send_sensor_data(client):
    """发送所有传感器数据"""
    for sensor, topic in SENSOR_TOPICS.items():
        value = update_sensor_value(sensor)
        print(f"发送 {sensor}: {value} 到主题 {topic}")
        client.publish(topic, str(value), qos=1)


def send_camera_data(client):
    """发送模拟摄像头数据"""
    camera_data = {
        "image": generate_test_image(),
        "timestamp": int(time.time())
    }
    print(f"发送摄像头图像数据到主题 {CAMERA_TOPIC}")
    client.publish(CAMERA_TOPIC, json.dumps(camera_data), qos=1)


def send_weather_data(client):
    """发送模拟天气数据"""
    weather_data = generate_weather_data()
    print(f"发送天气数据到主题 {WEATHER_TOPIC}: {weather_data['weather'][0]['description']}, {weather_data['main']['temp']}°C")
    client.publish(WEATHER_TOPIC, json.dumps(weather_data), qos=1)


def send_all_data_loop(client, interval=5, camera_interval=10, weather_interval=60):
    """持续发送所有类型的数据，使用不同的间隔"""
    counter = 0
    try:
        while True:
            # 每次循环都发送传感器数据
            send_sensor_data(client)
            
            # 每 camera_interval/interval 次发送一次摄像头数据
            if counter % (camera_interval // interval) == 0:
                send_camera_data(client)
            
            # 每 weather_interval/interval 次发送一次天气数据
            if counter % (weather_interval // interval) == 0:
                send_weather_data(client)
            
            counter += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("接收到中断信号，停止发送数据")
    except Exception as e:
        print(f"发送数据时出错: {e}")


def main():
    """主函数，解析命令行参数并启动数据发送"""
    parser = argparse.ArgumentParser(description='发送测试数据到MQTT服务器')
    parser.add_argument('--host', default=MQTT_BROKER_HOST, help='MQTT服务器地址')
    parser.add_argument('--port', type=int, default=MQTT_BROKER_PORT, help='MQTT服务器端口')
    parser.add_argument('--username', default=MQTT_USERNAME, help='MQTT用户名')
    parser.add_argument('--password', default=MQTT_PASSWORD, help='MQTT密码')
    parser.add_argument('--interval', type=int, default=5, help='传感器数据发送间隔（秒）')
    parser.add_argument('--camera-interval', type=int, default=10, help='摄像头数据发送间隔（秒）')
    parser.add_argument('--weather-interval', type=int, default=60, help='天气数据发送间隔（秒）')
    parser.add_argument('--sensors-only', action='store_true', help='仅发送传感器数据')
    parser.add_argument('--camera-only', action='store_true', help='仅发送摄像头数据')
    parser.add_argument('--weather-only', action='store_true', help='仅发送天气数据')
    parser.add_argument('--local', action='store_true', help='本地模式，增加调试输出和更频繁的数据更新')
    
    args = parser.parse_args()
    
    try:
        # 创建MQTT客户端并设置回调
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
        client.on_connect = on_connect
        
        # 本地模式下，可能不需要用户名和密码
        if not args.local or (args.username and args.password):
            client.username_pw_set(args.username, args.password)
        
        # 连接到MQTT服务器
        print(f"正在连接到MQTT服务器 {args.host}:{args.port}...")
        client.connect(args.host, args.port, 60)
        
        # 在后台启动网络线程
        client.loop_start()
        
        # 初始化传感器值
        init_sensor_values()
        
        # 本地模式下，减少发送间隔以加快刷新速度
        if args.local:
            print("运行在本地模式下，缩短数据发送间隔")
            args.interval = min(args.interval, 2)  # 至多2秒一次
            args.camera_interval = min(args.camera_interval, 5)  # 至多5秒一次
            args.weather_interval = min(args.weather_interval, 30)  # 至多30秒一次
        
        # 根据参数决定发送哪些数据
        if args.sensors_only:
            print("仅发送传感器数据模式")
            try:
                while True:
                    send_sensor_data(client)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("接收到中断信号，停止发送数据")
        elif args.camera_only:
            print("仅发送摄像头数据模式")
            try:
                while True:
                    send_camera_data(client)
                    time.sleep(args.camera_interval)
            except KeyboardInterrupt:
                print("接收到中断信号，停止发送数据")
        elif args.weather_only:
            print("仅发送天气数据模式")
            try:
                while True:
                    send_weather_data(client)
                    time.sleep(args.weather_interval)
            except KeyboardInterrupt:
                print("接收到中断信号，停止发送数据")
        else:
            print("完整数据发送模式")
            send_all_data_loop(client, args.interval, args.camera_interval, args.weather_interval)
        
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if 'client' in locals():
            client.loop_stop()
            client.disconnect()
            print("已断开与MQTT服务器的连接")


if __name__ == "__main__":
    # 检查PIL库是否可用
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("PIL库已加载，可以生成模拟摄像头图像")
    except ImportError:
        print("警告：PIL库未安装，无法生成模拟摄像头图像。请运行 'pip install Pillow' 进行安装。")
        sys.exit(1)
    
    main()