#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 简单工作版仪表盘
这是一个简化但功能完整的版本，专注于显示传感器数据
"""

import os
import sys
import time
import datetime
import threading
import logging
import random
import json
import math
import traceback
import base64
from pathlib import Path
from io import BytesIO

import tkinter as tk
from tkinter import ttk, font
import paho.mqtt.client as mqtt

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL库未安装，视频流功能将不可用。请运行 pip install Pillow")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("simple_dashboard")

# 全局变量和常量
MQTT_BROKER_HOST = "192.168.1.129"  # 改为"localhost"如果使用本地MQTT服务器
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "simple_dashboard_client"
MQTT_USERNAME = "siot"
MQTT_PASSWORD = "dfrobot"
MQTT_TOPICS = [
    "siot/环境温度", "siot/环境湿度", "siot/aqi", 
    "siot/tvoc", "siot/eco2", "siot/紫外线指数", 
    "siot/uv风险等级", "siot/噪音",
    "sc/camera/stream",  # 标准视频流主题
    "siot/摄像头"  # 烟铺小学特定的摄像头主题
]

# UI相关常量
WINDOW_TITLE = "智慧校园环境监测系统 - 简单工作版"
WINDOW_SIZE = "800x600"
BG_COLOR = "#1E1E1E"  # 深灰色背景
TEXT_COLOR = "#FFFFFF"  # 白色文字
PANEL_BG = "#2D2D2D"  # 稍浅的灰色作为面板背景
ACCENT_COLOR = "#4CAF50"  # 绿色强调色

# 模拟数据
SIMULATION_DATA = {
    "环境温度": "25.6",
    "环境湿度": "68.2",
    "aqi": "52",
    "tvoc": "320",
    "eco2": "780",
    "紫外线指数": "2.8",
    "uv风险等级": "低",
    "噪音": "45.5"
}

# 传感器配置
SENSOR_CONFIG = {
    "环境温度": {"display": "温度", "unit": "°C", "icon": "🌡️"},
    "环境湿度": {"display": "湿度", "unit": "%RH", "icon": "💧"},
    "aqi": {"display": "AQI", "unit": "", "icon": "💨"},
    "tvoc": {"display": "TVOC", "unit": "ppb", "icon": "🧪"},
    "eco2": {"display": "eCO2", "unit": "ppm", "icon": "🌿"},
    "紫外线指数": {"display": "紫外线指数", "unit": "", "icon": "☀️"},
    "uv风险等级": {"display": "UV风险", "unit": "", "icon": "⚠️"},
    "噪音": {"display": "噪音", "unit": "dB", "icon": "🔊"}
}

class SimpleDashboard:
    """简单但功能完整的仪表盘实现"""
    
    def __init__(self, root):
        """初始化仪表盘"""
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.config(bg=BG_COLOR)
        
        # 初始化变量
        self.mqtt_client = None
        self.use_simulation = False
        self.sensor_values = {topic.split('/')[-1]: "--" for topic in MQTT_TOPICS}
        self.sensor_labels = {}
        self.sensor_value_labels = {}
        self.simulation_thread = None
        self.connected = False
        self.last_update_time = {}
        
        # 视频相关变量
        self.video_frame = None
        self.video_label = None
        self.video_enabled = PIL_AVAILABLE
        self.video_simulation_active = False
        self.frame_count = 0
        
        # UI初始化
        self.setup_ui()
        
        # 添加窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 连接MQTT
        self.setup_mqtt()
        
        # 启动时钟更新
        self.update_clock()
        
        logger.info("仪表盘初始化完成")
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建标题栏
        title_frame = tk.Frame(self.root, bg=BG_COLOR, height=60)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(
            title_frame, 
            text="烟铺小学智慧校园环境监测系统",
            font=("Arial", 20, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # 时钟
        self.clock_var = tk.StringVar(value="00:00:00")
        clock_label = tk.Label(
            title_frame,
            textvariable=self.clock_var,
            font=("Arial", 14),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        clock_label.pack(side=tk.RIGHT, padx=10)
        
        # 创建主内容区，左侧传感器，右侧视频
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧传感器数据区域
        sensors_frame = tk.Frame(main_frame, bg=BG_COLOR)
        sensors_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 右侧视频区域
        if self.video_enabled:
            # 视频区域
            video_frame = tk.Frame(main_frame, bg=PANEL_BG, bd=1, relief=tk.RAISED)
            video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 视频标题
            video_title = tk.Label(
                video_frame,
                text="📹 实时监控",
                font=("Arial", 14, "bold"),
                bg=PANEL_BG,
                fg=TEXT_COLOR
            )
            video_title.pack(anchor=tk.N, padx=10, pady=5)
            
            # 视频显示区域
            self.video_label = tk.Label(video_frame, bg="black")
            self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 添加"无视频信号"文本
            self.video_label.config(text="等待视频信号...", fg="white", font=("Arial", 14))
            
            # 视频状态显示
            self.video_status_var = tk.StringVar(value="未连接")
            self.video_status_label = tk.Label(
                video_frame,
                textvariable=self.video_status_var,
                bg=PANEL_BG,
                fg="orange",
                font=("Arial", 10)
            )
            self.video_status_label.pack(anchor=tk.S, pady=5)
            
            # 存储上一帧的时间戳
            self.last_frame_time = None
            
            self.video_frame = video_frame
        
        # 创建网格布局
        for i, sensor_key in enumerate(SENSOR_CONFIG.keys()):
            row, col = divmod(i, 3)
            
            # 传感器面板
            panel = tk.Frame(
                sensors_frame,
                bg=PANEL_BG,
                bd=1,
                relief=tk.RAISED,
                height=120,
                width=200
            )
            panel.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            panel.grid_propagate(False)  # 固定大小
            
            # 传感器标题
            config = SENSOR_CONFIG[sensor_key]
            title_text = f"{config['icon']} {config['display']}"
            sensor_label = tk.Label(
                panel,
                text=title_text,
                font=("Arial", 14),
                bg=PANEL_BG,
                fg=TEXT_COLOR
            )
            sensor_label.pack(anchor=tk.NW, padx=10, pady=(10, 5))
            self.sensor_labels[sensor_key] = sensor_label
            
            # 传感器数值
            value_frame = tk.Frame(panel, bg=PANEL_BG)
            value_frame.pack(fill=tk.X, padx=10, pady=5)
            
            value_label = tk.Label(
                value_frame,
                text="--",
                font=("Arial", 24, "bold"),
                bg=PANEL_BG,
                fg=ACCENT_COLOR
            )
            value_label.pack(side=tk.LEFT, padx=5)
            self.sensor_value_labels[sensor_key] = value_label
            
            # 单位
            if config["unit"]:
                unit_label = tk.Label(
                    value_frame,
                    text=config["unit"],
                    font=("Arial", 12),
                    bg=PANEL_BG,
                    fg=TEXT_COLOR
                )
                unit_label.pack(side=tk.LEFT, padx=0, pady=0, anchor=tk.S)
        
        # 设置网格权重
        for i in range(3):
            sensors_frame.columnconfigure(i, weight=1)
        for i in range(3):
            sensors_frame.rowconfigure(i, weight=1)
        
        # 底部状态栏
        status_frame = tk.Frame(self.root, bg=BG_COLOR, height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # MQTT连接状态
        self.mqtt_status_var = tk.StringVar(value="未连接")
        mqtt_status = tk.Label(
            status_frame,
            textvariable=self.mqtt_status_var,
            font=("Arial", 10),
            bg=BG_COLOR,
            fg="#FF6666"  # 红色表示未连接
        )
        mqtt_status.pack(side=tk.LEFT)
        
        # 模拟数据切换按钮
        self.sim_button_text = tk.StringVar(value="启用模拟数据")
        sim_button = tk.Button(
            status_frame,
            textvariable=self.sim_button_text,
            command=self.toggle_simulation,
            font=("Arial", 10),
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground=TEXT_COLOR
        )
        sim_button.pack(side=tk.RIGHT)
        
        # 视频模拟按钮（如果视频功能启用）
        if self.video_enabled:
            self.video_sim_button_text = tk.StringVar(value="启用视频模拟")
            video_sim_button = tk.Button(
                status_frame,
                textvariable=self.video_sim_button_text,
                command=self.toggle_video_simulation,
                font=("Arial", 10),
                bg=PANEL_BG,
                fg=TEXT_COLOR,
                activebackground=ACCENT_COLOR,
                activeforeground=TEXT_COLOR
            )
            video_sim_button.pack(side=tk.RIGHT, padx=10)
    
    def setup_mqtt(self):
        """设置MQTT客户端"""
        try:
            # 创建MQTT客户端
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            
            # 设置回调
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            # 设置认证
            self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
            # 尝试连接
            logger.info(f"正在连接MQTT服务器: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            self.mqtt_client.connect_async(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            
            # 启动MQTT循环
            self.mqtt_client.loop_start()
            
        except Exception as e:
            logger.error(f"MQTT连接错误: {e}")
            self.update_mqtt_status("连接失败", False)
            # 默认启用模拟数据
            self.toggle_simulation()
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT连接成功回调"""
        if rc == 0:
            logger.info("已连接到MQTT服务器")
            self.connected = True
            self.update_mqtt_status("已连接", True)
            
            # 订阅主题
            for topic in MQTT_TOPICS:
                self.mqtt_client.subscribe(topic)
            logger.info(f"已订阅主题: {MQTT_TOPICS}")
        else:
            logger.error(f"MQTT连接失败, 返回码: {rc}")
            self.connected = False
            self.update_mqtt_status(f"连接失败 ({rc})", False)
            
            # 默认启用模拟数据
            if not self.use_simulation:
                self.toggle_simulation()
    
    def on_message(self, client, userdata, msg):
        """MQTT消息接收回调"""
        try:
            topic = msg.topic
            
            # 如果是视频流数据
            if (topic == "sc/camera/stream" or topic == "siot/摄像头") and self.video_enabled:
                # 记录视频流数据信息，但不打印完整数据以避免日志过大
                payload_size = len(msg.payload)
                payload_type = type(msg.payload).__name__
                sample = ""
                
                # 检测是否以data:image开头
                is_data_url = False
                if isinstance(msg.payload, bytes) and payload_size > 20:
                    if msg.payload[:20].decode('utf-8', errors='ignore').startswith('data:image/'):
                        is_data_url = True
                        header_sample = "数据URL格式：" + msg.payload[:30].decode('utf-8', errors='ignore')
                        sample = f"前20字节(Hex): {msg.payload[:20].hex()}, {header_sample}"
                    else:
                        sample = f"前20字节(Hex): {msg.payload[:20].hex()}"
                
                if is_data_url:
                    logger.info(f"接收到视频帧(数据URL): 主题={topic}, 类型={payload_type}, 大小={payload_size}字节, {sample}")
                else:
                    logger.info(f"接收到视频帧: 主题={topic}, 类型={payload_type}, 大小={payload_size}字节, {sample}")
                
                # 处理视频数据
                self.process_video_frame(msg.payload)
                return
                
            # 解码传感器数据消息
            payload = msg.payload.decode('utf-8')
            sensor_name = topic.split('/')[-1]  # 从主题中提取传感器名称
            
            logger.info(f"接收到消息: {topic} = {payload}")
            
            # 保存传感器数值
            self.sensor_values[sensor_name] = payload
            self.last_update_time[sensor_name] = datetime.datetime.now()
            
            # 更新UI
            if sensor_name in self.sensor_value_labels:
                self.sensor_value_labels[sensor_name].config(text=payload)
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            
    def update_video_status(self, status, success=True):
        """更新视频状态信息"""
        if hasattr(self, 'video_status_var'):
            now = datetime.datetime.now().strftime("%H:%M:%S")
            color = "green" if success else "red"
            self.video_status_var.set(f"{status} ({now})")
            if hasattr(self, 'video_status_label'):
                self.video_status_label.config(fg=color)
    
    def process_video_frame(self, payload):
        """处理视频帧数据"""
        if not PIL_AVAILABLE or not self.video_label:
            return
            
        try:
            img_data = None
            decode_method = "未知"
            
            # 检查是否是data:image/png;base64格式的数据URL
            data_url_detected = False
            
            # 先检查是否是bytes类型
            if isinstance(payload, bytes):
                # 检查是否以data:image/开头 (转换为hex查看前几个字节)
                if len(payload) > 10 and payload[:10].hex().startswith('646174613a696d'):
                    # 可能是data:image/ 开头的数据
                    try:
                        payload_str = payload.decode('utf-8', errors='ignore')
                        if payload_str.startswith('data:image/'):
                            data_url_detected = True
                            logger.info("检测到二进制data URL格式")
                    except:
                        pass
                
                # 如果检测到是data URL格式，尝试解析
                if data_url_detected:
                    try:
                        payload_str = payload.decode('utf-8', errors='ignore')
                        # 提取base64部分
                        base64_data = payload_str.split(',', 1)
                        if len(base64_data) >= 2:
                            logger.info(f"data URL格式: {base64_data[0]},...")
                            img_data = base64.b64decode(base64_data[1])
                            decode_method = "data URL解码"
                            logger.info(f"成功从data URL中解码图像数据，长度: {len(img_data)} 字节")
                        else:
                            logger.warning("data URL格式无效：未找到base64数据部分")
                            data_url_detected = False
                    except Exception as e:
                        logger.warning(f"解码data URL失败: {e}")
                        data_url_detected = False  # 重置标志以尝试其他方法
            
            # 如果是字符串，直接检查是否为data URL
            elif isinstance(payload, str) and payload.startswith('data:image/'):
                data_url_detected = True
                logger.info("检测到字符串data URL格式")
                try:
                    # 提取base64部分
                    base64_data = payload.split(',', 1)
                    if len(base64_data) >= 2:
                        img_data = base64.b64decode(base64_data[1])
                        decode_method = "data URL解码"
                        logger.info("成功从字符串data URL中解码图像数据")
                    else:
                        logger.warning("data URL格式无效：未找到base64数据部分")
                        data_url_detected = False
                except Exception as e:
                    logger.warning(f"解码data URL失败: {e}")
                    data_url_detected = False  # 重置标志以尝试其他方法
            
            # 如果不是data URL或解码失败，则尝试其他方法
            if not data_url_detected:
                # 第一步：尝试将payload解析为JSON
                try:
                    # 如果是字节串，先转换为字符串
                    if isinstance(payload, bytes):
                        payload_str = payload.decode('utf-8', errors='ignore')
                    else:
                        payload_str = payload
                        
                    data = json.loads(payload_str)
                    if "image" in data:
                        # 解码base64图像数据
                        img_data = base64.b64decode(data["image"])
                        decode_method = "JSON+Base64"
                        logger.info("成功从JSON中提取图像数据")
                    else:
                        logger.warning("JSON数据中没有找到'image'字段")
                        self.update_video_status("JSON格式错误", False)
                        return
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 第二步：如果不是JSON，尝试作为Base64编码或原始数据处理
                    logger.info("非JSON数据，尝试其他解码方式")
                    
                    if isinstance(payload, bytes):
                        # 尝试直接作为图像数据使用
                        try:
                            img_data = payload
                            decode_method = "原始字节"
                            logger.info("使用原始字节数据作为图像")
                        except Exception as e1:
                            logger.warning(f"直接使用字节数据失败: {e1}")
                            
                            # 尝试将字节转为字符串，然后Base64解码
                            try:
                                payload_str = payload.decode('utf-8', errors='ignore')
                                img_data = base64.b64decode(payload_str)
                                decode_method = "字节转字符串+Base64"
                                logger.info("从字节字符串中解码Base64图像")
                            except Exception as e2:
                                logger.warning(f"从字节解码Base64失败: {e2}")
                                # 仍然使用原始字节
                                img_data = payload
                    else:
                        # 如果是字符串，尝试作为Base64解码
                        try:
                            img_data = base64.b64decode(payload)
                            decode_method = "纯Base64"
                            logger.info("从字符串中解码Base64图像")
                        except Exception as e3:
                            logger.warning(f"Base64解码字符串失败: {e3}")
                            img_data = payload
                            decode_method = "未处理数据"
            
            # 检查是否成功获取图像数据
            if img_data is None:
                logger.error("无法从消息中提取图像数据")
                self.update_video_status("提取图像数据失败", False)
                return
            
            # 尝试打开图像
            success = False
            
            # 方法1: 标准PIL打开方式
            try:
                from PIL import ImageFile
                ImageFile.LOAD_TRUNCATED_IMAGES = True  # 允许处理不完整的图像
                
                # 记录图像数据前几个字节以便调试
                if img_data and len(img_data) > 8:
                    logger.info(f"图像数据前8个字节: {img_data[:8].hex()}")
                
                image_buffer = BytesIO(img_data)
                
                # 检查是否是PNG格式（PNG文件以89 50 4E 47开头）
                is_png = False
                if len(img_data) > 4 and img_data[:4] == b'\x89PNG':
                    is_png = True
                    logger.info("检测到PNG图像数据")
                
                # 检查是否是JPEG格式（JPEG文件通常以FF D8开头）
                is_jpeg = False
                if len(img_data) > 2 and img_data[:2] == b'\xFF\xD8':
                    is_jpeg = True
                    logger.info("检测到JPEG图像数据")
                
                img = Image.open(image_buffer)
                img.load()  # 强制加载数据
                
                logger.info(f"标准方式成功打开图像: 格式={img.format}, 大小={img.size}")
                
                # 调整图像大小
                img = self.resize_image(img, (300, 225))
                tk_img = ImageTk.PhotoImage(img)
                
                # 更新显示
                self.video_label.config(image=tk_img, text="")
                self.video_label.image = tk_img
                self.update_video_status(f"标准解码成功 ({decode_method})", True)
                return
            except Exception as e1:
                logger.warning(f"标准PIL方式打开图像失败: {e1}")
            
            # 方法2: 添加JPEG头信息
            try:
                # 检查数据前几个字节，如果不是JPEG头则添加
                if len(img_data) > 3 and not (img_data[0:3] == b'\xff\xd8\xff' or img_data[0:2] == b'\xff\xd8'):
                    # 添加JPEG文件头
                    img_data_fixed = b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00' + img_data
                else:
                    img_data_fixed = img_data
                
                # 尝试加载
                image_buffer = BytesIO(img_data_fixed)
                img = Image.open(image_buffer)
                img.load()
                
                logger.info("通过添加JPEG头成功打开图像")
                
                # 调整图像大小
                img = self.resize_image(img, (300, 225))
                tk_img = ImageTk.PhotoImage(img)
                
                # 更新显示
                self.video_label.config(image=tk_img, text="")
                self.video_label.image = tk_img
                self.update_video_status(f"JPEG头修复成功 ({decode_method})", True)
                return
            except Exception as e2:
                logger.warning(f"添加JPEG头方式失败: {e2}")
            
            # 方法3: 尝试作为原始RGB/RGBA数据
            try:
                if isinstance(img_data, bytes):
                    data_len = len(img_data)
                    
                    # 尝试常见的分辨率
                    for (w, h, c) in [(320, 240, 3), (640, 480, 3), (160, 120, 3), 
                                     (320, 240, 4), (640, 480, 4), (160, 120, 4)]:
                        if w * h * c == data_len:
                            try:
                                # 尝试安全导入numpy
                                import numpy as np
                                arr = np.frombuffer(img_data, dtype=np.uint8).reshape(h, w, c)
                                if c == 4:
                                    arr = arr[:,:,:3]  # 只取RGB通道
                                img = Image.fromarray(arr, 'RGB')
                                
                                logger.info(f"通过原始像素方式成功解析图像: {w}x{h}")
                                
                                # 调整大小并显示
                                img = self.resize_image(img, (300, 225))
                                tk_img = ImageTk.PhotoImage(img)
                                self.video_label.config(image=tk_img, text="")
                                self.video_label.image = tk_img
                                self.update_video_status(f"原始像素解析成功 ({w}x{h})", True)
                                return
                            except ImportError:
                                logger.warning("未安装NumPy，无法使用原始像素解析方法")
                                break
                            except Exception as np_err:
                                logger.warning(f"尝试{w}x{h}x{c}分辨率失败: {np_err}")
            except Exception as e3:
                logger.warning(f"原始像素方式失败: {e3}")
            
            # 所有方法都失败了
            logger.error("所有图像解析方法均失败")
            self.update_video_status("图像解析失败", False)
            self.video_label.config(image="", text="图像解析错误\n请检查视频源", fg="red")
            
        except Exception as e:
            logger.error(f"处理视频帧时出错: {e}")
            self.update_video_status(f"处理错误: {str(e)[:30]}", False)
            logger.error(traceback.format_exc())
            
    def resize_image(self, img, target_size):
        """调整图像大小，保持宽高比"""
        # 获取原始尺寸
        width, height = img.size
        
        # 计算目标尺寸，保持宽高比
        target_width, target_height = target_size
        ratio = min(target_width / width, target_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # 调整图像大小
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=0):
        """MQTT断开连接回调"""
        logger.warning(f"MQTT连接已断开, 返回码: {rc}")
        self.connected = False
        self.update_mqtt_status("已断开", False)
        
        # 尝试重新连接
        if not self.use_simulation:
            logger.info("10秒后尝试重新连接...")
            threading.Timer(10.0, self.reconnect).start()
    
    def reconnect(self):
        """尝试重新连接MQTT"""
        if not self.connected and not self.use_simulation:
            try:
                logger.info("正在重新连接MQTT服务器...")
                self.mqtt_client.reconnect()
            except Exception as e:
                logger.error(f"重新连接失败: {e}")
                # 10秒后再次尝试
                threading.Timer(10.0, self.reconnect).start()
    
    def update_mqtt_status(self, status, is_connected):
        """更新MQTT连接状态显示"""
        self.mqtt_status_var.set(f"MQTT状态: {status}")
        if is_connected:
            color = "#33FF99"  # 绿色表示已连接
        else:
            color = "#FF6666"  # 红色表示未连接或错误
        
        # 查找状态标签并更新颜色
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_y() > 500:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "MQTT状态" in child.cget("text"):
                        child.config(fg=color)
    
    def toggle_simulation(self):
        """切换是否使用模拟数据"""
        self.use_simulation = not self.use_simulation
        
        if self.use_simulation:
            logger.info("已启用模拟数据模式")
            self.sim_button_text.set("关闭模拟数据")
            self.update_mqtt_status("使用模拟数据", False)
            
            # 使用模拟数据更新显示
            for sensor_name, value in SIMULATION_DATA.items():
                if sensor_name in self.sensor_value_labels:
                    self.sensor_value_labels[sensor_name].config(text=value)
                    self.sensor_values[sensor_name] = value
            
            # 启动模拟数据线程
            if not self.simulation_thread or not self.simulation_thread.is_alive():
                self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
                self.simulation_thread.start()
                
            # 启动模拟视频
            if self.video_enabled and self.video_label:
                self.start_video_simulation()
        else:
            logger.info("已关闭模拟数据模式")
            self.sim_button_text.set("启用模拟数据")
            
            # 停止模拟视频
            if hasattr(self, 'video_simulation_active'):
                self.video_simulation_active = False
            
            if self.connected:
                self.update_mqtt_status("已连接", True)
            else:
                self.update_mqtt_status("未连接", False)
                # 尝试重新连接MQTT
                self.reconnect()
                
    def start_video_simulation(self):
        """开始视频模拟"""
        if not PIL_AVAILABLE:
            return
            
        self.video_simulation_active = True
        self.frame_count = 0
        
        # 启动视频模拟线程
        threading.Thread(target=self.video_simulation_loop, daemon=True).start()
    
    def video_simulation_loop(self):
        """视频模拟循环"""
        if not PIL_AVAILABLE:
            return
            
        logger.info("模拟视频线程已启动")
        
        while self.video_simulation_active and self.use_simulation:
            try:
                # 生成模拟视频帧
                img = self.generate_test_frame(self.frame_count, 320, 240)
                
                if img:
                    # 转换为Tkinter格式
                    tk_img = ImageTk.PhotoImage(img)
                    
                    # 更新视频标签（在主线程中）
                    self.root.after(0, lambda: self.update_video_frame(tk_img))
                
                # 递增帧计数器
                self.frame_count += 1
                
                # 等待一段时间
                time.sleep(0.2)  # 5 FPS
                
            except Exception as e:
                logger.error(f"生成模拟视频帧时出错: {e}")
                time.sleep(1)  # 错误后等待1秒
    
    def update_video_frame(self, img):
        """更新视频帧（在主线程中调用）"""
        if self.video_label and self.video_simulation_active:
            self.video_label.config(image=img, text="")
            self.video_label.image = img  # 保持引用
    
    def generate_test_frame(self, frame_number, width=320, height=240):
        """生成测试视频帧"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            # 创建深蓝色背景图像
            img = Image.new('RGB', (width, height), color=(0, 0, 40))
            
            # 如果PIL支持ImageDraw功能
            if hasattr(Image, 'Draw'):
                from PIL import ImageDraw, ImageFont
                
                draw = ImageDraw.Draw(img)
                
                # 绘制网格
                for x in range(0, width, 20):
                    draw.line([(x, 0), (x, height)], fill=(20, 20, 60), width=1)
                
                for y in range(0, height, 20):
                    draw.line([(0, y), (width, y)], fill=(20, 20, 60), width=1)
                
                # 绘制移动的圆形
                t = frame_number / 10.0
                cx = int(width / 2 + width / 4 * math.sin(t))
                cy = int(height / 2 + height / 4 * math.cos(t))
                r = 20 + 5 * math.sin(t * 2)
                
                # 圆形
                draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(255, 100, 100))
                
                # 显示学校名称和时间
                import math
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                text = f"烟铺小学 - 监控画面 {current_time}"
                
                # 尝试加载字体，如果失败则使用默认
                try:
                    # 使用默认字体
                    font_size = 14
                    draw.text((10, 10), text, fill=(200, 200, 200))
                except Exception:
                    pass
                    
                # 显示帧号
                draw.text((10, height-20), f"Frame: {frame_number}", fill=(150, 150, 150))
                
                # 绘制移动的校徽模拟图形 (简单几何图形)
                logo_x = int(width * 0.8)
                logo_y = int(height * 0.8)
                logo_size = 30
                
                # 外圆
                draw.ellipse(
                    [(logo_x-logo_size, logo_y-logo_size), 
                     (logo_x+logo_size, logo_y+logo_size)], 
                    outline=(200, 200, 0), width=2
                )
                
                # 内部图案
                draw.polygon(
                    [(logo_x, logo_y-logo_size/2), 
                     (logo_x-logo_size/2, logo_y+logo_size/2),
                     (logo_x+logo_size/2, logo_y+logo_size/2)],
                    fill=(100, 200, 100)
                )
            
            return img
            
        except Exception as e:
            logger.error(f"生成测试帧时出错: {e}")
            return None
    
    def simulation_loop(self):
        """模拟数据生成循环"""
        logger.info("模拟数据线程已启动")
        
        while self.use_simulation:
            # 更新模拟数据
            for sensor_name in SIMULATION_DATA.keys():
                try:
                    # 转换为浮点数
                    current = float(SIMULATION_DATA[sensor_name])
                    
                    # 添加一些随机变化
                    if sensor_name == "环境温度":
                        change = random.uniform(-0.5, 0.5)
                        new_value = max(15, min(35, current + change))
                    elif sensor_name == "环境湿度":
                        change = random.uniform(-2, 2)
                        new_value = max(30, min(90, current + change))
                    elif sensor_name == "aqi":
                        change = random.uniform(-3, 3)
                        new_value = max(20, min(150, current + change))
                    elif sensor_name == "tvoc":
                        change = random.uniform(-20, 20)
                        new_value = max(100, min(600, current + change))
                    elif sensor_name == "eco2":
                        change = random.uniform(-20, 20)
                        new_value = max(400, min(1200, current + change))
                    elif sensor_name == "紫外线指数":
                        change = random.uniform(-0.2, 0.2)
                        new_value = max(0, min(10, current + change))
                    elif sensor_name == "噪音":
                        change = random.uniform(-2, 2)
                        new_value = max(30, min(70, current + change))
                    else:
                        continue
                    
                    # 格式化为字符串，保留一位小数
                    if sensor_name == "aqi" or sensor_name == "tvoc" or sensor_name == "eco2":
                        display_value = f"{int(new_value)}"
                    else:
                        display_value = f"{new_value:.1f}"
                    
                    # 更新模拟数据字典
                    SIMULATION_DATA[sensor_name] = display_value
                    
                    # 特殊处理UV风险等级
                    if sensor_name == "紫外线指数":
                        uv_value = float(display_value)
                        if uv_value < 3:
                            SIMULATION_DATA["uv风险等级"] = "低"
                        elif uv_value < 6:
                            SIMULATION_DATA["uv风险等级"] = "中"
                        elif uv_value < 8:
                            SIMULATION_DATA["uv风险等级"] = "高"
                        else:
                            SIMULATION_DATA["uv风险等级"] = "极高"
                except ValueError:
                    # 如果不是数值，保持不变
                    pass
            
            # 在主线程中更新UI
            self.root.after(0, self.update_simulation_ui)
            
            # 等待一段时间
            time.sleep(5)
    
    def update_simulation_ui(self):
        """更新模拟数据的UI显示"""
        if self.use_simulation:
            for sensor_name, value in SIMULATION_DATA.items():
                if sensor_name in self.sensor_value_labels:
                    self.sensor_value_labels[sensor_name].config(text=value)
    
    def update_clock(self):
        """更新时钟显示"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_var.set(current_time)
        self.root.after(1000, self.update_clock)
    
    def on_closing(self):
        """窗口关闭处理"""
        logger.info("应用程序正在关闭...")
        
        # 关闭MQTT连接
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        # 停止模拟模式
        self.use_simulation = False
        
        # 关闭窗口
        self.root.destroy()

    def toggle_video_simulation(self):
        """切换是否使用视频模拟"""
        if not self.video_enabled or not self.video_label:
            return
            
        # 切换视频模拟状态
        if hasattr(self, 'video_simulation_active') and self.video_simulation_active:
            # 停止视频模拟
            self.video_simulation_active = False
            self.video_sim_button_text.set("启用视频模拟")
            # 清除视频显示
            self.video_label.config(image="", text="视频模拟已停止", fg="white", font=("Arial", 14))
        else:
            # 启动视频模拟
            self.start_video_simulation()
            self.video_sim_button_text.set("停止视频模拟")

if __name__ == "__main__":
    try:
        # 创建根窗口
        root = tk.Tk()
        
        # 创建仪表盘
        app = SimpleDashboard(root)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        logger.error(f"启动仪表盘时出错: {e}")
        traceback.print_exc()
