#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易MQTT消息转发程序
用于智慧校园仪表盘本地测试
不需要外部MQTT代理服务器
"""

import sys
import time
import socket
import logging
import argparse
import threading
import json
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
subscribers = {}  # 主题 -> 订阅者列表
clients = []  # 所有连接的客户端
lock = threading.Lock()

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
    client.publish("system/info", json.dumps({
        "message": "Connected to Python MQTT Relay",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }))

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
    sender_id = client._client_id.decode() if hasattr(client, '_client_id') else str(id(client))
    logger.info(f"收到消息: 主题={msg.topic}, QoS={msg.qos}, 发送者={sender_id}")
    
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

def create_simple_broker():
    """创建一个简易的MQTT代理服务器"""
    import socket
    import select
    import struct
    import threading
    
    # 创建服务器socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 存储连接的客户端
    clients = []
    
    # 处理客户端连接的线程
    class ClientHandler(threading.Thread):
        def __init__(self, client_sock, client_addr):
            super().__init__()
            self.client_sock = client_sock
            self.client_addr = client_addr
            self.running = True
            self.daemon = True
        
        def run(self):
            logger.info(f"客户端连接: {self.client_addr}")
            try:
                while self.running:
                    data = self.client_sock.recv(1024)
                    if not data:
                        break
                        
                    # 将消息转发给所有其他客户端
                    for client in clients:
                        if client != self.client_sock:
                            try:
                                client.send(data)
                            except:
                                pass
            except Exception as e:
                logger.error(f"处理客户端时出错: {e}")
            finally:
                if self.client_sock in clients:
                    clients.remove(self.client_sock)
                try:
                    self.client_sock.close()
                except:
                    pass
                logger.info(f"客户端断开连接: {self.client_addr}")
    
    # 简易代理类
    class SimpleServer:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.socket = server_sock
            self.running = False
            
        def start(self):
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
                self.running = True
                
                logger.info(f"MQTT简易服务器已启动，监听于 {self.host}:{self.port}")
                
                while self.running:
                    try:
                        client_sock, client_addr = self.socket.accept()
                        clients.append(client_sock)
                        handler = ClientHandler(client_sock, client_addr)
                        handler.start()
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            logger.error(f"接受连接时出错: {e}")
            
            except Exception as e:
                logger.error(f"启动服务器时出错: {e}")
                return False
            
            return True
                
        def stop(self):
            self.running = False
            for client in list(clients):
                try:
                    client.close()
                except:
                    pass
            clients.clear()
            
            try:
                self.socket.close()
            except:
                pass
            
            logger.info("MQTT简易服务器已停止")
    
    return SimpleServer

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="简易MQTT消息中继服务器")
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'主机地址 (默认: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'端口号 (默认: {DEFAULT_PORT})')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 打印欢迎信息
    print("=" * 50)
    print("     简易MQTT服务器 - 智慧校园仪表盘测试用")
    print("=" * 50)
    
    # 尝试连接MQTT代理或启动自己的代理
    try:
        print(f"尝试连接到MQTT代理 {args.host}:{args.port}...")
        
        # 创建转发客户端
        client_id = f"mqtt-relay-{int(time.time())}"
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        
        # 设置连接超时
        client.connect_async(args.host, args.port, keepalive=60)
        
        print(f"启动MQTT中继，ID: {client_id}")
        print("按Ctrl+C停止")
        
        # 启动MQTT客户端循环
        client.loop_start()
        client.loop_start()  # 在后台线程中启动网络循环
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n接收到中断，正在退出...")
    except socket.error as e:
        print(f"\n连接错误: {e}")
        print("可能无法绑定到指定地址和端口。")
        print("检查是否已有MQTT代理在运行，或尝试不同的端口。")
    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        if 'client' in locals():
            client.loop_stop()
            client.disconnect()
        print("程序已退出")

if __name__ == "__main__":
    main()
