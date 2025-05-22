#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 简化版
仅包含基本窗口和AQI显示功能，增强错误处理和MQTT模拟
"""

import tkinter as tk
import random
import logging
import os
import sys
import json
import time
import threading
from datetime import datetime
import locale

# Ensure project structure is handled for imports
from pathlib import Path
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent # dashboard/src/ui/simple_dashboard.py -> dashboard/

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

# Core components that might be used by SimpleDashboard
# Assuming SimpleDashboard might use ConfigManager for its MQTT settings or other configs.
from core.config_manager import ConfigManager
from core.log_manager import logger # Use the pre-configured logger from log_manager

# 尝试导入MQTT
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
    print("MQTT库已成功导入")
except ImportError:
    MQTT_AVAILABLE = False
    print("警告: MQTT库未安装，使用模拟数据")
    
# 尝试导入PIL
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("PIL库已成功导入")
except ImportError:
    PIL_AVAILABLE = False
    print("警告: PIL库未安装，图像功能不可用")

# UI 常量
PAGE_BG_COLOR = "#0A1E36"  # 深科技蓝色背景
PANEL_BG_COLOR = "#102A43" # 稍亮一点的蓝色面板背景
TEXT_COLOR_HEADER = "#E0EFFF"  # 标题文本颜色
TEXT_COLOR_VALUE = "#64FFDA"   # 值文本颜色

# MQTT配置 - Now primarily driven by ConfigManager
# The old way of reading config files here can be removed or made secondary.

# 模拟数据 - 用于MQTT不可用或连接失败时
simulation_data = {
    "环境温度": 25.6,
    "环境湿度": 68.2,
    "aqi": 52,
    "tvoc": 320,
    "eco2": 780,
    "紫外线指数": 2.8,
    "uv风险等级": "低",
    "噪音": 45.5
}

class SimpleDashboard:
    def __init__(self, app_config: dict, master: tk.Tk | None = None): # Accept app_config dict and optional master
        self.app_config = app_config # Store the passed config
        self.logger = logger # Use the global logger

        if master:
            self.root = master
        else:
            self.root = tk.Tk()
            self.is_main_window = True # Flag if this instance created the root window

        self.root.title(self.app_config.get("simple_dashboard_title", "智慧校园环境监测系统 - 简化版"))
        geometry = self.app_config.get("simple_dashboard_geometry", "800x600")
        self.root.geometry(geometry)
        self.root.configure(bg=self.app_config.get("page_bg_color", PAGE_BG_COLOR))
        
        # Get MQTT settings from the passed app_config
        self.mqtt_broker_host = self.app_config.get("mqtt_broker_host", "localhost")
        self.mqtt_broker_port = self.app_config.get("mqtt_broker_port", 1883)
        self.mqtt_username = self.app_config.get("mqtt_username", "siot") # Or siot_username from config
        self.mqtt_password = self.app_config.get("mqtt_password", "dfrobot") # Or siot_password
        self.mqtt_client_id = self.app_config.get("mqtt_client_id", f"simple_dashboard_client_{random.randint(1000,9999)}")
        self.mqtt_topics = self.app_config.get("mqtt_topics", []) # Get topics from main config

        # 初始化变量
        self.mqtt_client = None
        self.use_simulation = True  # Default, can be changed by MQTT connection status
        self.sensor_data = {topic.split('/')[-1]: "N/A" for topic in self.mqtt_topics} # More robust key creation
        # Initialize with default simulation data if specific keys are expected
        for key in simulation_data.keys():
            if key not in self.sensor_data:
                 self.sensor_data[key] = "N/A"

        # 创建简单布局
        self.create_ui()
        
        # 尝试MQTT连接
        if MQTT_AVAILABLE:
            self.mqtt_connect()
        else:
            self.logger.warning("MQTT库不可用，将仅使用模拟数据.")
            self.update_connection_status("模拟模式 (MQTT库缺失)", "orange")
            self.use_simulation = True
            self.update_aqi_display() # Start with simulated data
        
        # 协议处理监听器
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logger.info("简化版仪表盘已初始化.")

    def create_ui(self):
        # 创建标题栏
        header_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        header_frame.pack(fill="x", pady=20)
        
        title_text = self.app_config.get("simple_dashboard_header", "智慧校园环境监测系统")
        title_label = tk.Label(header_frame, text=title_text, 
                             font=("Helvetica", 24, "bold"), 
                             fg=self.app_config.get("text_color_header", TEXT_COLOR_HEADER), 
                             bg=self.app_config.get("page_bg_color", PAGE_BG_COLOR))
        title_label.pack()
        
        # 添加连接状态
        self.connection_label = tk.Label(header_frame, text="状态: 初始化中...", 
                                     font=("Helvetica", 10), 
                                     fg="orange", bg=PAGE_BG_COLOR)
        self.connection_label.pack(pady=5)
        
        # 创建AQI面板
        self.aqi_frame = tk.Frame(self.root, bg=self.app_config.get("panel_bg_color", PANEL_BG_COLOR), 
                                 padx=20, pady=20,
                                 highlightbackground="#555555", 
                                 highlightthickness=1)
        self.aqi_frame.pack(pady=30)
        
        # AQI标题
        tk.Label(self.aqi_frame, text="空气质量指数 (AQI)", 
               font=("Helvetica", 18, "bold"), 
               fg=TEXT_COLOR_HEADER, bg=PANEL_BG_COLOR).pack(pady=(0,20))
        
        # AQI数值显示
        self.aqi_value_label = tk.Label(self.aqi_frame, text="--", 
                                      font=("Helvetica", 40, "bold"), 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.aqi_value_label.pack()
        
        # AQI等级显示
        self.aqi_level_label = tk.Label(self.aqi_frame, text="--", 
                                      font=("Helvetica", 16), 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.aqi_level_label.pack(pady=(10, 0))
        
        # AQI描述显示
        self.aqi_desc_label = tk.Label(self.aqi_frame, text="--", 
                                     font=("Helvetica", 12), 
                                     fg=TEXT_COLOR_HEADER, bg=PANEL_BG_COLOR,
                                     wraplength=300)
        self.aqi_desc_label.pack(pady=(5, 0))
        
        # 按钮框架
        buttons_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        buttons_frame.pack(pady=20)
        
        # 添加刷新按钮
        self.refresh_button = tk.Button(buttons_frame, text="刷新数据", 
                                      command=self.update_aqi_display,
                                      font=("Helvetica", 12),
                                      bg="#007BFF", fg="white",
                                      padx=10, pady=5)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 添加切换模拟数据按钮
        self.toggle_sim_button = tk.Button(buttons_frame, text="切换模拟数据", 
                                        command=self.toggle_simulation,
                                        font=("Helvetica", 12),
                                        bg="#28a745", fg="white", 
                                        padx=10, pady=5)
        self.toggle_sim_button.pack(side=tk.LEFT, padx=5)
        
    def toggle_simulation(self):
        """切换是否使用模拟数据"""
        self.use_simulation = not self.use_simulation
        if self.use_simulation:
            print("已切换到模拟数据模式")
            self.connection_label.config(text="状态: 使用模拟数据", fg="orange")
            self.update_aqi_display()  # 立即启动模拟数据更新
        else:
            print("尝试恢复MQTT连接")
            self.connection_label.config(text="状态: 尝试连接MQTT...", fg="orange")
            # 尝试重新连接MQTT
            if self.mqtt_client:
                try:
                    self.mqtt_client.disconnect()
                    self.mqtt_client.loop_stop()
                except:
                    pass
            self.mqtt_connect()
    
    def mqtt_connect(self):
        """尝试连接MQTT服务器"""
        if not MQTT_AVAILABLE:
            self.logger.warning("尝试MQTT连接，但库不可用.")
            return

        try:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.mqtt_client_id)
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            if self.mqtt_username and self.mqtt_password:
                self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
            
            self.logger.info(f"尝试连接到MQTT代理: {self.mqtt_broker_host}:{self.mqtt_broker_port}")
            self.update_connection_status(f"连接中: {self.mqtt_broker_host}...", "orange")
            self.mqtt_client.connect(self.mqtt_broker_host, self.mqtt_broker_port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            self.logger.error(f"MQTT连接失败: {e}", exc_info=True)
            self.update_connection_status(f"连接失败: {e}", "red")
            self.use_simulation = True
            self.update_aqi_display() # Fallback to simulation

    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None): # Added properties for v2 callback
        if rc == 0:
            self.logger.info("成功连接到MQTT代理")
            self.update_connection_status("已连接到MQTT", "green")
            self.use_simulation = False # Switch from simulation on successful connect
            # Subscribe to relevant topics from app_config
            for topic in self.mqtt_topics:
                client.subscribe(topic)
                self.logger.info(f"已订阅主题: {topic}")
        else:
            self.logger.error(f"MQTT连接失败，返回码: {rc}")
            self.update_connection_status(f"MQTT连接失败 (码: {rc})", "red")
            self.use_simulation = True
            self.update_aqi_display() # Fallback to simulation

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            topic_key = msg.topic.split('/')[-1] # Use last part of topic as key
            self.logger.debug(f"收到MQTT消息 - 主题: {msg.topic}, 内容: {payload}")
            
            # Try to parse JSON, if not, use as string
            try:
                data = json.loads(payload)
                # If data is a dict and has a known value field (e.g., 'value')
                if isinstance(data, dict) and 'value' in data:
                    self.sensor_data[topic_key] = data['value']
                # Handle specific known JSON structures if necessary
                # elif ... 
                else:
                    self.sensor_data[topic_key] = payload # Fallback to raw payload if JSON structure is not as expected
            except json.JSONDecodeError:
                self.sensor_data[topic_key] = payload # Store as plain text if not JSON

            # Update UI based on the new data
            # For simple_dashboard, we primarily care about AQI for detailed display
            if topic_key == "aqi" or "aqi" in msg.topic.lower():
                self.update_aqi_display() 
            # Potentially update other parts of the UI if they exist in simple_dashboard

        except Exception as e:
            self.logger.error(f"处理MQTT消息时出错: {e} (主题: {msg.topic})", exc_info=True)

    def on_mqtt_disconnect(self, client, userdata, rc, properties=None): # Added properties for v2 callback
        self.logger.warning(f"与MQTT代理断开连接，返回码: {rc}")
        self.update_connection_status("MQTT已断开", "red")
        self.use_simulation = True
        # Optionally, try to reconnect or just switch to simulation
        # For simplicity here, just switch to simulation and update display
        self.update_aqi_display()

    def update_connection_status(self, text, color):
        if hasattr(self, 'connection_label'): # Check if UI element exists
            self.connection_label.config(text=f"状态: {text}", fg=color)
        self.logger.info(f"连接状态更新: {text}")

    def update_aqi_display(self):
        """更新AQI显示"""
        if self.use_simulation:  # 如果使用模拟数据
            try:
                current_aqi = simulation_data["aqi"]
                if isinstance(current_aqi, str):
                    current_aqi = float(current_aqi)
            except (ValueError, KeyError):
                current_aqi = 50  # 默认AQI值
            
            # 添加随机变化
            aqi_value = current_aqi + random.randint(-5, 5)
            aqi_value = max(0, min(500, aqi_value))  # 限制在有效范围内
            
            # 更新数据源
            simulation_data["aqi"] = aqi_value
            print(f"使用模拟AQI值: {aqi_value}")
        else:
            # 使用上次更新的传感器数据
            try:
                if isinstance(self.sensor_data["aqi"], (int, float)):
                    aqi_value = float(self.sensor_data["aqi"])
                elif isinstance(self.sensor_data["aqi"], str) and self.sensor_data["aqi"] != "N/A":
                    aqi_value = float(self.sensor_data["aqi"])
                else:
                    # 如果没有有效的传感器数据，切换到模拟模式
                    print("没有有效的传感器数据，临时使用模拟数据")
                    aqi_value = simulation_data["aqi"]
                    if isinstance(aqi_value, str):
                        aqi_value = float(aqi_value)
                print(f"使用{'存储的' if not self.use_simulation else '模拟'}AQI值: {aqi_value}")
            except (ValueError, KeyError):
                print("无法获取有效AQI值，使用模拟数据")
                aqi_value = 50
                simulation_data["aqi"] = aqi_value
        
        # 无论何种情况，确保aqi_value是有效的浮点数
        try:
            if aqi_value is None or not isinstance(aqi_value, (int, float)):
                print(f"AQI值无效 ({aqi_value})，使用默认值50")
                aqi_value = 50
            
            # 确保在有效范围内
            aqi_value = max(0, min(500, float(aqi_value)))
            
            # 显示AQI值
            self.aqi_value_label.config(text=str(int(aqi_value)))
            
            # 根据AQI值设置等级和描述
            if aqi_value <= 50:
                level = "优"
                color = "#4CAF50"  # 绿色
                desc = "空气质量令人满意，基本无污染"
            elif aqi_value <= 100:
                level = "良"
                color = "#FFEB3B"  # 黄色
                desc = "空气质量可接受，敏感人群应减少户外活动"
            elif aqi_value <= 150:
                level = "轻度污染"
                color = "#FF9800"  # 橙色
                desc = "轻度污染，儿童等敏感人群应减少户外活动"
            elif aqi_value <= 200:
                level = "中度污染"
                color = "#F44336"  # 红色
                desc = "中度污染，应减少户外活动"
            elif aqi_value <= 300:
                level = "重度污染"
                color = "#9C27B0"  # 紫色
                desc = "重度污染，应避免户外活动"
            else:
                level = "严重污染"
                color = "#880E4F"  # 深紫色
                desc = "严重污染，应停止户外活动"
            
            # 更新UI
            self.aqi_level_label.config(text=level, fg=color)
            self.aqi_value_label.config(fg=color)
            self.aqi_desc_label.config(text=desc)
            
            # 如果是模拟模式，安排下一次更新
            if self.use_simulation:
                self.root.after(3000, self.update_aqi_display)
                
        except Exception as e:
            print(f"处理AQI值时出错: {e}, 使用默认值50")
            aqi_value = 50
            # 即使出现异常也尝试更新UI
            try:
                self.aqi_value_label.config(text=str(int(aqi_value)))
                self.aqi_level_label.config(text="良", fg="#FFEB3B")
                self.aqi_desc_label.config(text="数据处理出错，显示模拟值")
                # 安排下一次更新
                if self.use_simulation:
                    self.root.after(3000, self.update_aqi_display)
            except:
                print("无法更新UI控件")
                
        # 显示AQI值
        self.aqi_value_label.config(text=str(int(aqi_value)))
        
        # 根据AQI值设置等级和描述
        if aqi_value <= 50:
            level = "优"
            color = "#4CAF50"  # 绿色
            desc = "空气质量令人满意，基本无污染"
        elif aqi_value <= 100:
            level = "良"
            color = "#FFEB3B"  # 黄色
            desc = "空气质量可接受，敏感人群应减少户外活动"
        elif aqi_value <= 150:
            level = "轻度污染"
            color = "#FF9800"  # 橙色
            desc = "轻度污染，儿童等敏感人群应减少户外活动"
        elif aqi_value <= 200:
            level = "中度污染"
            color = "#F44336"  # 红色
            desc = "中度污染，应减少户外活动"
        elif aqi_value <= 300:
            level = "重度污染"
            color = "#9C27B0"  # 紫色
            desc = "重度污染，应避免户外活动"
        else:
            level = "严重污染"
            color = "#880E4F"  # 深紫色
            desc = "严重污染，应停止户外活动"
        
        # 更新UI
        self.aqi_level_label.config(text=level, fg=color)
        self.aqi_value_label.config(fg=color)
        self.aqi_desc_label.config(text=desc)
        
        # 如果是模拟模式，安排下一次更新
        if self.use_simulation:
            self.root.after(3000, self.update_aqi_display)
            
    def toggle_simulation_mode(self):
        if MQTT_AVAILABLE and self.mqtt_client and self.mqtt_client.is_connected():
            self.logger.info("MQTT已连接，无法手动切换到模拟模式。请先断开连接或等待连接失败。")
            # Or, force disconnect and switch:
            # self.mqtt_client.disconnect()
            # self.use_simulation = True
            # self.update_aqi_display()
            # self.update_connection_status("模拟模式 (手动切换)", "orange")
        else:
            self.use_simulation = not self.use_simulation
            status_text = "模拟模式" if self.use_simulation else "尝试连接MQTT..."
            status_color = "orange" if self.use_simulation else "blue"
            self.update_connection_status(status_text, status_color)
            self.logger.info(f"模拟模式切换为: {self.use_simulation}")
            if not self.use_simulation and MQTT_AVAILABLE:
                self.mqtt_connect() # Try to connect if switching off simulation
            else:
                self.update_aqi_display() # Update display with new mode data

    def on_closing(self):
        self.logger.info("关闭简化版仪表盘...")
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.logger.info("MQTT客户端已断开连接")
        if hasattr(self, 'is_main_window') and self.is_main_window:
            self.root.destroy()
        else: # If not main window, just hide or handle differently
            pass 

    def run(self):
        """如果此实例创建了根窗口，则启动Tkinter主循环。"""
        if hasattr(self, 'is_main_window') and self.is_main_window:
            self.logger.info("启动Tkinter主循环 (SimpleDashboard)")
            self.root.mainloop()
        else:
            self.logger.info("SimpleDashboard run() called, but not main window. UI should be managed by parent.")

# 主程序入口 (for standalone testing)
if __name__ == '__main__':
    logger.info("以独立模式运行 SimpleDashboard...")
    # For standalone, we need a ConfigManager instance to get a mock config
    # In the actual app, main_dashboard.py provides this.
    try:
        config_manager = ConfigManager() # Gets default config
        app_config = config_manager.get_all()
    except Exception as e:
        logger.error(f"独立运行时无法加载配置: {e}, 使用硬编码的默认值.")
        app_config = {
            "mqtt_broker_host": "localhost",
            "mqtt_broker_port": 1883,
            "mqtt_topics": ["siot/aqi"], 
            # Add other necessary default values for simple_dashboard
            "page_bg_color": PAGE_BG_COLOR, 
            "panel_bg_color": PANEL_BG_COLOR,
            "text_color_header": TEXT_COLOR_HEADER,
            "text_color_value": TEXT_COLOR_VALUE
        }

    # Ensure MQTT_AVAILABLE is defined for standalone execution
    if 'MQTT_AVAILABLE' not in globals():
        try:
            import paho.mqtt.client as mqtt
            MQTT_AVAILABLE = True
        except ImportError:
            MQTT_AVAILABLE = False
            logger.warning("MQTT库在独立运行时未找到.")

    root = tk.Tk()
    app = SimpleDashboard(app_config=app_config, master=root)
    app.run() # This will call root.mainloop()
