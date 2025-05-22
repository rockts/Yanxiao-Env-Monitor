#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 纯净版
这是一个完全独立的版本，不依赖于原有的代码结构，确保能正常运行
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, font
import logging
from datetime import datetime
import random
import threading
import time
from pathlib import Path
import json

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
LOG_DIR = PROJECT_ROOT / "logs"

# 创建日志目录
if not LOG_DIR.exists():
    os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
log_file = LOG_DIR / f"pure_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# UI颜色方案
DARK_MODE = True
if DARK_MODE:
    # 深色主题
    BG_COLOR = "#1e1e2e"  # 暗色背景
    PANEL_BG_COLOR = "#313244"  # 面板背景
    TEXT_COLOR = "#cdd6f4"  # 亮色文字
    ACCENT_COLOR = "#89b4fa"  # 亮蓝色强调
    SECONDARY_COLOR = "#f38ba8"  # 粉色次要强调
    STATUS_GOOD = "#a6e3a1"  # 绿色正常状态
    STATUS_WARNING = "#f9e2af"  # 黄色警告状态
    STATUS_CRITICAL = "#f38ba8"  # 红色错误状态
else:
    # 浅色主题
    BG_COLOR = "#ffffff"
    PANEL_BG_COLOR = "#f0f0f0"
    TEXT_COLOR = "#333333"
    ACCENT_COLOR = "#0078d7"
    SECONDARY_COLOR = "#e81123"
    STATUS_GOOD = "#107c10"
    STATUS_WARNING = "#ff8c00"
    STATUS_CRITICAL = "#e81123"

# 传感器配置
SENSOR_CONFIG = {
    "temp": {"name": "环境温度", "unit": "°C", "icon": "🌡️", "min": 10, "max": 40, "warn_min": 15, "warn_max": 30, "color": "#f38ba8"},
    "humi": {"name": "环境湿度", "unit": "%RH", "icon": "💧", "min": 20, "max": 95, "warn_min": 30, "warn_max": 70, "color": "#89b4fa"},
    "aqi": {"name": "空气质量指数", "unit": "", "icon": "🌬️", "min": 20, "max": 300, "warn_min": 50, "warn_max": 100, "color": "#a6e3a1"},
    "tvoc": {"name": "TVOC", "unit": "ppb", "icon": "🧪", "min": 50, "max": 500, "warn_min": 100, "warn_max": 300, "color": "#fab387"},
    "eco2": {"name": "eCO2", "unit": "ppm", "icon": "🌿", "min": 400, "max": 2000, "warn_min": 600, "warn_max": 1000, "color": "#94e2d5"},
    "uv": {"name": "紫外线指数", "unit": "", "icon": "☀️", "min": 0, "max": 10, "warn_min": 3, "warn_max": 7, "color": "#f9e2af"},
    "noise": {"name": "噪音", "unit": "dB", "icon": "🔊", "min": 30, "max": 90, "warn_min": 50, "warn_max": 70, "color": "#cba6f7"}
}

# 模拟数据
SIMULATED_DATA = {
    "temp": "25.6",
    "humi": "68.2",
    "aqi": "52",
    "tvoc": "320",
    "eco2": "780",
    "uv": "2.8",
    "noise": "45.5"
}

# 天气状态模拟
WEATHER_STATUS = {
    "city": "烟铺小学",
    "temperature": "26",
    "condition": "晴",
    "air_quality": "良好",
    "wind": "东北风 3级",
    "updated": datetime.now().strftime("%H:%M")
}

class PureDashboard:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # 状态变量
        self.simulation_enabled = True
        self.simulation_btn_text = tk.StringVar(value="关闭模拟数据")
        self.status_text = tk.StringVar(value="状态: 已启用模拟数据")
        self.current_time = tk.StringVar()
        
        # 传感器数据变量
        self.sensor_data = {}
        for sensor_id in SENSOR_CONFIG:
            self.sensor_data[sensor_id] = tk.StringVar(value="--")
        
        # 创建UI
        self.create_ui()
        
        # 启动定时任务
        self.update_time()
        self.update_simulated_data()
        
        # 设置窗口关闭处理
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """设置窗口基本属性"""
        self.root.title("烟铺小学智慧校园环境监测系统")
        self.root.geometry("1024x768")
        self.root.configure(bg=BG_COLOR)
        
        # 确保窗口大小适应内容
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10, style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # 顶部标题栏
        self.create_header(main_frame)
        
        # 中部内容区域 - 传感器面板
        content_frame = ttk.Frame(main_frame, style="Content.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        self.create_sensor_panels(content_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """创建顶部标题栏"""
        header_frame = ttk.Frame(parent, style="Header.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(
            header_frame, 
            text="烟铺小学智慧校园环境监测系统",
            font=("微软雅黑", 20, "bold"),
            foreground=ACCENT_COLOR,
            background=BG_COLOR,
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # 天气信息
        weather_frame = ttk.Frame(header_frame, style="Weather.TFrame")
        weather_frame.grid(row=0, column=1, sticky="e")
        
        weather_text = f"{WEATHER_STATUS['condition']} {WEATHER_STATUS['temperature']}°C  {WEATHER_STATUS['wind']}"
        weather_label = ttk.Label(
            weather_frame,
            text=weather_text,
            font=("微软雅黑", 12),
            foreground=TEXT_COLOR,
            background=BG_COLOR
        )
        weather_label.pack(side=tk.LEFT, padx=10)
        
        # 时间显示
        time_label = ttk.Label(
            header_frame,
            textvariable=self.current_time,
            font=("微软雅黑", 12),
            foreground=TEXT_COLOR,
            background=BG_COLOR
        )
        time_label.grid(row=0, column=2, sticky="e", padx=10)
    
    def create_sensor_panels(self, parent):
        """创建传感器面板"""
        # 创建网格布局
        sensors_frame = ttk.Frame(parent, style="Sensors.TFrame")
        sensors_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置3列布局
        cols = 3
        sensors_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        
        # 创建传感器面板
        row, col = 0, 0
        for sensor_id, config in SENSOR_CONFIG.items():
            # 创建面板框架
            panel = ttk.Frame(
                sensors_frame, 
                style="SensorPanel.TFrame", 
                padding=10,
                relief="ridge", 
                borderwidth=2
            )
            panel.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # 面板标题和图标
            header_frame = ttk.Frame(panel, style="PanelHeader.TFrame")
            header_frame.pack(fill=tk.X, pady=(0, 5))
            
            icon_label = ttk.Label(
                header_frame,
                text=config["icon"],
                font=("微软雅黑", 16),
                foreground=config["color"],
                background=PANEL_BG_COLOR
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
            
            name_label = ttk.Label(
                header_frame,
                text=config["name"],
                font=("微软雅黑", 14, "bold"),
                foreground=TEXT_COLOR,
                background=PANEL_BG_COLOR
            )
            name_label.pack(side=tk.LEFT)
            
            # 传感器值和单位
            value_frame = ttk.Frame(panel, style="PanelValue.TFrame")
            value_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            value_label = ttk.Label(
                value_frame,
                textvariable=self.sensor_data[sensor_id],
                font=("微软雅黑", 30, "bold"),
                foreground=config["color"],
                background=PANEL_BG_COLOR
            )
            value_label.pack(side=tk.LEFT)
            
            if config["unit"]:
                unit_label = ttk.Label(
                    value_frame,
                    text=config["unit"],
                    font=("微软雅黑", 12),
                    foreground=TEXT_COLOR,
                    background=PANEL_BG_COLOR
                )
                unit_label.pack(side=tk.LEFT, anchor="s", padx=(5, 0), pady=(0, 5))
            
            # 更新列和行索引
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # 设置行的比重
        for i in range(row + 1):  # 加1是因为上面的row是最后一行的索引
            sensors_frame.grid_rowconfigure(i, weight=1, uniform="row")
    
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_frame = ttk.Frame(parent, style="Status.TFrame")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # 状态文本
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("微软雅黑", 10),
            foreground=STATUS_WARNING,  # 使用警告色，因为是模拟数据
            background=BG_COLOR
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        # 模拟数据切换按钮
        sim_button = ttk.Button(
            status_frame,
            textvariable=self.simulation_btn_text,
            command=self.toggle_simulation,
            style="Accent.TButton"
        )
        sim_button.pack(side=tk.RIGHT, padx=10)
    
    def update_time(self):
        """更新显示的时间"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time.set(current_time)
        self.root.after(1000, self.update_time)
    
    def update_simulated_data(self):
        """更新模拟的传感器数据"""
        if not self.simulation_enabled:
            return
        
        for sensor_id, config in SENSOR_CONFIG.items():
            if sensor_id in SIMULATED_DATA:
                try:
                    current_value = float(SIMULATED_DATA[sensor_id])
                    # 添加随机变化
                    variation = current_value * (random.random() * 0.06 - 0.03)  # -3% 到 +3%
                    new_value = current_value + variation
                    
                    # 确保值在传感器允许范围内
                    new_value = max(config["min"], min(config["max"], new_value))
                    
                    # 格式化显示
                    if "温度" in config["name"]:
                        formatted_value = f"{new_value:.1f}"
                    elif "湿度" in config["name"]:
                        formatted_value = f"{new_value:.1f}"
                    elif "aqi" in sensor_id.lower():
                        formatted_value = f"{int(new_value)}"
                    else:
                        formatted_value = f"{new_value:.1f}"
                    
                    # 更新显示和存储的值
                    self.sensor_data[sensor_id].set(formatted_value)
                    SIMULATED_DATA[sensor_id] = formatted_value
                    
                except (ValueError, TypeError):
                    # 对于非数值型的，直接使用原值
                    self.sensor_data[sensor_id].set(SIMULATED_DATA[sensor_id])
        
        # 每5秒更新一次
        self.root.after(5000, self.update_simulated_data)
    
    def toggle_simulation(self):
        """切换模拟数据模式"""
        self.simulation_enabled = not self.simulation_enabled
        
        if self.simulation_enabled:
            self.simulation_btn_text.set("关闭模拟数据")
            self.status_text.set("状态: 已启用模拟数据")
            logging.info("已启用模拟数据模式")
            # 启动模拟数据更新
            self.update_simulated_data()
        else:
            self.simulation_btn_text.set("启用模拟数据")
            self.status_text.set("状态: 已停用模拟数据")
            logging.info("已停用模拟数据模式")
    
    def on_closing(self):
        """窗口关闭处理"""
        logging.info("应用程序正在关闭")
        self.root.destroy()

def configure_styles():
    """配置ttk样式"""
    style = ttk.Style()
    
    # 使用clam主题，它比较适合自定义
    style.theme_use("clam")
    
    # 配置基本样式
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
    style.configure("TButton", background=ACCENT_COLOR, foreground=TEXT_COLOR)
    
    # 自定义样式
    style.configure("Main.TFrame", background=BG_COLOR)
    style.configure("Header.TFrame", background=BG_COLOR)
    style.configure("Content.TFrame", background=BG_COLOR)
    style.configure("Sensors.TFrame", background=BG_COLOR)
    style.configure("Status.TFrame", background=BG_COLOR)
    
    # 传感器面板样式
    style.configure("SensorPanel.TFrame", background=PANEL_BG_COLOR)
    style.configure("PanelHeader.TFrame", background=PANEL_BG_COLOR)
    style.configure("PanelValue.TFrame", background=PANEL_BG_COLOR)
    
    # 标题和内容标签样式
    style.configure("Title.TLabel", background=BG_COLOR, foreground=ACCENT_COLOR, font=("微软雅黑", 20, "bold"))
    
    # 按钮样式
    style.configure("Accent.TButton", background=ACCENT_COLOR)
    
    # 天气信息框样式
    style.configure("Weather.TFrame", background=BG_COLOR)

def main():
    # 设置应用
    root = tk.Tk()
    configure_styles()
    
    # 创建仪表盘实例
    app = PureDashboard(root)
    
    # 运行应用
    print("智慧校园环境监测系统 - 纯净版启动中...")
    logging.info("应用程序启动")
    root.mainloop()
    
if __name__ == "__main__":
    main()
