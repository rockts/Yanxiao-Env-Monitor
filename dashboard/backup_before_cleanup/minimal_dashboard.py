#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 最小修复版
这个文件包含了一个简化版的仪表盘实现，修复了原始代码中的问题
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
import random
import threading
import time
import json

# 设置路径和导入
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "src"))

# 设置日志
log_dir = os.path.join(script_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"minimal_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# 常量定义
WINDOW_TITLE = "烟铺小学智慧校园环境监测系统 - 修复版"
WINDOW_SIZE = "1024x768"
BG_COLOR = "#1e1e2e"  # 暗色背景
TEXT_COLOR = "#ffffff"  # 白色文本
ACCENT_COLOR = "#89dceb"  # 亮蓝色强调色
PANEL_BG = "#313244"  # 面板背景色

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
SENSOR_CONFIGS = {
    "temp": {"name": "环境温度", "unit": "°C", "icon": "🌡️"},
    "humi": {"name": "环境湿度", "unit": "%RH", "icon": "💧"},
    "aqi": {"name": "空气质量指数", "unit": "", "icon": "🌬️"},
    "tvoc": {"name": "TVOC", "unit": "ppb", "icon": "🧪"},
    "eco2": {"name": "eCO2", "unit": "ppm", "icon": "🌿"},
    "uv": {"name": "紫外线指数", "unit": "", "icon": "☀️"},
    "noise": {"name": "噪音", "unit": "dB", "icon": "🔊"}
}

class MinimalDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)
        
        # 状态变量
        self.use_simulation = True
        self.sim_button_text = tk.StringVar(value="关闭模拟数据")
        self.status_text = tk.StringVar(value="状态: 使用模拟数据")
        self.current_time = tk.StringVar()
        
        # 数据变量
        self.sensor_values = {}
        for sensor_id, config in SENSOR_CONFIGS.items():
            self.sensor_values[sensor_id] = tk.StringVar(value="--")
        
        # 布局设置
        self.setup_ui()
        
        # 启动模拟数据更新
        self.update_time()
        self.update_simulation_data()
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部信息栏
        self.create_header(main_frame)
        
        # 传感器数据面板
        self.create_sensor_panels(main_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """创建顶部信息栏"""
        header_frame = ttk.Frame(parent, padding="5")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(
            header_frame,
            text="烟铺小学智慧校园环境监测系统",
            font=("微软雅黑", 20, "bold"),
            foreground=ACCENT_COLOR,
            background=BG_COLOR
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # 时间显示
        time_label = ttk.Label(
            header_frame,
            textvariable=self.current_time,
            font=("微软雅黑", 12),
            foreground=TEXT_COLOR,
            background=BG_COLOR
        )
        time_label.pack(side=tk.RIGHT, padx=10)
    
    def create_sensor_panels(self, parent):
        """创建传感器数据面板"""
        sensors_frame = ttk.Frame(parent)
        sensors_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建网格布局
        num_sensors = len(SENSOR_CONFIGS)
        cols = 3
        rows = (num_sensors + cols - 1) // cols  # 向上取整
        
        row_index = 0
        col_index = 0
        
        for sensor_id, config in SENSOR_CONFIGS.items():
            panel_frame = ttk.Frame(sensors_frame, padding="10", style="Panel.TFrame")
            panel_frame.grid(row=row_index, column=col_index, padx=10, pady=10, sticky="nsew")
            
            # 标题和图标
            header_frame = ttk.Frame(panel_frame)
            header_frame.pack(fill=tk.X)
            
            icon_label = ttk.Label(
                header_frame,
                text=config["icon"],
                font=("微软雅黑", 16)
            )
            icon_label.pack(side=tk.LEFT)
            
            title_label = ttk.Label(
                header_frame,
                text=config["name"],
                font=("微软雅黑", 14, "bold")
            )
            title_label.pack(side=tk.LEFT, padx=5)
            
            # 值显示
            value_frame = ttk.Frame(panel_frame, padding="10")
            value_frame.pack(fill=tk.BOTH, expand=True)
            
            value_label = ttk.Label(
                value_frame,
                textvariable=self.sensor_values[sensor_id],
                font=("微软雅黑", 24, "bold"),
                foreground=ACCENT_COLOR
            )
            value_label.pack(side=tk.LEFT, padx=5)
            
            unit_label = ttk.Label(
                value_frame,
                text=config["unit"],
                font=("微软雅黑", 12)
            )
            unit_label.pack(side=tk.LEFT, anchor="s")
            
            # 更新网格位置
            col_index += 1
            if col_index >= cols:
                col_index = 0
                row_index += 1
        
        # 设置列的权重使它们平均分布
        for i in range(cols):
            sensors_frame.columnconfigure(i, weight=1)
        
        # 设置行的权重
        for i in range(rows):
            sensors_frame.rowconfigure(i, weight=1)
    
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_frame = ttk.Frame(parent, padding="5")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 连接状态
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("微软雅黑", 10)
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        # 模拟数据控制按钮
        sim_button = ttk.Button(
            status_frame,
            textvariable=self.sim_button_text,
            command=self.toggle_simulation
        )
        sim_button.pack(side=tk.RIGHT, padx=10)
    
    def update_time(self):
        """更新显示的当前时间"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time.set(current_time)
        self.root.after(1000, self.update_time)
    
    def toggle_simulation(self):
        """切换模拟数据模式"""
        self.use_simulation = not self.use_simulation
        
        if self.use_simulation:
            self.sim_button_text.set("关闭模拟数据")
            self.status_text.set("状态: 使用模拟数据")
            logging.info("已启用模拟数据模式")
        else:
            self.sim_button_text.set("启用模拟数据")
            self.status_text.set("状态: 已停止模拟数据")
            logging.info("已停止模拟数据模式")
    
    def update_simulation_data(self):
        """更新模拟数据"""
        if self.use_simulation:
            for sensor_id, config in SENSOR_CONFIGS.items():
                sensor_name = config["name"]
                if sensor_name in SIMULATION_DATA:
                    # 获取基础值
                    try:
                        base_value = float(SIMULATION_DATA[sensor_name])
                        # 添加少量随机波动 (-3% 到 +3%)
                        variation = base_value * (random.random() * 0.06 - 0.03)
                        new_value = base_value + variation
                        
                        # 格式化不同类型的传感器值
                        if "温度" in sensor_name:
                            formatted_value = f"{new_value:.1f}"
                        elif "湿度" in sensor_name:
                            formatted_value = f"{new_value:.1f}"
                        elif "aqi" in sensor_name.lower():
                            formatted_value = f"{int(new_value)}"
                        else:
                            formatted_value = f"{new_value:.1f}"
                        
                        # 更新UI
                        self.sensor_values[sensor_id].set(formatted_value)
                        
                    except ValueError:
                        # 对于非数值的，直接使用原值
                        self.sensor_values[sensor_id].set(SIMULATION_DATA[sensor_name])
        
        # 每5秒更新一次
        self.root.after(5000, self.update_simulation_data)
    
    def on_closing(self):
        """窗口关闭处理"""
        logging.info("应用程序正在关闭")
        self.root.destroy()

def main():
    try:
        # 创建根窗口
        root = tk.Tk()
        
        # 配置样式
        style = ttk.Style()
        style.theme_use('alt')  # 使用alt主题，它通常比默认主题更适合自定义
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure("TButton", padding=6)
        style.configure("Panel.TFrame", background=PANEL_BG)
        
        # 创建应用实例
        app = MinimalDashboard(root)
        
        # 启动主循环
        print("启动应用程序主循环...")
        root.mainloop()
        
    except Exception as e:
        logging.error(f"应用程序启动时出错: {str(e)}")
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
