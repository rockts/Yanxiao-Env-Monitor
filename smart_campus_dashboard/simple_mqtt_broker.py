#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简MQTT代理模拟器
用于智慧校园仪表盘本地测试
"""

import os
import sys
import time
import socket
import select
import logging
import argparse
import threading
import subprocess
from datetime import datetime

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
running = True
topics = {}  # 主题 -> 最新消息
clients = {}  # socket -> 客户端信息
lock = threading.Lock()

class MQTTProxyServer:
    """简易的MQTT代理服务器，转发消息"""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """初始化服务器"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}  # 客户端连接 socket -> 信息
        self.topics = {}   # 主题 -> 最新消息
        self.subscribers = {}  # 主题 -> 订阅者列表
        
    def start(self):
        """启动服务器"""
        try:
            # 创建服务器socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置选项，方便调试时重用地址和端口
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定地址和端口
            self.server_socket.bind((self.host, self.port))
            # 开始监听连接
            self.server_socket.listen(5)
            # 设置非阻塞模式
            self.server_socket.settimeout(1.0)
            
            logger.info(f"MQTT代理服务器已启动，监听于 {self.host}:{self.port}")
            print(f"MQTT代理服务器已启动，监听于 {self.host}:{self.port}")
            
            self.running = True
            # 运行消息处理循环
            self._run_server_loop()
            
            return True
        
        except Exception as e:
            logger.error(f"启动MQTT代理服务器失败: {e}")
            print(f"启动MQTT代理服务器失败: {e}")
            return False
    
    def stop(self):
        """停止服务器"""
        self.running = False
        logger.info("正在停止MQTT代理服务器...")
        
        # 关闭所有客户端连接
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        # 关闭服务器socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("MQTT代理服务器已停止")
    
    def _run_server_loop(self):
        """运行服务器主循环"""
        try:
            while self.running:
                try:
                    # 尝试接受新的客户端连接
                    client_socket, client_address = self.server_socket.accept()
                    # 客户端连接成功
                    logger.info(f"客户端连接: {client_address}")
                    # 添加到客户端列表
                    self.clients[client_socket] = {
                        'address': client_address,
                        'connected_at': datetime.now(),
                        'subscriptions': []
                    }
                    
                    # 创建一个新线程处理这个客户端
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    # 超时是正常的，继续循环
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"接受客户端连接时出错: {e}")
        
        except KeyboardInterrupt:
            logger.info("接收到键盘中断，停止服务器")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket, client_address):
        """处理单个客户端连接"""
        try:
            # 设置socket为非阻塞
            client_socket.setblocking(False)
            
            # 处理循环
            buffer = bytearray()
            
            while self.running:
                try:
                    # 尝试从客户端读取数据
                    ready = select.select([client_socket], [], [], 0.5)
                    if ready[0]:
                        data = client_socket.recv(1024)
                        if not data:
                            # 客户端断开连接
                            break
                        
                        # 将数据添加到缓冲区
                        buffer.extend(data)
                        
                        # TODO: 解析MQTT协议包，现在只是简单地存储并转发
                        # 这里只是最基本的功能，不实现完整的MQTT协议
                        
                        # 转发此消息给其他客户端
                        self._broadcast_message(client_socket, buffer)
                        
                        # 清空缓冲区，准备接收新数据
                        buffer.clear()
                
                except Exception as e:
                    logger.error(f"处理客户端 {client_address} 时出错: {e}")
                    break
        
        finally:
            # 客户端连接结束
            logger.info(f"客户端断开连接: {client_address}")
            
            # 从客户端列表中移除
            if client_socket in self.clients:
                del self.clients[client_socket]
            
            # 关闭socket
            try:
                client_socket.close()
            except:
                pass
    
    def _broadcast_message(self, sender_socket, message):
        """广播消息给所有其他客户端"""
        for client_socket in list(self.clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.send(message)
                except:
                    # 如果发送失败，移除此客户端
                    if client_socket in self.clients:
                        del self.clients[client_socket]
                    try:
                        client_socket.close()
                    except:
                        pass
    
    try:
        await broker.start()
        logger.info(f"MQTT代理已启动，监听于 {host}:{port}")
        
        # 保持运行，直到被中断
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭MQTT代理...")
    except Exception as e:
        logger.error(f"启动MQTT代理时出错: {e}")
    finally:
        await broker.shutdown()
        logger.info("MQTT代理已关闭")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="简易MQTT代理服务器")
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'主机地址 (默认: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'端口号 (默认: {DEFAULT_PORT})')
    
    args = parser.parse_args()
    
    print(f"启动MQTT代理服务器于 {args.host}:{args.port}")
    print("按Ctrl+C停止服务器")
    
    try:
        asyncio.run(start_broker(args.host, args.port))
    except KeyboardInterrupt:
        print("\nMQTT代理服务器已停止")
