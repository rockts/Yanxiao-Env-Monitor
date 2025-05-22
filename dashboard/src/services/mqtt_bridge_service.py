#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易MQTT桥接器
用于智慧校园仪表盘本地测试
桥接不同的MQTT客户端以便于开发测试
"""

import sys
import time
import socket
import logging
import argparse
import threading
import json
import random
import os
import math  # 添加math模块
import base64  # 添加base64模块用于图像编码
from paho.mqtt import client as mqtt

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 1883

# 全局变量
topics = {}  # 主题 -> 最后的消息
topic_subscribers = {}  # 主题 -> 订阅者列表
clients = []  # 所有连接的客户端
lock = threading.Lock()
message_count = 0  # 消息计数

# MQTT客户端回调函数
def on_connect(client, userdata, flags, rc, properties=None):
    """当客户端连接到代理时的回调"""
    client_id = client._client_id.decode() if hasattr(client, '_client_id') else str(id(client))
    logger.info(f"客户端连接: {client_id}, 状态: {rc}")
    
    # 记录客户端
    with lock:
        if client not in clients:
            clients.append(client)
    
    # 让客户端订阅所有主题
    client.subscribe("#")  # 订阅所有主题
    
    # 发送欢迎消息
    try:
        client.publish("system/info", json.dumps({
            "message": "Connected to Python MQTT Relay",
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }))
    except Exception as e:
        logger.error(f"发送欢迎消息时出错: {e}")

def on_disconnect(client, userdata, rc, properties=None):
    """当客户端断开连接时的回调"""
    client_id = client._client_id.decode() if hasattr(client, '_client_id') else str(id(client))
    logger.info(f"客户端断开: {client_id}, 状态: {rc}")
    
    # 移除客户端
    with lock:
        if client in clients:
            clients.remove(client)

def on_message(client, userdata, msg):
    """当收到消息时的回调"""
    global message_count
    message_count += 1
    
    sender_id = client._client_id.decode() if hasattr(client, '_client_id') else str(id(client))
    # 只输出前30个字符的payload，以避免日志过长
    try:
        payload_preview = msg.payload.decode('utf-8')[:30]
    except:
        payload_preview = str(msg.payload)[:30] + "... (binary)"
    
    # 每收到100条消息才记录一次日志，避免过多输出
    if message_count % 100 == 1:
        logger.info(f"收到消息 #{message_count}: 主题={msg.topic}, 内容预览={payload_preview}...")
    
    # 存储消息
    with lock:
        topics[msg.topic] = msg.payload
    
    # 转发给其他客户端
    forward_message(client, msg)

def forward_message(sender, msg):
    """将消息转发给除发送者外的所有连接的客户端"""
    with lock:
        for client in clients:
            if client != sender:  # 不要转发给原始发送者
                try:
                    client.publish(msg.topic, msg.payload, qos=msg.qos)
                except Exception as e:
                    logger.error(f"转发消息时出错: {e}")

def generate_test_image(index=0, size=(320, 240)):
    """
    生成一个用于测试的图像数据
    返回base64编码的字符串
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建一个图像对象
        width, height = size
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制测试图案
        for i in range(0, width, 20):
            # 绘制垂直线
            draw.line([(i, 0), (i, height)], fill=(30, 30, 80), width=1)
        
        for j in range(0, height, 20):
            # 绘制水平线
            draw.line([(0, j), (width, j)], fill=(30, 30, 80), width=1)
        
        # 绘制一些随机彩色矩形
        for _ in range(5):
            rect_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            rect_x = random.randint(0, width-80)
            rect_y = random.randint(0, height-60)
            rect_width = random.randint(30, 80)
            rect_height = random.randint(20, 60)
            draw.rectangle([rect_x, rect_y, rect_x+rect_width, rect_y+rect_height], 
                          outline=rect_color, fill=None, width=2)
        
        # 绘制当前时间和索引号
        current_time = time.strftime("%H:%M:%S")
        text = f"测试视频 #{index} - {current_time}"
        
        # 简单字体处理
        try:
            # 尝试加载系统字体，根据操作系统调整
            font_path = None
            if os.path.exists("/System/Library/Fonts/PingFang.ttc"):  # macOS
                font_path = "/System/Library/Fonts/PingFang.ttc"
            elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):  # Linux
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
            if font_path:
                font = ImageFont.truetype(font_path, 16)
                draw.text((10, 10), text, fill=(200, 200, 200), font=font)
            else:
                # 如果没有找到合适的字体，使用默认
                draw.text((10, 10), text, fill=(200, 200, 200))
        except Exception as e:
            # 如果字体处理出错，直接使用默认
            logger.error(f"字体处理出错: {e}")
            draw.text((10, 10), text, fill=(200, 200, 200))
        
        # 添加一个移动的小球，让图像看起来有变化
        ball_x = 50 + (index % 30) * 8
        if ball_x > width - 50:
            ball_x = width - 50 - (ball_x - (width - 50))
        ball_y = 120 + int(20 * math.sin(index * 0.2))
        draw.ellipse([ball_x-10, ball_y-10, ball_x+10, ball_y+10], fill=(255, 255, 0))
        
        # 将图像转换为base64编码的字符串
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return image_b64
    except ImportError:
        logger.error("生成测试图像需要PIL库，请安装: pip install Pillow")
        # 返回一个基本提示消息
        return ""
    except Exception as e:
        logger.error(f"生成测试图像出错: {e}")
        return ""

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="简易MQTT桥接器")
    parser.add_argument("--host", default=DEFAULT_HOST, help="MQTT代理主机地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MQTT代理端口")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--test", action="store_true", help="测试模式，发送模拟消息")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 打印欢迎信息
    print("=" * 60)
    print("     简易MQTT桥接器 - 智慧校园仪表盘测试用")
    print("=" * 60)
    print(f"连接到MQTT代理: {args.host}:{args.port}")
    print("按Ctrl+C停止")
    print("-" * 60)
    
    # 创建MQTT客户端
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"mqtt-bridge-{int(time.time())}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    try:
        # 连接到MQTT代理
        client.connect(args.host, args.port, keepalive=60)
        client.loop_start()  # 在后台线程中启动网络循环
        
        if args.test:
            # 测试模式：每隔5秒发送模拟传感器数据
            print("测试模式：开始发送模拟数据...")
            
            topics_to_simulate = [
                "siot/环境温度",
                "siot/环境湿度",
                "siot/aqi",
                "siot/tvoc",
                "siot/eco2",
                "siot/紫外线指数",
                "siot/uv风险等级",
                "siot/噪音",
                "siot/视频测试"  # 添加视频测试主题
            ]
            
            sensor_values = {
                "siot/环境温度": 25.0,
                "siot/环境湿度": 60.0,
                "siot/aqi": 50,
                "siot/tvoc": 200,
                "siot/eco2": 800,
                "siot/紫外线指数": 4.5,
                "siot/uv风险等级": 2,
                "siot/噪音": 45
            }
            
            try:
                video_index = 0
                while True:
                    # 模拟数据的微小变化
                    sensor_values["siot/环境温度"] += (0.5 - random.random())
                    sensor_values["siot/环境湿度"] += (0.5 - random.random())
                    sensor_values["siot/aqi"] += int(5 - random.random() * 10)
                    sensor_values["siot/tvoc"] += int(10 - random.random() * 20)
                    sensor_values["siot/eco2"] += int(20 - random.random() * 40)
                    sensor_values["siot/紫外线指数"] += (0.2 - random.random() * 0.4)
                    sensor_values["siot/uv风险等级"] = max(0, min(4, sensor_values["siot/uv风险等级"] + (0.5 - random.random())))
                    sensor_values["siot/噪音"] += (2 - random.random() * 4)
                    
                    # 限制在合理范围内
                    sensor_values["siot/环境温度"] = max(15, min(35, sensor_values["siot/环境温度"]))
                    sensor_values["siot/环境湿度"] = max(30, min(90, sensor_values["siot/环境湿度"]))
                    sensor_values["siot/aqi"] = max(10, min(300, sensor_values["siot/aqi"]))
                    sensor_values["siot/tvoc"] = max(100, min(1000, sensor_values["siot/tvoc"]))
                    sensor_values["siot/eco2"] = max(400, min(2000, sensor_values["siot/eco2"]))
                    sensor_values["siot/紫外线指数"] = max(0, min(10, sensor_values["siot/紫外线指数"]))
                    sensor_values["siot/噪音"] = max(30, min(85, sensor_values["siot/噪音"]))
                    
                    # 发布数据
                    for topic in topics_to_simulate:
                        value = sensor_values[topic]
                        if isinstance(value, float):
                            value_str = f"{value:.1f}"
                        else:
                            value_str = str(value)
                        client.publish(topic, value_str)
                    
                    # 发送测试视频数据
                    test_image = generate_test_image(video_index)
                    client.publish("siot/视频测试", test_image)
                    video_index += 1
                    
                    time.sleep(5)
            except KeyboardInterrupt:
                print("测试模式停止")
            except Exception as e:
                print(f"测试模式出错: {e}")
        else:
            # 正常模式：只转发消息
            try:
                # 保持主线程运行
                while True:
                    time.sleep(1)
                    
                    # 每10秒显示一次状态
                    if int(time.time()) % 10 == 0:
                        with lock:
                            num_topics = len(topics)
                            topic_list = list(topics.keys())
                        
                        print(f"MQTT桥接状态: 已处理 {message_count} 条消息，{num_topics} 个主题")
                        if topic_list and len(topic_list) <= 5:
                            print(f"活跃主题: {', '.join(topic_list)}")
                        time.sleep(1)  # 避免多次打印同一秒
            except KeyboardInterrupt:
                print("\n接收到中断，正在退出...")
    
    except socket.error as e:
        print(f"\n连接错误: {e}")
        print("无法连接到MQTT代理。请确认代理是否正在运行，以及地址和端口是否正确。")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)
    finally:
        # 清理
        if 'client' in locals():
            client.loop_stop()
            client.disconnect()
        print("\n已断开连接，程序退出")

if __name__ == "__main__":
    # 导入这里以避免不必要的依赖
    import random
    main()
