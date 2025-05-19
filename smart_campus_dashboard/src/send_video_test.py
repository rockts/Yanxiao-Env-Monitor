#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频测试数据发送脚本
用于智慧校园仪表盘的视频显示测试
生成模拟视频数据并发送到MQTT代理
"""

import time
import random
import math
import json
import base64
import argparse
import os
from io import BytesIO
from datetime import datetime
import paho.mqtt.client as mqtt

# 默认配置
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "sc/camera/stream"
DEFAULT_FPS = 5  # 每秒发送帧数
DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 300

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: PIL库未安装，无法生成测试图像。请运行 pip install Pillow")

def on_connect(client, userdata, flags, rc, properties=None):
    """连接回调"""
    if rc == 0:
        print(f"已连接到MQTT代理，状态码: {rc}")
    else:
        print(f"连接失败，状态码: {rc}")

def generate_test_frame(frame_number, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """生成测试视频帧"""
    if not PIL_AVAILABLE:
        return None
    
    # 创建黑色背景图像
    image = Image.new('RGB', (width, height), color=(20, 20, 40))
    draw = ImageDraw.Draw(image)
    
    # 绘制网格
    for x in range(0, width, 20):
        color = (40, 40, 80)
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    
    for y in range(0, height, 20):
        color = (40, 40, 80)
        draw.line([(0, y), (width, y)], fill=color, width=1)
    
    # 绘制随机矩形
    for _ in range(4):
        rect_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        x1 = random.randint(0, width - 80)
        y1 = random.randint(0, height - 60)
        x2 = x1 + random.randint(40, 100)
        y2 = y1 + random.randint(30, 80)
        draw.rectangle([x1, y1, x2, y2], outline=rect_color, width=2)
    
    # 绘制移动的球
    ball_x = 50 + (frame_number % 20) * 15
    if ball_x > width - 50:
        ball_x = width - 50 - (ball_x - (width - 50))
    ball_y = height // 2 + int(30 * math.sin(frame_number * 0.2))
    draw.ellipse([ball_x-15, ball_y-15, ball_x+15, ball_y+15], fill=(255, 220, 0))
    
    # 添加文本信息
    now = datetime.now().strftime("%H:%M:%S")
    text = f"测试视频 #{frame_number} - {now}"
    
    # 尝试加载字体
    font = None
    try:
        font_path = None
        if os.path.exists("/System/Library/Fonts/PingFang.ttc"):  # macOS
            font_path = "/System/Library/Fonts/PingFang.ttc"
        elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):  # Linux
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
        if font_path:
            font = ImageFont.truetype(font_path, 16)
    except Exception as e:
        print(f"字体加载失败: {e}")
    
    # 绘制文本
    text_color = (200, 200, 200)
    if font:
        draw.text((10, 10), text, font=font, fill=text_color)
    else:
        draw.text((10, 10), text, fill=text_color)
    
    # 转换为Base64编码的字符串
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode('utf-8')

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="发送模拟视频数据到MQTT")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"MQTT代理主机地址 (默认: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"MQTT代理端口 (默认: {DEFAULT_PORT})")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help=f"MQTT主题 (默认: {DEFAULT_TOPIC})")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help=f"每秒发送的帧数 (默认: {DEFAULT_FPS})")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"图像宽度 (默认: {DEFAULT_WIDTH})")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help=f"图像高度 (默认: {DEFAULT_HEIGHT})")
    
    args = parser.parse_args()
    
    if not PIL_AVAILABLE:
        print("错误: 需要PIL库来生成测试图像。请运行 pip install Pillow")
        return
    
    # 创建MQTT客户端
    client_id = f"video_test_sender_{random.randint(1000, 9999)}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect
    
    # 连接到MQTT代理
    print(f"正在连接到MQTT代理 {args.host}:{args.port}...")
    try:
        client.connect(args.host, args.port, 60)
        client.loop_start()
    except Exception as e:
        print(f"连接失败: {e}")
        return
    
    # 发送视频帧
    frame_interval = 1.0 / args.fps
    frame_number = 0
    print(f"开始发送视频数据到主题 {args.topic}, 按Ctrl+C终止...")
    
    try:
        while True:
            start_time = time.time()
            
            # 生成帧并发送
            frame_base64 = generate_test_frame(frame_number, args.width, args.height)
            if frame_base64:
                # 制作视频数据包
                video_data = {
                    "image": frame_base64,
                    "timestamp": time.time(),
                    "frame": frame_number
                }
                
                # 发布到MQTT
                client.publish(args.topic, json.dumps(video_data))
                
                frame_number += 1
                if frame_number % 10 == 0:
                    print(f"已发送 {frame_number} 帧")
            
            # 等待下一帧时间
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在退出...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("已断开连接")

if __name__ == "__main__":
    main()
