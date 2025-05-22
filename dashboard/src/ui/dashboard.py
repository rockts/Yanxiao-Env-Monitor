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

# 设置日志
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
log_dir = os.path.join(base_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"simple_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# UI 常量
PAGE_BG_COLOR = "#0A1E36"  # 深科技蓝色背景
PANEL_BG_COLOR = "#102A43" # 稍亮一点的蓝色面板背景
TEXT_COLOR_HEADER = "#E0EFFF"  # 标题文本颜色
TEXT_COLOR_VALUE = "#64FFDA"   # 值文本颜色

# MQTT配置
# 尝试从配置文件读取设置，如果失败则使用默认值
try:
    import json
    # 先尝试读取local_config.json（用于本地测试）
    config_file_local = os.path.join(base_dir, "config", "local_config.json")
    if os.path.exists(config_file_local):
        print(f"尝试加载本地配置: {config_file_local}")
        with open(config_file_local, 'r') as f:
            config = json.load(f)
            MQTT_BROKER_HOST = config.get("mqtt_broker_host", "localhost")
            MQTT_BROKER_PORT = config.get("mqtt_broker_port", 1883)
            MQTT_USERNAME = config.get("siot_username", "siot") 
            MQTT_PASSWORD = config.get("siot_password", "dfrobot")
            print(f"从本地配置文件加载MQTT设置: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    else:
        # 然后尝试标准配置文件
        config_file = os.path.join(base_dir, "config", "config.json")
        if os.path.exists(config_file):
            print(f"尝试加载标准配置: {config_file}")
            with open(config_file, 'r') as f:
                config = json.load(f)
                MQTT_BROKER_HOST = config.get("mqtt_broker_host", "192.168.1.129")
                MQTT_BROKER_PORT = config.get("mqtt_broker_port", 1883)
                MQTT_USERNAME = config.get("siot_username", "siot") 
                MQTT_PASSWORD = config.get("siot_password", "dfrobot")
                print(f"从标准配置文件加载MQTT设置: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        else:
            # 无配置文件，使用默认设置
            raise FileNotFoundError("找不到配置文件")
except Exception as e:
    # 默认MQTT配置
    print(f"加载配置出错: {e}")
    MQTT_BROKER_HOST = "localhost"  # 默认使用本地主机以便配合start_with_local_mqtt.command脚本
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = "siot"
    MQTT_PASSWORD = "dfrobot"
    print(f"使用默认MQTT设置: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

# 设置唯一客户端ID
import uuid
MQTT_CLIENT_ID = f"simple_dashboard_client_{uuid.uuid4().hex[:8]}"

# 订阅的MQTT主题
MQTT_TOPICS = [
    "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
    "siot/紫外线指数", "siot/uv风险等级", "siot/噪音"
]

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
    def __init__(self, root):
        self.root = root
        self.root.title("智慧校园环境监测系统 - 简化版")
        self.root.geometry("800x600")
        self.root.configure(bg=PAGE_BG_COLOR)
        
        # 初始化变量
        self.mqtt_client = None
        self.use_simulation = True  # 默认使用模拟数据
        self.sensor_data = {key: "N/A" for key in simulation_data.keys()}
        
        # 创建简单布局
        self.create_ui()
        
        # 尝试MQTT连接
        self.mqtt_connect()
        
        # 启动更新循环
        if self.use_simulation:
            self.update_aqi_display()
            
        # 协议处理监听器
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # 创建标题栏
        header_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        header_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(header_frame, text="智慧校园环境监测系统", 
                             font=("Helvetica", 24, "bold"), 
                             fg=TEXT_COLOR_HEADER, bg=PAGE_BG_COLOR)
        title_label.pack()
        
        # 添加连接状态
        self.connection_label = tk.Label(header_frame, text="状态: 初始化中...", 
                                     font=("Helvetica", 10), 
                                     fg="orange", bg=PAGE_BG_COLOR)
        self.connection_label.pack(pady=5)
        
        # 创建AQI面板
        self.aqi_frame = tk.Frame(self.root, bg=PANEL_BG_COLOR, 
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
            print("MQTT库不可用，使用模拟数据")
            self.use_simulation = True
            self.update_aqi_display()  # 立即启动模拟数据显示
            self.connection_label.config(text="状态: MQTT库不可用，使用模拟数据", fg="orange")
            return
            
        try:
            # 先清理之前的连接
            if self.mqtt_client:
                try:
                    self.mqtt_client.disconnect()
                    self.mqtt_client.loop_stop()
                    print("已断开之前的MQTT连接")
                except:
                    pass
            
            print(f"尝试连接MQTT服务器 {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
            # 使用API版本2，并设置唯一的客户端ID
            client_id = f"{MQTT_CLIENT_ID}_{random.randint(1000, 9999)}"
            print(f"使用客户端ID: {client_id}")
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=True)
            self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
            # 设置连接超时
            self.mqtt_client.connect_timeout = 5  # 减少连接超时时间，快速失败
            
            # 注册回调
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            # 更新UI状态
            self.connection_label.config(text="MQTT: 连接中...", fg="orange")
            
            # 尝试连接
            try:
                print(f"开始连接到MQTT服务器...")
                self.mqtt_client.connect_async(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 10)
                self.mqtt_client.loop_start()
                print("MQTT客户端已启动，等待连接回调")
            except Exception as conn_err:
                print(f"MQTT连接过程中出错: {conn_err}")
                raise conn_err
            
            # 添加超时检查 - 5秒后检查连接是否成功
            self.root.after(5000, self.check_mqtt_connection)
            
        except Exception as e:
            print(f"MQTT连接初始化失败: {e}")
            self.connection_label.config(text=f"MQTT连接失败: {str(e)[:30]}", fg="red")
            self.use_simulation = True
            # 先确保能显示一些数据
            simulation_data["aqi"] = 50
            self.update_aqi_display()  # 立即启动模拟数据显示
            
            # 一分钟后尝试重连
            print("计划60秒后重试连接...")
            self.root.after(60000, self.retry_mqtt_connection)
    
    def check_mqtt_connection(self):
        """检查MQTT连接是否成功建立"""
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            print("MQTT连接失败或超时，切换到模拟模式")
            self.connection_label.config(text="MQTT: 连接失败，使用模拟数据", fg="orange")
            
            # 停止之前的MQTT连接尝试
            if self.mqtt_client:
                try:
                    self.mqtt_client.disconnect()
                    self.mqtt_client.loop_stop()
                except:
                    pass
                
            self.use_simulation = True
            print("启动模拟数据显示...")
            # 确保立即显示一个初始值
            self.sensor_data["aqi"] = simulation_data["aqi"]
            self.update_aqi_display()  # 立即启动模拟数据更新
            
            # 添加定期重试MQTT连接的机制
            self.root.after(30000, self.retry_mqtt_connection)  # 30秒后重试连接
    
    def retry_mqtt_connection(self):
        """尝试重新连接MQTT服务器"""
        if self.use_simulation:  # 如果当前处于模拟模式，尝试重新连接
            print("尝试重新连接MQTT服务器...")
            self.connection_label.config(text="MQTT: 尝试重新连接...", fg="orange")
            self.mqtt_connect()
        # 无论结果如何，确保数据显示持续更新
        if self.use_simulation:
            self.root.after(3000, self.update_aqi_display)
    
    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT连接成功回调"""
        if rc == 0:
            print("MQTT连接成功！")
            self.connection_label.config(text="MQTT: 已连接", fg="green")
            
            # 订阅主题
            for topic in MQTT_TOPICS:
                self.mqtt_client.subscribe(topic)
                print(f"已订阅: {topic}")
                
            self.use_simulation = False
        else:
            error_msg = f"MQTT连接失败，代码: {rc}"
            print(error_msg)
            self.connection_label.config(text=error_msg, fg="red")
            self.use_simulation = True
            self.update_aqi_display()  # 立即启动模拟数据更新
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        print(f"MQTT连接已断开: {rc}")
        self.connection_label.config(text="MQTT: 已断开", fg="red")
        self.use_simulation = True
        self.update_aqi_display()  # 启动模拟数据更新
    
    def on_mqtt_message(self, client, userdata, msg):
        """处理收到的MQTT消息"""
        topic = msg.topic
        try:
            payload = msg.payload.decode("utf-8")
            print(f"收到消息: {topic} = {payload}")
            
            # 根据主题类型处理数据
            if topic == "siot/aqi":
                # 确保AQI数据被正确解析
                try:
                    # 尝试多种格式解析
                    aqi_value = None
                    
                    # 1. 尝试直接转换为数值
                    try:
                        aqi_value = float(payload)
                        print(f"成功将AQI值直接解析为数值: {aqi_value}")
                    except ValueError:
                        print(f"AQI值无法直接转换为数值: {payload}")
                        pass
                        
                    # 2. 尝试JSON解析
                    if aqi_value is None:
                        try:
                            data = json.loads(payload)
                            for key in ["value", "data", "aqi", "result", "val", "reading"]:
                                if key in data:
                                    try:
                                        aqi_value = float(data[key])
                                        print(f"成功从JSON中提取AQI值 (键={key}): {aqi_value}")
                                        break
                                    except (ValueError, TypeError):
                                        continue
                        except (json.JSONDecodeError, ValueError):
                            print(f"AQI值无法作为JSON解析: {payload}")
                    
                    # 3. 尝试提取数值部分
                    if aqi_value is None:
                        numeric_part = ''.join(c for c in payload if c.isdigit() or c == '.')
                        if numeric_part:
                            try:
                                aqi_value = float(numeric_part)
                                print(f"成功提取AQI数值部分: {aqi_value}")
                            except ValueError:
                                pass
                    
                    # 4. 如果所有方法都失败，使用模拟值
                    if aqi_value is None:
                        aqi_value = simulation_data["aqi"]
                        print(f"无法解析AQI值，使用模拟值: {aqi_value}")
                    
                    # 确保AQI为合理值
                    if isinstance(aqi_value, (int, float)):
                        # 限制AQI在合理范围内
                        aqi_value = max(0, min(500, aqi_value))
                        print(f"最终AQI值 (可能经过校正): {aqi_value}")
                        self.sensor_data["aqi"] = aqi_value
                        # 在主线程中更新UI
                        self.root.after(0, lambda: self.update_aqi_display(aqi_value))
                    else:
                        print(f"解析后的AQI值不是数值类型: {type(aqi_value)}")
                        
                except Exception as e:
                    print(f"处理AQI数据时出错: {e}")
                    # 即使出错也使用模拟数据，确保显示
                    self.root.after(0, self.update_aqi_display)
            
            # 处理其他主题数据
            elif topic.startswith("siot/"):
                sensor_type = topic.split("/")[1]
                if sensor_type in self.sensor_data:
                    self.sensor_data[sensor_type] = payload
                    print(f"更新传感器数据: {sensor_type} = {payload}")
        
        except Exception as e:
            print(f"处理MQTT消息时出错: {e}")
    
    def update_aqi_display(self, aqi_value=None):
        """更新AQI显示"""
        if aqi_value is None:  # 如果没有提供AQI值
            if self.use_simulation:
                # 模拟AQI数据变化
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
            
    def on_closing(self):
        """窗口关闭时的清理工作"""
        print("正在关闭应用...")
        if self.mqtt_client:
            try:
                self.mqtt_client.disconnect()
                self.mqtt_client.loop_stop()
                print("MQTT客户端已正常关闭")
            except Exception as e:
                print(f"关闭MQTT客户端时出错: {e}")
        self.root.destroy()

def main():
    try:
        # 设置中文区域设置
        try:
            locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
            print("成功设置中文区域设置")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Chinese_China.936')  # Windows系统
                print("成功设置Windows中文区域设置")
            except locale.Error:
                print("无法设置中文区域设置，使用默认设置")
        
        # 创建根窗口
        root = tk.Tk()
        root.title("智慧校园环境监测系统 - 简化版")
        root.geometry("800x600")
        
        # 捕获CTRL+C信号
        try:
            import signal
            def signal_handler(sig, frame):
                print("收到终止信号，正在关闭程序...")
                root.destroy()
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except (ImportError, AttributeError):
            pass  # 有些平台不支持信号
        
        # 创建应用
        app = SimpleDashboard(root)
        
        # 启动主循环
        print("启动Tkinter主循环...")
        root.mainloop()
        print("主循环结束")
        
        return 0
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("程序开始运行...")
    main()
    print("程序已退出")
