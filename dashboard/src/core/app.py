# -*- coding: utf-8 -*-
# =============================================================================
# 智慧校园仪表盘系统 - 优化版本
# 
# 优化记录：
# 1. 图表更新逻辑改进：修复了self.last_chart_update为None时的TypeError问题
# 2. UV风险等级处理增强：特殊处理"siot/uv风险等级"主题，防止未处理警告
# 3. 错误处理机制优化：改进了未处理主题的日志和尝试自动匹配
# 4. 内存管理功能：添加了定期内存清理功能，防止长时间运行时的内存泄漏
# 5. 视频帧处理稳定性改进：增加了视频帧计数和时间戳跟踪
# 6. 系统状态监控：实现了自动检测MQTT连接、传感器数据和视频流状态
# 7. 简化重连逻辑：优化了MQTT断开重连的处理，减少资源占用
# 8. 增强的UI反馈：系统状态变化会即时反映在界面上
# 9. 数据处理增强：支持多种格式的传感器数据解析（JSON、文本、百分比等）
# 10. 模拟模式改进：长时间未接收数据时可自动切换到模拟模式
# =============================================================================

print("脚本开始执行...") # DEBUG: Script start

# 导入必要的库
# 添加日志功能
import logging
import os
from datetime import datetime

# 创建日志目录
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
log_dir = os.path.join(base_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_file = os.path.join(log_dir, f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logging.info("智慧校园仪表盘启动")

# 确保导入json库
# 用于Basic Authentication
# 用于URL编码Topic
# 用于MQTT通信
try:
    from PIL import Image, ImageTk, UnidentifiedImageError
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告：Pillow库未安装或导入失败，视频/图像显示功能将不可用。请运行 'pip install Pillow' 进行安装。")

import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import paho.mqtt.client as mqtt
import json
import base64
import io # Added io import
from PIL import Image, ImageTk, UnidentifiedImageError
from datetime import datetime, timedelta
import time
import threading
import random
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import dates as mdates
import locale # Added locale import
import socket # For network error handling in MQTT connect
import requests

# --- Matplotlib Imports ---
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
    plt.style.use('dark_background') # Apply dark theme to matplotlib charts
    # 解决中文显示问题
    # 尝试使用 'PingFang SC'，如果找不到，尝试 'Heiti TC' 或其他macOS常见中文字体
    # 确保字体名称与系统中安装的名称完全一致
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("警告：matplotlib库未安装或导入失败，图表功能将不可用。请运行 'pip install matplotlib' 进行安装。")

# --- Weather API Configuration ---
WEATHER_API_KEY = "d24595021efb5faa04f4f6744c94086f"
WEATHER_CITY_NAME = "Tianshui" # 天水
WEATHER_API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={WEATHER_CITY_NAME}&appid={WEATHER_API_KEY}&units=metric&lang=zh_cn"
WEATHER_FETCH_INTERVAL = 1800 # 30 minutes in seconds (30 * 60)

# --- MQTT Configuration ---
# 尝试加载配置文件
try:
    config_file = os.path.join(base_dir, "config", "config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            # 读取配置
            SIOT_SERVER_HTTP = config.get("siot_server_http", "http://192.168.1.129:8080")
            SIOT_USERNAME = config.get("siot_username", "siot")
            SIOT_PASSWORD = config.get("siot_password", "dfrobot")
            MQTT_BROKER_HOST = config.get("mqtt_broker_host", "192.168.1.129")
            MQTT_BROKER_PORT = config.get("mqtt_broker_port", 1883)
            MQTT_CLIENT_ID = config.get("mqtt_client_id", "smart_campus_dashboard_client_001")
            MQTT_CAMERA_TOPIC = config.get("mqtt_camera_topic", "sc/camera/stream")
            MQTT_WEATHER_TOPIC = config.get("mqtt_weather_topic", "sc/weather/data")
            logging.info("成功加载配置文件")
    else:
        logging.warning(f"配置文件不存在: {config_file}，使用默认配置")
        SIOT_SERVER_HTTP = "http://192.168.1.129:8080"
        SIOT_USERNAME = "siot"
        SIOT_PASSWORD = "dfrobot"
        MQTT_BROKER_HOST = "192.168.1.129"
        MQTT_BROKER_PORT = 1883
        MQTT_CLIENT_ID = "smart_campus_dashboard_client_001"
        MQTT_CAMERA_TOPIC = "sc/camera/stream"
        MQTT_WEATHER_TOPIC = "sc/weather/data"
except Exception as e:
    logging.error(f"加载配置文件时出错: {e}，使用默认配置")
    SIOT_SERVER_HTTP = "http://192.168.1.129:8080"
    SIOT_USERNAME = "siot"
    SIOT_PASSWORD = "dfrobot"
    MQTT_BROKER_HOST = "192.168.1.129"
    MQTT_BROKER_PORT = 1883
    MQTT_CLIENT_ID = "smart_campus_dashboard_client_001"
    MQTT_CAMERA_TOPIC = "sc/camera/stream"
    MQTT_WEATHER_TOPIC = "sc/weather/data"
MQTT_TOPICS = [
    "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
    "siot/紫外线指数", "siot/uv风险等级", "siot/噪音", MQTT_CAMERA_TOPIC, MQTT_WEATHER_TOPIC
]
mqtt_data_cache = {topic: "--" for topic in MQTT_TOPICS} # 初始化缓存
mqtt_data_cache[MQTT_CAMERA_TOPIC] = None # Initialize camera data as None
# 使用指定的API版本来初始化客户端，以消除弃用警告
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# 模拟数据，在无法连接服务器时使用
simulation_data = {
    "环境温度": "25.6",
    "环境湿度": "68.2",
    "aqi": "52",
    "tvoc": "320",
    "eco2": "780",
    "紫外线指数": "2.8",
    "uv风险等级": "低",
    "噪音": "45.5"
}

# 全局变量，记录是否使用模拟数据
use_simulation = False

# --- UI Constants ---
# Updated Theme: Deeper Blue, Lighter Panels, Icons
PAGE_BG_COLOR = "#0A1E36"  # Darker tech blue for main page background
PANEL_BG_COLOR = "#102A43" # Slightly lighter blue for panels, charts, AI section
CHART_BG_COLOR = PANEL_BG_COLOR # Charts use panel background
VIDEO_BG_COLOR = "#000000" # Video区域纯黑背景

BORDER_LINE_COLOR = "#888888" # Thin grey for border lines

TEXT_COLOR_HEADER = "#E0EFFF"
TEXT_COLOR_NORMAL = "#C0D0E0"
TEXT_COLOR_VALUE = "#64FFDA"
TEXT_COLOR_UNIT = "#A0B0C0"
TEXT_COLOR_PANEL_TITLE = "#E0EFFF"
TEXT_COLOR_AI_TITLE = "#64FFDA"
TEXT_COLOR_AI_ADVICE = "#C0D0E0"
TEXT_COLOR_STATUS_OK = "#33FF99"
TEXT_COLOR_STATUS_FAIL = "#FF6666"
TEXT_COLOR_STATUS_SIM = "#FFD700"
TEXT_COLOR_VERSION = "#8090A0"
CHART_LINE_COLOR = "#00BFFF"
CHART_TEXT_COLOR = "#C0D0E0"

FONT_APP_TITLE = ("Helvetica", 30, "bold")
FONT_TIMESTAMP = ("Helvetica", 14, "bold") # Increased font size and made bold
FONT_PANEL_ICON = ("Helvetica", 16) # New font for icons
FONT_PANEL_TITLE = ("Helvetica", 14, "bold") # Adjusted for data item label
FONT_PANEL_LABEL = ("Helvetica", 12) 
FONT_PANEL_VALUE = ("Helvetica", 30, "bold")
FONT_PANEL_UNIT = ("Helvetica", 12)
FONT_AI_SECTION_TITLE = ("Helvetica", 16, "bold")
FONT_AI_ADVICE = ("Helvetica", 12)
FONT_STATUS = ("Helvetica", 11)
# FONT_BUTTON = ("Helvetica", 10, "bold") # Not currently used

APP_VERSION = "v1.2.0" # 更新版本号反映新变更
APP_TITLE = "烟铺小学智慧校园环境监测系统"

# --- Global UI References & StringVars ---
# root = None # Will be instance variable self.root
# time_var = None # Will be instance variable self.time_var
# connection_status_var = None # Will be instance variable self.connection_status_var
# sim_button_text_var = None # Will be instance variable self.sim_button_text_var
# data_vars = {} # Will be instance variable self.data_vars
# ai_advice_text_widget = None # Will be instance variable self.ai_advice_text_widget
# app = None # Global app instance, will be created in __main__

# These can remain global if they are truly UI widget references not directly tied to app state
# or if they are configured outside the class context initially.
# However, for better encapsulation, they could also become instance variables if primarily
# managed by the app instance. For now, let's assume they might be accessed by global functions
# that are not yet methods.
connection_status_label_widget = None
sim_button_widget = None

# video_image_label and video_photo_image are handled as self.camera_image_label and self.video_photo_image

# Weather StringVars - These will be deprecated in favor of data_vars entries
# weather_desc_var = None
# wind_speed_var = None

# --- Chart Specific Globals ---
CHART_HISTORY_MAXLEN = 20 # Maximum number of data points for charts - This is used in __init__

# Global history deques and their specific MAXLENs are removed to use self.chart_data_history consistently.
# TEMP_HISTORY_MAXLEN = 50
# HUMI_HISTORY_MAXLEN = 50
# NOISE_HISTORY_MAXLEN = 50
# temp_history = deque(maxlen=TEMP_HISTORY_MAXLEN)
# humi_history = deque(maxlen=HUMI_HISTORY_MAXLEN)
# noise_history = deque(maxlen=NOISE_HISTORY_MAXLEN)

# Temperature Chart
chart_canvas_widget_temp = None
fig_temp_chart = None
ax_temp_chart = None

# Humidity Chart
chart_canvas_widget_humi = None
fig_humi_chart = None
ax_humi_chart = None

# Noise Chart (Renamed from AQI)
chart_canvas_widget_noise = None # Renamed from fig_canvas_widget_aqi
fig_noise_chart = None # Renamed from fig_aqi_chart
ax_noise_chart = None # Renamed from ax_aqi_chart

# Mapping for data processing and display
# base_topic_name is used with get_topic_value
# display_title is shown on the panel
# unit is the unit string
panel_configs = {
    "temp": {"base_topic_name": "环境温度", "display_title": "环境温度", "unit": "°C", "icon": "🌡️"},
    "weather_desc": {"base_topic_name": "weather_api_desc", "display_title": "天气状况", "unit": "", "icon": "☁️"},
    "wind_speed": {"base_topic_name": "weather_api_wind", "display_title": "风速", "unit": "m/s", "icon": "🌬️"},
    "humi": {"base_topic_name": "环境湿度", "display_title": "环境湿度", "unit": "%RH", "icon": "💧"},
    "aqi": {"base_topic_name": "aqi", "display_title": "AQI", "unit": "", "icon": "💨"},
    "eco2": {"base_topic_name": "eco2", "display_title": "eCO2", "unit": "ppm", "icon": "🌿"},
    "tvoc": {"base_topic_name": "tvoc", "display_title": "TVOC", "unit": "ppb", "icon": "🧪"},
    "uv": {"base_topic_name": "紫外线指数", "display_title": "紫外线指数", "unit": "", "icon": "☀️"},
    "noise": {"base_topic_name": "噪音", "display_title": "噪音", "unit": "dB", "icon": "🔊"},
}
# Order of panels in the grid - this might become dynamic or less relevant if left panel shows all
# panel_order = ["eco2", "tvoc", "uv", "noise", "uvl"] # Original for reference

# --- UI Creation Functions ---
# create_header_section and create_main_layout will be moved into the class or refactored.
# Global create_main_layout and update_camera_stream are removed from here.

class SmartCampusDashboard:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title(APP_TITLE) # Use constant
        self.root.geometry("1200x800")
        self.root.configure(bg=PAGE_BG_COLOR)

        # Initialize instance variables for UI elements and data
        self.time_var = tk.StringVar()
        self.connection_status_var = tk.StringVar(value="MQTT状态: 初始化...")
        self.sim_button_text_var = tk.StringVar(value="启用模拟数据")
        
        self.panel_configs = panel_configs # Initialize self.panel_configs from global
        self.MQTT_TOPICS = MQTT_TOPICS # Initialize self.MQTT_TOPICS from global
        self.MQTT_CAMERA_TOPIC = MQTT_CAMERA_TOPIC # Initialize self.MQTT_CAMERA_TOPIC from global
        self.MQTT_WEATHER_TOPIC = MQTT_WEATHER_TOPIC # Initialize self.MQTT_WEATHER_TOPIC from global

        # MQTT连接相关变量
        self._mqtt_reconnect_thread = None
        self._mqtt_client = None
        self._reconnect_attempts = 0
        self._mqtt_connected = False
        self.last_data_received_time = None
        self.debug_mode = True  # 启用调试模式，显示更详细的连接信息

        self.data_vars = {key: tk.StringVar(value="--") for key in self.panel_configs.keys()}
        self.sensor_data_history = {key: deque(maxlen=CHART_HISTORY_MAXLEN) for key in self.panel_configs.keys() if not self.panel_configs[key].get("is_weather_metric", False) and not self.panel_configs[key].get("is_status_metric", False)}
        
        self.weather_data = {} # To store fetched weather data
        self.weather_error = None # To store any error during weather fetch

        self.ai_advice_text_widget = None
        self.connection_status_label_widget = None
        self.sim_button_widget = None
        self.camera_image_label = None 
        self.video_photo_image = None # Keep a reference to the PhotoImage

        self.use_simulation = False
        self._debug_video_update_counter = 0 # For debugging video updates
        self.video_frames_received = 0 # 视频帧计数器
        self.last_video_frame_time = None # 最后接收到视频帧的时间
        self.last_data_received_time = None # 追踪最后一次数据接收时间
        self.last_chart_update = datetime.now() # 追踪最后一次图表更新时间

        # Chart related (placeholders if Matplotlib not available)
        self.charts = {} # To store chart objects (Figure, Axes, Canvas)
        # 修改数据结构，存储(timestamp, value)元组，用于时间序列图表
        self.chart_data_history = {
            'temperature': deque(maxlen=CHART_HISTORY_MAXLEN),
            'humidity': deque(maxlen=CHART_HISTORY_MAXLEN),
            'noise': deque(maxlen=CHART_HISTORY_MAXLEN)
        }

        self.setup_ui_layout()
        self.setup_charts() # Call chart setup
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID, clean_session=True)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.username_pw_set(SIOT_USERNAME, SIOT_PASSWORD)

        self.connect_mqtt()
        self.update_time_display() # Start the clock
        self.fetch_weather_data_periodic() # Start periodic weather fetching
        self.check_system_status() # Start periodic system status checks
        
        # 启动内存清理定时任务（首次在启动后10分钟执行）
        self.root.after(10 * 60 * 1000, self.clean_memory)  

        print("DEBUG: SmartCampusDashboard initialized")

    def create_main_layout(self, parent):
        print("DEBUG: self.create_main_layout called")

        main_regions_frame = tk.Frame(parent, bg=PAGE_BG_COLOR)
        main_regions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 重新调整布局比例：左侧数据面板2，中间视频区域3，右侧图表区域8
        # 进一步减小左侧区域宽度，增加右侧图表区域宽度，使图表显示更清晰
        main_regions_frame.grid_columnconfigure(0, weight=2) # 左侧数据面板
        main_regions_frame.grid_columnconfigure(1, weight=3, minsize=300) # 中间视频区域，适当增加宽度
        main_regions_frame.grid_columnconfigure(2, weight=8) # 右侧图表区域，进一步增加宽度比例
        main_regions_frame.grid_rowconfigure(0, weight=1)

        # --- Left Region (Data Panels) ---
        left_region_frame = tk.Frame(main_regions_frame, bg=PAGE_BG_COLOR, padx=5, pady=5)
        left_region_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        data_panels_container = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR)
        data_panels_container.pack(expand=False, fill='x', anchor='n')
        
        # left_panel_keys = list(self.panel_configs.keys())
        left_panel_keys = list(self.panel_configs.keys())
        
        for key in left_panel_keys:
            # if key not in self.panel_configs:
            if key not in self.panel_configs:
                print(f"警告: left_panel_keys 中的键 '{key}' 在 self.panel_configs 中未找到。")
                continue
            
            # config = self.panel_configs[key]
            config = self.panel_configs[key]
            display_title = config.get("display_title", key.capitalize())
            unit = config.get("unit", "")
            icon_char = config.get("icon", "")
        
            panel_frame = tk.Frame(data_panels_container, bg=PANEL_BG_COLOR, pady=5, padx=10,
                                   highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
            panel_frame.pack(fill="x", pady=3, padx=5)
        
            # 优化面板内部布局，使其更加美观
            content_row_frame = tk.Frame(panel_frame, bg=PANEL_BG_COLOR)
            content_row_frame.pack(fill="x")
            
            # 左侧容器：图标和标题
            left_container = tk.Frame(content_row_frame, bg=PANEL_BG_COLOR)
            left_container.pack(side="left", padx=5)
            
            # 将标题和图标组合在一起，保持统一对齐
            if icon_char:
                icon_label = tk.Label(left_container, text=icon_char, font=FONT_PANEL_ICON, fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR)
                icon_label.pack(side="left", padx=(0, 5))
            
            title_label = tk.Label(left_container, text=display_title + ":", font=FONT_PANEL_LABEL, fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR)
            title_label.pack(side="left", padx=(0, 5))
            
            # 右侧容器：数值和单位
            value_unit_frame = tk.Frame(content_row_frame, bg=PANEL_BG_COLOR)
            value_unit_frame.pack(side="right", padx=8)  # 增加右侧padding，使数值显示更美观
            
            if key in self.data_vars and self.data_vars[key] is not None:
                value_label = tk.Label(value_unit_frame, textvariable=self.data_vars[key], font=FONT_PANEL_VALUE, 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR, width=5, anchor="e")  # 固定宽度，右对齐
                value_label.pack(side="left", anchor="s")
            else:
                tk.Label(value_unit_frame, text="--", font=FONT_PANEL_VALUE, fg="red", bg=PANEL_BG_COLOR, 
                        width=5, anchor="e").pack(side="left", anchor="s")  # 固定宽度，右对齐
                print(f"DEBUG: self.data_vars missing or None for key: {key} in create_main_layout")
            
            # 确保单位始终显示
            if unit:
                unit_label = tk.Label(value_unit_frame, text=unit, font=FONT_PANEL_UNIT, fg=TEXT_COLOR_UNIT, bg=PANEL_BG_COLOR)
                unit_label.pack(side="left", anchor="s", padx=(3, 0), pady=(0, 3))
                
                # 保存单位标签的引用，以便在后续更新中使用
                if not hasattr(self, 'unit_labels'):
                    self.unit_labels = {}
                self.unit_labels[key] = unit_label
                
        # --- Version, Simulation Button, and Connection Status (REMOVED from Bottom of Left Region) ---
        # The following block has been removed as these elements are moved to the header:
        # bottom_info_frame = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR)
        # bottom_info_frame.pack(side=tk.BOTTOM, fill="x", pady=(10,0), padx=5)
        # version_label = tk.Label(bottom_info_frame, text=f"版本: {APP_VERSION}", font=FONT_STATUS, fg=TEXT_COLOR_VERSION, bg=PAGE_BG_COLOR, bd=0)
        # version_label.pack(side="left", padx=(5, 5))
        # self.sim_button_widget = tk.Button(bottom_info_frame, textvariable=self.sim_button_text_var, font=FONT_STATUS, fg=TEXT_COLOR_STATUS_SIM, bg=PANEL_BG_COLOR,
        #                               activebackground=PANEL_BG_COLOR, bd=0, highlightthickness=0, command=self.toggle_simulation)
        # self.sim_button_widget.pack(side="left", padx=5, pady=5)
        # self.connection_status_label_widget = tk.Label(bottom_info_frame, textvariable=self.connection_status_var, font=FONT_STATUS, fg=TEXT_COLOR_STATUS_FAIL, bg=PAGE_BG_COLOR)
        # self.connection_status_label_widget.pack(side="right", padx=(5, 5))

        # --- Middle Region (Video Top, Gauges Middle, AI Bottom) ---
        middle_region_frame = tk.Frame(main_regions_frame, bg=PAGE_BG_COLOR, padx=5, pady=5)
        middle_region_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        middle_region_frame.grid_rowconfigure(0, weight=5)  # 视频区域更大
        middle_region_frame.grid_rowconfigure(1, weight=2)  # 仪表盘区域
        middle_region_frame.grid_rowconfigure(2, weight=1)  # AI建议区域
        middle_region_frame.grid_columnconfigure(0, weight=1)
        
        video_outer_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR,
                          highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        video_outer_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        
        # 视频区域标题栏
        video_title_frame = tk.Frame(video_outer_frame, bg=PANEL_BG_COLOR)
        video_title_frame.pack(fill="x", anchor="nw", padx=10, pady=5)
        
        # 左侧标题
        tk.Label(video_title_frame, text="实时监控视频", font=FONT_PANEL_TITLE, 
                fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR).pack(side=tk.LEFT)
        
        # 右侧状态指示器（用于显示视频帧接收状态）
        self.video_status_var = tk.StringVar(value="等待视频流...")
        self.video_status_label = tk.Label(video_title_frame, textvariable=self.video_status_var,
                                          font=("Helvetica", 9), fg=TEXT_COLOR_STATUS_FAIL, bg=PANEL_BG_COLOR)
        self.video_status_label.pack(side=tk.RIGHT, padx=5)
        
        # 创建一个内部框架来容纳视频画面，设置更大的最小尺寸确保视频区域足够大
        video_inner_frame = tk.Frame(video_outer_frame, bg=PANEL_BG_COLOR, width=450, height=340)
        video_inner_frame.pack(expand=True, fill="both", padx=10, pady=10)
        video_inner_frame.pack_propagate(False)  # 防止内部控件改变框架大小
        
        # 视频显示区域增加边框
        video_display_frame = tk.Frame(video_inner_frame, bg="#1a1a1a", bd=2, relief=tk.SUNKEN)
        video_display_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        # 使用深色背景创建视频标签，改善视觉效果，优化显示
        self.camera_image_label = tk.Label(video_display_frame, bg="#000000", 
                                         text="等待视频流...", fg="#888888", font=("Helvetica", 14),
                                         borderwidth=0, highlightthickness=0)  # 移除边框，使视频显示更干净
        self.camera_image_label.pack(expand=True, fill="both", padx=2, pady=2)  # 添加适当的内边距

        # 创建仪表盘区域 - 放在视频下面
        gauge_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR,
                              highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        gauge_frame.grid(row=1, column=0, sticky="nsew", pady=(5,0))
        
        # 分成左右两个区域，左侧AQI仪表盘，右侧UV风险等级仪表盘
        gauge_frame.grid_columnconfigure(0, weight=1)
        gauge_frame.grid_columnconfigure(1, weight=1)
        
        # --- AQI仪表盘 ---
        aqi_frame = tk.Frame(gauge_frame, bg=PANEL_BG_COLOR, padx=10, pady=5)
        aqi_frame.grid(row=0, column=0, sticky="nsew", padx=(5,2), pady=5)
        
        # AQI标题
        tk.Label(aqi_frame, text="空气质量指数 (AQI)", font=FONT_PANEL_TITLE, 
                fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR).pack(anchor="n", pady=(5,10))
        
        # AQI值显示 - 增强视觉效果
        aqi_display_frame = tk.Frame(aqi_frame, bg=PANEL_BG_COLOR)
        aqi_display_frame.pack(fill="x", pady=5)
        
        # 左侧放置圆形指示器
        self.aqi_indicator_canvas = tk.Canvas(aqi_display_frame, width=50, height=50, 
                                           bg=PANEL_BG_COLOR, highlightthickness=0)
        self.aqi_indicator_canvas.pack(side=tk.LEFT, padx=(20, 0))
        
        # 右侧放置值和等级
        aqi_value_frame = tk.Frame(aqi_display_frame, bg=PANEL_BG_COLOR)
        aqi_value_frame.pack(side=tk.LEFT, expand=True, fill="x", padx=15)
        
        # 创建AQI值的标签 - 更大字体
        self.aqi_value_label = tk.Label(aqi_value_frame, text="--", font=("Helvetica", 28, "bold"), 
                                      fg="#4CAF50", bg=PANEL_BG_COLOR)
        self.aqi_value_label.pack(anchor="center")
        
        # AQI等级 - 更醒目
        self.aqi_level_label = tk.Label(aqi_value_frame, text="--", font=("Helvetica", 14), 
                                       fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.aqi_level_label.pack(anchor="center", pady=2)
        
        # AQI描述标签 - 添加详细说明
        self.aqi_desc_label = tk.Label(aqi_frame, text="--", font=("Helvetica", 10), 
                                     fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR, wraplength=180)
        self.aqi_desc_label.pack(anchor="center", pady=(5, 10), fill="x")
        
        # --- UV风险等级仪表盘 ---
        uv_frame = tk.Frame(gauge_frame, bg=PANEL_BG_COLOR, padx=10, pady=5)
        uv_frame.grid(row=0, column=1, sticky="nsew", padx=(2,5), pady=5)
        
        # UV标题
        tk.Label(uv_frame, text="紫外线风险等级", font=FONT_PANEL_TITLE, 
                fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR).pack(anchor="n", pady=(5,10))
        
        # UV值显示区域
        uv_display_frame = tk.Frame(uv_frame, bg=PANEL_BG_COLOR)
        uv_display_frame.pack(fill="x", pady=5)
        
        # UV值和等级显示
        uv_value_frame = tk.Frame(uv_display_frame, bg=PANEL_BG_COLOR)
        uv_value_frame.pack(side=tk.TOP, fill="x", pady=5)
        
        # 创建UV值的标签 - 更大字体
        self.uv_value_label = tk.Label(uv_value_frame, text="--", font=("Helvetica", 28, "bold"), 
                                      fg="#FFA500", bg=PANEL_BG_COLOR)
        self.uv_value_label.pack(anchor="center")
        
        # UV等级 - 更醒目
        self.uv_level_label = tk.Label(uv_value_frame, text="--", font=("Helvetica", 14), 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.uv_level_label.pack(anchor="center", pady=2)
        
        # 创建UV进度条指示器
        self.uv_indicator_canvas = tk.Canvas(uv_frame, width=200, height=40, 
                                          bg=PANEL_BG_COLOR, highlightthickness=0)
        self.uv_indicator_canvas.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # UV描述标签 - 添加详细说明
        self.uv_desc_label = tk.Label(uv_frame, text="--", font=("Helvetica", 10), 
                                     fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR, wraplength=180)
        self.uv_desc_label.pack(anchor="center", pady=(5, 10), fill="x")

        # 创建AI建议区域
        ai_advice_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR, pady=5, padx=10,
                                   highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        ai_advice_frame.grid(row=2, column=0, sticky="nsew", pady=(5,0))

        tk.Label(ai_advice_frame, text="AI建议", font=FONT_AI_SECTION_TITLE, fg=TEXT_COLOR_AI_TITLE, bg=PANEL_BG_COLOR).pack(anchor="nw", padx=10, pady=5)

        self.ai_advice_text_widget = tk.Text(ai_advice_frame, height=4, wrap=tk.WORD, bg=PANEL_BG_COLOR, fg=TEXT_COLOR_AI_ADVICE,
                                 font=FONT_AI_ADVICE, bd=0, highlightthickness=0)
        self.ai_advice_text_widget.pack(expand=True, fill="both", padx=10, pady=(0,5))
        self.ai_advice_text_widget.insert(tk.END, "欢迎使用智慧校园环境监测系统")
        self.ai_advice_text_widget.config(state=tk.DISABLED)

        # --- Right Region (Charts) ---
        right_region_frame = tk.Frame(main_regions_frame, bg=PAGE_BG_COLOR, padx=5, pady=5)
        right_region_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0)) 

        self.charts_frame = tk.Frame(right_region_frame, bg=PAGE_BG_COLOR)
        self.charts_frame.pack(expand=True, fill="both", pady=0, padx=0)

        self.charts_frame.grid_rowconfigure(0, weight=1)
        self.charts_frame.grid_rowconfigure(1, weight=1)
        self.charts_frame.grid_rowconfigure(2, weight=1)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        
        print("DEBUG: self.create_main_layout finished")
        return main_regions_frame

    def update_camera_stream(self, data):
        """更新视频流显示"""
        self._debug_video_update_counter += 1
        print(f"DEBUG: update_camera_stream 接收到数据类型: {type(data)}")

        if not PIL_AVAILABLE:
            if self._debug_video_update_counter % 50 == 1:  # 减少日志频率
                print("DEBUG: Pillow (PIL) 不可用，无法处理视频流。")
            return

        try:
            # 验证输入数据，支持更多数据格式
            image_data_b64 = None
            
            # 支持dict格式 {"image": base64_data}
            if isinstance(data, dict):
                # 检查常见的键名模式
                possible_keys = ["image", "img", "frame", "data", "imageData", "base64"]
                for key in possible_keys:
                    if key in data and isinstance(data[key], str):
                        image_data_b64 = data[key]
                        print(f"DEBUG: 从字典中键'{key}'提取图像数据，长度: {len(image_data_b64)}")
                        break
            # 支持直接传递base64字符串
            elif isinstance(data, str):
                # 检查是否看起来像base64数据 (常见前缀或长度)
                if (data.startswith("data:image") or 
                    len(data) > 100 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in data[:20])):
                    image_data_b64 = data
                    print(f"DEBUG: 直接使用字符串数据，长度: {len(data)}")
            
            # 如果找到的是data URI scheme格式 (例如: "data:image/jpeg;base64,/9j/4AA...")
            if image_data_b64 and image_data_b64.startswith("data:"):
                try:
                    # 提取base64部分
                    image_data_b64 = image_data_b64.split(",", 1)[1]
                except IndexError:
                    print("错误: 无效的Data URI格式")
                    return
            
            if not image_data_b64:
                if self._debug_video_update_counter % 10 == 1:  # 减少日志频率
                    print(f"DEBUG: 无法获取有效的图像数据。数据类型: {type(data)}")
                return
                
            # 解码Base64数据
            try:
                # 尝试清理错误的填充字符
                if len(image_data_b64) % 4 != 0:
                    missing_padding = 4 - len(image_data_b64) % 4
                    image_data_b64 += "=" * missing_padding
                
                image_bytes = base64.b64decode(image_data_b64)
            except base64.binascii.Error as b64_error:
                print(f"错误: Base64解码错误: {b64_error}。数据是否正确编码? 数据前64字符: {image_data_b64[:64]}")
                # 尝试移除非base64字符并再次解码
                try:
                    cleaned_data = ''.join(c for c in image_data_b64 if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
                    image_bytes = base64.b64decode(cleaned_data)
                    print("成功: 通过清理非base64字符修复了数据")
                except:
                    print("错误: 即使清理后仍无法解码数据")
                    return
            except Exception as e:
                print(f"错误: Base64解码过程中出现意外错误: {type(e).__name__} - {e}")
                return

            if not image_bytes:
                print("错误: 解码后的图像数据为空。")
                return

            # 打开图像
            try:
                img_io = io.BytesIO(image_bytes)
                image = Image.open(img_io)
            except UnidentifiedImageError as uie:
                print(f"错误: 无法识别图像文件格式。Base64数据是否为有效图像? 详情: {uie}")
                return
            except OSError as ose:
                print(f"错误: 打开图像时出现OS错误: {ose}")
                return
            except Exception as e:
                print(f"错误: 打开图像时出现意外错误: {type(e).__name__} - {e}")
                return
                    
            # 获取视频框架尺寸 - 使用配置的尺寸而不是容器的当前尺寸
            # 这样可以确保视频始终以固定且优化的尺寸显示
            target_width, target_height = 450, 340  # 使用更大的目标尺寸，提高清晰度
            
            # 获取容器尺寸作为备选
            container_width = self.camera_image_label.winfo_width()
            container_height = self.camera_image_label.winfo_height()
            
            # 如果容器尺寸合理且大于默认目标尺寸，则使用容器尺寸
            if container_width > 100 and container_height > 100:
                if container_width > target_width:
                    target_width = min(container_width, 600)  # 限制最大宽度
                if container_height > target_height:
                    target_height = min(container_height, 480)  # 限制最大高度
                    
            original_width, original_height = image.size
            if original_width == 0 or original_height == 0:
                print("错误: 原始图像尺寸为零。")
                return

            aspect_ratio = original_width / float(original_height)  # 确保浮点除法
            
            # 计算合适的尺寸，保持宽高比
            if target_width / aspect_ratio <= target_height:
                new_width = target_width
                new_height = int(new_width / aspect_ratio) if aspect_ratio > 0 else target_width  # 处理aspect_ratio = 0的情况
            else:
                new_height = target_height
                new_width = int(new_height * aspect_ratio)

            # 确保尺寸合理
            if new_width <= 0: new_width = 320  # 设置最小宽度
            if new_height <= 0: new_height = 240  # 设置最小高度
                
            # 使用高质量的缩放方法调整图像大小
            try:
                # 使用LANCZOS重采样方法获得更好的图像质量
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"错误: 图像缩放失败: {e}")
                try:
                    # 降级到简单的重采样方法
                    image = image.resize((new_width, new_height), Image.Resampling.NEAREST)
                except Exception as e2:
                    print(f"错误: 所有缩放尝试均失败: {e2}")
                    return

            # 创建Tkinter可用的图像对象
            try:
                self.video_photo_image = ImageTk.PhotoImage(image)
            except RuntimeError as rte:
                print(f"错误: 创建ImageTk.PhotoImage时出现RuntimeError: {rte}。这可能是由损坏的图像数据或Tkinter问题导致的。")
                return
            except Exception as e:
                print(f"错误: 创建ImageTk.PhotoImage时出现意外错误: {type(e).__name__} - {e}")
                return

            # 更新图像显示
            if self.camera_image_label:
                # 更新图像，并保持对图像的引用（这很重要！）
                self.camera_image_label.config(image=self.video_photo_image, text="")
                self.camera_image_label.image = self.video_photo_image  # 保持引用以防垃圾回收
                
                # 更新标签尺寸以适应图像
                self.camera_image_label.config(width=new_width, height=new_height)
                
                # 更新视频状态指示器
                self.last_video_frame_time = datetime.now()
                if hasattr(self, 'video_status_var'):
                    now = self.last_video_frame_time.strftime("%H:%M:%S")
                    self.video_status_var.set(f"视频流正常 ({now})")
                    self.video_status_label.config(fg=TEXT_COLOR_STATUS_OK)
                
                # 更新视频帧计数
                self.video_frames_received += 1
                if self.video_frames_received % 20 == 0:
                    print(f"已接收 {self.video_frames_received} 帧视频数据")
            else:
                print("错误: camera_image_label为None，无法更新视频流。")

        except Exception as e:
            print(f"视频流更新中发生严重错误: {type(e).__name__} - {e}")
            logging.error(f"视频流更新发生严重错误: {str(e)}")
            # 可选：在视频标签上显示错误信息
            if hasattr(self, 'camera_image_label') and self.camera_image_label:
                self.camera_image_label.config(image="", text=f"视频处理错误")
                if hasattr(self, 'video_status_var') and hasattr(self, 'video_status_label'):
                    self.video_status_var.set("视频流错误")
                    self.video_status_label.config(fg=TEXT_COLOR_STATUS_FAIL)

    def setup_ui_layout(self):
        print("DEBUG: self.setup_ui_layout called")
        # Header Section
        header_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        header_frame.pack(fill="x", pady=(5,0))
        title_label = tk.Label(header_frame, text="智慧校园环境监测系统", font=FONT_APP_TITLE, fg=TEXT_COLOR_HEADER, bg=PAGE_BG_COLOR)
        title_label.pack(pady=5)

        # New frame for the info bar (time, version, sim button, status)
        info_bar_frame = tk.Frame(header_frame, bg=PAGE_BG_COLOR)
        info_bar_frame.pack(fill="x", pady=(0, 10))

        self.time_label_widget = tk.Label(info_bar_frame, textvariable=self.time_var, font=FONT_TIMESTAMP, fg=TEXT_COLOR_NORMAL, bg=PAGE_BG_COLOR)
        self.time_label_widget.pack(side="left", padx=(10, 5)) # Time on the far left

        version_label = tk.Label(info_bar_frame, text=f"版本: {APP_VERSION}", font=FONT_STATUS, fg=TEXT_COLOR_VERSION, bg=PAGE_BG_COLOR, bd=0)
        version_label.pack(side="left", padx=5) # Version next to time

        # Connection status to the far right
        self.connection_status_label_widget = tk.Label(info_bar_frame, textvariable=self.connection_status_var, font=FONT_STATUS, fg=TEXT_COLOR_STATUS_FAIL, bg=PAGE_BG_COLOR)
        self.connection_status_label_widget.pack(side="right", padx=(5, 10))
        
        # Simulation button to the left of connection status
        self.sim_button_widget = tk.Button(info_bar_frame, textvariable=self.sim_button_text_var, font=FONT_STATUS, 
                                          fg="#FFFFFF", bg="#007BFF", 
                                          activeforeground="#FFFFFF", activebackground="#0056b3", 
                                          relief=tk.RAISED, borderwidth=2,
                                          highlightthickness=0, command=self.toggle_simulation)
        self.sim_button_widget.pack(side="right", padx=5)
        # Original time_label_widget packing is removed as it's now in info_bar_frame
        # self.time_label_widget = tk.Label(header_frame, textvariable=self.time_var, font=FONT_TIMESTAMP, fg=TEXT_COLOR_NORMAL, bg=PAGE_BG_COLOR)
        # self.time_label_widget.pack(pady=(0,10))

        self.main_content_frame = self.create_main_layout(self.root)
        print("DEBUG: self.setup_ui_layout finished")

    def setup_charts(self):
        print("DEBUG: self.setup_charts called")
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib不可用，跳过图表设置。")
            if self.charts_frame: # Check if charts_frame exists
                # Display a message in each chart panel area if charts_frame is available
                placeholder_text = "图表功能不可用\n(Matplotlib未安装)"
                
                temp_chart_panel_placeholder = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                temp_chart_panel_placeholder.grid(row=0, column=0, sticky="nsew", pady=(0,5))
                tk.Label(temp_chart_panel_placeholder, text=placeholder_text, fg="red", bg=CHART_BG_COLOR, justify=tk.CENTER).pack(expand=True)

                humi_chart_panel_placeholder = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                humi_chart_panel_placeholder.grid(row=1, column=0, sticky="nsew", pady=5)
                tk.Label(humi_chart_panel_placeholder, text=placeholder_text, fg="red", bg=CHART_BG_COLOR, justify=tk.CENTER).pack(expand=True)

                noise_chart_panel_placeholder = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                noise_chart_panel_placeholder.grid(row=2, column=0, sticky="nsew", pady=(5,0))
                tk.Label(noise_chart_panel_placeholder, text=placeholder_text, fg="red", bg=CHART_BG_COLOR, justify=tk.CENTER).pack(expand=True)
            return

        # Adjusted figsize to better fit the allocated column width
        chart_figsize = (3.3, 2.2) # Approx 330x220 pixels at 100 DPI

        # Temperature Chart
        self.fig_temp_chart = Figure(figsize=chart_figsize, dpi=100, facecolor=CHART_BG_COLOR)
        self.ax_temp_chart = self.fig_temp_chart.add_subplot(111)
        self.ax_temp_chart.set_facecolor(CHART_BG_COLOR)
        self.ax_temp_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_temp_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_temp_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
        self.ax_temp_chart.spines['top'].set_color(CHART_BG_COLOR) 
        self.ax_temp_chart.spines['right'].set_color(CHART_BG_COLOR)
        self.ax_temp_chart.spines['left'].set_color(CHART_TEXT_COLOR)
        # self.fig_temp_chart.tight_layout(pad=0.5) # Keep tight_layout - moved after formatter for better layout

        # Add X and Y labels, remove old title
        self.ax_temp_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
        self.ax_temp_chart.set_ylabel("温度 (°C)", color=CHART_TEXT_COLOR, fontsize=8)
        # Format X-axis to show time in H:M format
        self.ax_temp_chart.xaxis.set_major_locator(mdates.MinuteLocator(interval=5)) # Tick every 5 minutes
        self.ax_temp_chart.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.fig_temp_chart.autofmt_xdate() # Auto-format date labels to prevent overlap
        self.fig_temp_chart.tight_layout(pad=0.5) # Apply tight_layout after all settings


        temp_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        temp_chart_panel.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        self.chart_canvas_widget_temp = FigureCanvasTkAgg(self.fig_temp_chart, master=temp_chart_panel)
        self.chart_canvas_widget_temp.draw()
        self.chart_canvas_widget_temp.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Humidity Chart
        self.fig_humi_chart = Figure(figsize=chart_figsize, dpi=100, facecolor=CHART_BG_COLOR)
        self.ax_humi_chart = self.fig_humi_chart.add_subplot(111)
        self.ax_humi_chart.set_facecolor(CHART_BG_COLOR)
        self.ax_humi_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_humi_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_humi_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
        self.ax_humi_chart.spines['top'].set_color(CHART_BG_COLOR)
        self.ax_humi_chart.spines['right'].set_color(CHART_BG_COLOR)
        self.ax_humi_chart.spines['left'].set_color(CHART_TEXT_COLOR)
        # self.fig_humi_chart.tight_layout(pad=0.5) # Keep tight_layout - moved after formatter

        # Add X and Y labels, remove old title
        self.ax_humi_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
        self.ax_humi_chart.set_ylabel("湿度 (%RH)", color=CHART_TEXT_COLOR, fontsize=8)
        # Format X-axis to show time in H:M format
        self.ax_humi_chart.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        self.ax_humi_chart.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.fig_humi_chart.autofmt_xdate()
        self.fig_humi_chart.tight_layout(pad=0.5)

        humi_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        humi_chart_panel.grid(row=1, column=0, sticky="nsew", pady=5)
        self.chart_canvas_widget_humi = FigureCanvasTkAgg(self.fig_humi_chart, master=humi_chart_panel)
        self.chart_canvas_widget_humi.draw()
        self.chart_canvas_widget_humi.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Noise Chart
        self.fig_noise_chart = Figure(figsize=chart_figsize, dpi=100, facecolor=CHART_BG_COLOR)
        self.ax_noise_chart = self.fig_noise_chart.add_subplot(111)
        self.ax_noise_chart.set_facecolor(CHART_BG_COLOR)
        self.ax_noise_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_noise_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
        self.ax_noise_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
        self.ax_noise_chart.spines['top'].set_color(CHART_BG_COLOR)
        self.ax_noise_chart.spines['right'].set_color(CHART_BG_COLOR)
        self.ax_noise_chart.spines['left'].set_color(CHART_TEXT_COLOR)
        # self.fig_noise_chart.tight_layout(pad=0.5) # Keep tight_layout - moved after formatter
        
        # Add X and Y labels, remove old title
        self.ax_noise_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
        self.ax_noise_chart.set_ylabel("噪音 (dB)", color=CHART_TEXT_COLOR, fontsize=8)
        # Format X-axis to show time in H:M format
        self.ax_noise_chart.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        self.ax_noise_chart.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.fig_noise_chart.autofmt_xdate()
        self.fig_noise_chart.tight_layout(pad=0.5)
        
        noise_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        noise_chart_panel.grid(row=2, column=0, sticky="nsew", pady=(5,0))
        self.chart_canvas_widget_noise = FigureCanvasTkAgg(self.fig_noise_chart, master=noise_chart_panel)
        self.chart_canvas_widget_noise.draw()
        self.chart_canvas_widget_noise.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        print("DEBUG: self.setup_charts finished")

    def update_time_display(self):
        now = datetime.now()
        # Get Chinese weekday name
        days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        day_name = days[now.weekday()]
        
        # Format the string in Chinese
        now_str = now.strftime(f"%Y年%m月%d日 {day_name} %H:%M:%S")
        
        self.time_var.set(now_str)
        
        # 更新窗口标题，显示数据接收状态
        if hasattr(self, 'last_data_received_time') and self.last_data_received_time:
            time_diff = (datetime.now() - self.last_data_received_time).total_seconds()
            if time_diff < 10:
                status = "数据正常接收中"
            elif time_diff < 30:
                status = "数据接收缓慢"
            else:
                status = "长时间未接收到数据"
            self.root.title(f"{APP_TITLE} - {status}")
        
        self.root.after(1000, self.update_time_display)

    def connect_mqtt(self):
        try:
            # 显示更详细的连接信息
            conn_msg = f"尝试连接MQTT服务器: 192.168.1.129:1883 (客户端ID: {MQTT_CLIENT_ID})"
            logging.info(conn_msg)
            if self.debug_mode:
                print(f"DEBUG: {conn_msg}")
            
            self.update_connection_status_display(False, "正在连接MQTT服务器...")
            self.mqtt_client.connect("192.168.1.129", 1883, 60)  # 修改为与测试脚本相同的地址
            self.mqtt_client.loop_start()
            logging.debug("MQTT客户端循环已启动")
        except socket.error as e:
            logging.error(f"MQTT连接错误: {e} - 无法连接到代理")
            self.update_connection_status_display(False, f"连接错误: {e}")
            # 启动自动重连线程
            if not hasattr(self, '_mqtt_reconnect_thread') or not self._mqtt_reconnect_thread or not self._mqtt_reconnect_thread.is_alive():
                self._mqtt_reconnect_thread = threading.Thread(target=self._mqtt_reconnect, daemon=True)
                self._mqtt_reconnect_thread.start()
        except Exception as e:
            logging.error(f"MQTT连接期间发生未知错误: {type(e).__name__} - {e}")
            self.update_connection_status_display(False, f"未知错误: {e}")
            # 启动自动重连线程
            if not hasattr(self, '_mqtt_reconnect_thread') or not self._mqtt_reconnect_thread or not self._mqtt_reconnect_thread.is_alive():
                self._mqtt_reconnect_thread = threading.Thread(target=self._mqtt_reconnect, daemon=True)
                self._mqtt_reconnect_thread.start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        logging.info(f"MQTT连接尝试结果: {mqtt.connack_string(rc)}, flags: {flags}")
        if rc == 0: # Connection successful
            self._mqtt_connected = True
            self._reconnect_attempts = 0
            self.update_connection_status_display(True)
            logging.info("MQTT连接成功，订阅主题...")
            # 使用通配符订阅所有SIOT主题
            client.subscribe("siot/#")
            logging.info("  已订阅: siot/# (通配符订阅)")
            
            # 同时保留对特定主题的订阅
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                logging.info(f"  已订阅: {topic}")
            # Also subscribe to weather topic if not already in MQTT_TOPICS for general messages
            if MQTT_WEATHER_TOPIC not in MQTT_TOPICS:
                 client.subscribe(MQTT_WEATHER_TOPIC)
                 logging.info(f"  已订阅天气主题: {MQTT_WEATHER_TOPIC}")
            self.fetch_weather_data() # Fetch initial weather data on connect
        elif rc == 5: # Not authorized
            print("MQTT连接失败，状态码：Not authorized")
            self.update_connection_status_display(False, "MQTT认证失败")
        else:
            error_string = mqtt.connack_string(rc)
            print(f"MQTT连接失败，状态码：{rc} ({error_string})")
            self.update_connection_status_display(False, f"MQTT连接失败: {error_string} (码 {rc})")

    def on_disconnect(self, client, userdata, flags, rc, properties=None): # Added flags for V2            # rc is a DisconnectReasonCode instance for V2, or an int for V1
        if isinstance(rc, int): # V1 compatibility or unexpected
            reason_code_int = rc
            reason_string = f"Return code: {rc}"
        else: # V2, rc is a ReasonCode object
            reason_code_int = rc.value if hasattr(rc, 'value') else -1 # Get int value if possible
            reason_string = str(rc)
            
        logging.warning(f"MQTT连接断开: {reason_string} (码 {reason_code_int})")
        self.update_connection_status_display(False, f"MQTT连接断开: {reason_string}")
        
        # 开始自动重连
        if not self._mqtt_reconnect_thread or not self._mqtt_reconnect_thread.is_alive():
            logging.info("启动MQTT重连线程")
            self._mqtt_reconnect_thread = threading.Thread(target=self._mqtt_reconnect, daemon=True)
            self._mqtt_reconnect_thread.start()

        logging.debug(f"MQTT断开: client={client}, userdata={userdata}, flags={flags}, rc(reason)={reason_string}")
        
        # 标记连接状态
        self._mqtt_connected = False
        
    def _mqtt_reconnect(self):
        """尝试自动重新连接MQTT服务器的方法，将在一个单独的线程中运行。"""
        max_attempts = 10  # 最大重试次数
        base_delay = 2  # 基础延迟秒数
        
        self._reconnect_attempts = 0
        
        while self._reconnect_attempts < max_attempts:
            self._reconnect_attempts += 1
            
            # 计算延迟时间，使用指数退避策略
            delay = min(base_delay * (2 ** (self._reconnect_attempts - 1)), 60)
            
            # 更新状态显示
            self.update_connection_status_display(
                False, 
                f"MQTT重连中... (尝试 {self._reconnect_attempts}/{max_attempts})"
            )
            
            logging.info(f"MQTT重连尝试 {self._reconnect_attempts}/{max_attempts}，延迟 {delay}秒")
            
            # 延迟一定时间后重试
            time.sleep(delay)
            
            # 尝试连接
            try:
                if hasattr(self, 'mqtt_client') and self.mqtt_client:
                    # 关闭现有连接
                    try:
                        self.mqtt_client.loop_stop()
                        self.mqtt_client.disconnect()
                    except:
                        pass
                    
                # 重新创建MQTT客户端并连接
                logging.info("重新连接MQTT服务器...")
                self.connect_mqtt()
                
                # 等待几秒检查是否连接成功
                time.sleep(3)
                
                # 通过连接状态变量检查是否成功
                if hasattr(self, '_mqtt_connected') and self._mqtt_connected:
                    logging.info("MQTT重连成功")
                    return True
            except Exception as e:
                logging.error(f"MQTT重连错误: {str(e)}")
        
        # 如果达到最大重试次数仍未成功
        logging.error(f"MQTT重连失败，达到最大尝试次数: {max_attempts}")
        self.update_connection_status_display(False, "MQTT连接失败，请检查网络或服务器")
        return False
        
        # if reason_code_int == 0:
        #     print("MQTT正常断开连接。")
        #     # self.update_connection_status_display(False, "MQTT已断开") # Or a more neutral message
        # else:
        #     print(f"MQTT意外断开连接，原因: {reason_string}")
        #     self.update_connection_status_display(False, f"MQTT断开: {reason_string}")
        
        # For any disconnect, update status unless it was an intentional shutdown
        # We might need a flag for intentional disconnect if self.on_closing handles it.
        # For now, assume any disconnect callback means connection is lost.
        self.update_connection_status_display(False, f"MQTT已断开 ({reason_string})")


    def on_message(self, client, userdata, msg):
        # global panel_configs # panel_configs is a global constant, can be accessed directly or via self if passed during init
        
        # 记录最后一次数据接收时间
        self.last_data_received_time = datetime.now()
        
        payload_str = ""
        try:
            # Try to decode as UTF-8. If it fails, it might be raw bytes for an image,
            # but for camera, we expect base64 encoded string, often within JSON.
            payload_str = msg.payload.decode('utf-8')
        except UnicodeDecodeError:
            # If it's the camera topic and decoding fails, it's problematic as we expect string data.
            # For other topics, it might be binary, but our current sensors send strings.
            logging.error(f"UnicodeDecodeError for topic {msg.topic}. Payload might not be UTF-8.")
            # If it's camera topic, we probably can't proceed with current logic.
            if msg.topic == self.MQTT_CAMERA_TOPIC:
                logging.error(f"Camera topic {msg.topic} received non-UTF-8 payload. Cannot process as base64 string.")
                return
            # For other topics, this would be an unexpected error.
            # For now, just return, or handle as appropriate if binary data is expected for some topics.
            return

        topic_str = msg.topic
        # 只记录有限的payload前缀以避免日志文件过大
        logging.debug(f"接收消息: Topic: {topic_str}, Payload前缀: {payload_str[:30]}...")

        # 打印完整的主题和数据用于调试
        print(f"DEBUG: 收到主题: {topic_str}, 数据: {payload_str}")

        # Simplified topic to key mapping based on panel_configs
        matched_key = None
        
        # 特殊处理UV风险等级主题
        if topic_str == "siot/uv风险等级":
            # 找到对应的UV风险等级面板键
            for key, config_data in self.panel_configs.items():
                if "base_topic_name" in config_data and config_data["base_topic_name"] == "紫外线指数":
                    matched_key = key
                    logging.info(f"接收到UV风险等级数据: {payload_str}")
                    break
        
        # 如果不是特殊处理的主题，则进行常规匹配
        if not matched_key:
            # Iterate through panel_configs to find which panel this topic belongs to
            for key, config_data in self.panel_configs.items():
                # Assuming sensor topics are generally prefixed with "siot/"
                # and their specific part is in "base_topic_name"
                if "base_topic_name" in config_data:
                    # 修复主题匹配逻辑
                    # 1. 精确匹配完整主题
                    expected_topic = "siot/" + config_data["base_topic_name"]
                    if topic_str == expected_topic:
                        matched_key = key # 'key' is like "temp", "humi", "aqi"
                        print(f"DEBUG: 精确匹配主题: {topic_str} -> {key}, 数据: {payload_str}")
                        break
                    # 2. 处理通配符情况（例如从 'siot/#' 订阅到的主题）
                    if topic_str.startswith("siot/"):
                        topic_part = topic_str.split("/", 1)[1]
                        # 精确匹配主题名
                        if config_data["base_topic_name"] == topic_part:
                            matched_key = key
                            print(f"DEBUG: 部分主题匹配: {topic_str} -> {key}, 数据: {payload_str}")
                            break
                        # 尝试模糊匹配（针对某些主题可能有前缀或后缀的情况）
                        if topic_part.find(config_data["base_topic_name"]) >= 0:
                            print(f"DEBUG: 模糊匹配主题: {topic_str} -> {key}, 数据: {payload_str}")
                            matched_key = key
                            break
        
        if topic_str == self.MQTT_WEATHER_TOPIC:
            print(f"DEBUG: Received message on WEATHER_TOPIC: {topic_str}")
            try:
                weather_data_json = json.loads(payload_str)
                self.root.after(0, self.update_weather_display, weather_data_json, None)
            except json.JSONDecodeError as e:
                print(f"ERROR: JSONDecodeError for weather data on topic {topic_str}: {e}. Payload: {payload_str}")
            except Exception as e:
                print(f"ERROR: Exception processing weather data for topic {topic_str}: {type(e).__name__} - {e}")
            return

        elif topic_str == self.MQTT_CAMERA_TOPIC:
            print(f"DEBUG: Received message on CAMERA_TOPIC: {topic_str}") # New log
            try:
                image_data_b64 = None
                
                # Try to parse JSON first, in case image is in a JSON payload
                try:
                    json_data = json.loads(payload_str)
                    # Look for base64 encoded image string in common JSON structures
                    for key in ['image', 'data', 'frame', 'image_data', 'image_data_b64', 'base64', 'imageBase64']:
                        if key in json_data and isinstance(json_data[key], str):
                            print(f"DEBUG: Extracted {key} from JSON payload for camera.")
                            image_data_b64 = json_data[key]
                            break
                except json.JSONDecodeError:
                    # If not JSON, assume the entire payload is base64 data
                    print("DEBUG: Camera payload is not JSON, treating as direct base64 data.")
                    image_data_b64 = payload_str
                
                if image_data_b64:
                    print(f"DEBUG: Queueing camera frame update. image_data_b64 (first 30): {image_data_b64[:30]}")
                    # Use after() to move image processing to the main thread - wrap in a dictionary
                    self.root.after(0, self.update_camera_stream, {"image": image_data_b64})
                    # Update frame statistics
                    self.video_frames_received += 1
                    self.last_video_frame_time = datetime.now()
                else:
                    print("DEBUG: No valid image data found in camera topic payload.")
            except Exception as e:
                print(f"ERROR: Exception in on_message for camera topic {topic_str} before queueing update_camera_stream: {type(e).__name__} - {e}")
            return # Explicit return after handling camera topic

        elif matched_key:
            if self.debug_mode:
                print(f"DEBUG: 匹配主题 {topic_str} 到面板键 {matched_key}, 数据: {payload_str}")
            
            try:
                data_value = payload_str
                data_processed = False
                
                # 尝试几种不同的数据格式解析
                # 1. 尝试解析JSON
                if payload_str.startswith('{') and payload_str.endswith('}'):
                    try:
                        json_data = json.loads(payload_str)
                        
                        # 支持几种常见的JSON格式
                        if 'value' in json_data:
                            data_value = json_data['value']
                            data_processed = True
                            print(f"DEBUG: 从JSON中提取'value'字段: {data_value}")
                        elif 'data' in json_data:
                            data_value = json_data['data']
                            data_processed = True
                            print(f"DEBUG: 从JSON中提取'data'字段: {data_value}")
                        else:
                            # 使用第一个找到的数值
                            for key, val in json_data.items():
                                if isinstance(val, (int, float, str)):
                                    data_value = val
                                    data_processed = True
                                    print(f"DEBUG: 从JSON中提取字段 {key}: {data_value}")
                                    break
                    except json.JSONDecodeError:
                        print(f"DEBUG: 数据不是有效JSON: {payload_str}")
                
                # 2. 尝试识别百分比值
                if not data_processed and '%' in payload_str:
                    try:
                        # 尝试提取百分比前面的数字
                        numeric_part = ''.join(c for c in payload_str.split('%')[0] if c.isdigit() or c == '.')
                        if numeric_part:
                            data_value = float(numeric_part)
                            data_processed = True
                            print(f"DEBUG: 提取百分比值: {data_value}")
                    except ValueError:
                        pass
                
                # 3. 尝试直接提取数值
                if not data_processed:
                    try:
                        # 尝试将整个字符串视为数值
                        data_value = float(payload_str)
                        data_processed = True
                        print(f"DEBUG: 直接转换为数值: {data_value}")
                    except ValueError:
                        try:
                            # 尝试提取所有数字字符作为数值
                            numeric_part = ''.join(c for c in payload_str if c.isdigit() or c == '.')
                            if numeric_part:
                                data_value = float(numeric_part)
                                data_processed = True
                                print(f"DEBUG: 提取数值部分: {data_value}")
                        except ValueError:
                            pass
                
                # 4. 如果经过以上处理仍无法提取有效数据，记录日志
                if not data_processed and self.debug_mode:
                    print(f"DEBUG: 无法处理数据: {payload_str}")

                self.root.after(0, self.update_sensor_data, matched_key, data_value)
            except Exception as e:
                print(f"ERROR: Exception processing sensor data for topic {topic_str}, key {matched_key}: {type(e).__name__} - {e}")
        else:
            # 改进未处理主题的日志记录，提供更详细的信息
            logging.warning(f"收到未处理主题消息: {topic_str}. 负载前缀: {payload_str[:50]}")
            print(f"Warning: Received message on unhandled topic: {topic_str}")
            
            # 尝试猜测最佳匹配的面板配置
            best_match = None
            best_score = 0
            
            for key, config_data in self.panel_configs.items():
                if "base_topic_name" in config_data:
                    topic_name = config_data["base_topic_name"]
                    # 简单的字符串相似性检查
                    common_chars = sum(c1 == c2 for c1, c2 in zip(topic_str, "siot/" + topic_name))
                    score = common_chars / max(len(topic_str), len("siot/" + topic_name))
                    if score > 0.5 and score > best_score:  # 相似度阈值
                        best_match = key
                        best_score = score
                            
            if best_match:
                logging.info(f"发现可能的匹配: 主题 {topic_str} 可能对应面板键 {best_match}")
                print(f"可能的匹配: 主题 {topic_str} → 面板 {best_match} ({self.panel_configs[best_match]['display_title']})")
                try:
                    # 尝试使用猜测的匹配更新数据
                    self.root.after(0, self.update_sensor_data, best_match, payload_str)
                    print(f"尝试以 {best_match} 处理未匹配主题的数据: {payload_str}")
                except Exception as e:
                    print(f"尝试处理未匹配主题时出错: {e}")

    def update_sensor_data(self, panel_key, data_value): # Renamed 'topic' to 'panel_key', 'data_str' to 'data_value'
        # 只在调试模式下输出详细日志
        if self.debug_mode:
            print(f"DEBUG: update_sensor_data调用，面板键: {panel_key}, 数据: {str(data_value)[:50]}")
        
        # 记录最后一次数据接收时间，用于状态监控
        self.last_data_received_time = datetime.now()
        
        # 如果启用了模拟模式，忽略真实传感器数据
        if self.use_simulation:
            if self.debug_mode:
                print("模拟模式已启用，忽略真实传感器数据。")
            return

        # 确保数据为字符串类型
        if not isinstance(data_value, str):
            data_value = str(data_value)
            
        # 尝试清理数据，处理可能的JSON或其他格式
        cleaned_data = data_value
        try:
            # 检查数据是否可能是JSON格式
            if data_value.startswith('{') and data_value.endswith('}'):
                json_data = json.loads(data_value)
                if 'value' in json_data:
                    cleaned_data = str(json_data['value'])
                elif 'data' in json_data:
                    cleaned_data = str(json_data['data'])
                else:
                    # 使用第一个找到的数值
                    for key, value in json_data.items():
                        if isinstance(value, (int, float)):
                            cleaned_data = str(value)
                            break
            # 尝试直接转换为浮点数，移除非数字字符
            else:
                try:
                    # 移除所有非数字、非小数点的字符
                    numeric_part = ''.join(c for c in data_value if c.isdigit() or c == '.')
                    if numeric_part:
                        float(numeric_part)  # 验证是否为有效数字
                        cleaned_data = numeric_part
                except ValueError:
                    pass
        except Exception as e:
            print(f"警告: 处理数据值时出错: {e}")

        # 更新UI显示和数据存储
        if panel_key and panel_key in self.data_vars:
            # 确保数据值是字符串格式，适合StringVar显示
            self.data_vars[panel_key].set(str(cleaned_data))
            
            # 添加单位显示和处理特殊面板
            display_value = cleaned_data
            if panel_key in self.panel_configs:
                display_name = self.panel_configs[panel_key]['display_title']
                unit = self.panel_configs[panel_key].get('unit', '')
                logging.info(f"传感器更新: {display_name} = {display_value}{unit}")
                
                # 更新窗口标题，反映最新数据状态
                if panel_key == "temp":                    
                    self.root.title(f"{APP_TITLE} - 温度: {display_value}{unit}")
                
                # 更新AQI仪表盘
                if panel_key == "aqi" and hasattr(self, 'aqi_value_label'):
                    try:
                        aqi_value = float(cleaned_data)
                        self.aqi_value_label.config(text=str(cleaned_data))
                        
                        # 根据AQI值确定等级和颜色
                        if aqi_value <= 50:
                            level = "优"
                            color = "#4CAF50"  # 绿色
                            bg_color = "#E8F5E9"  # 浅绿色背景
                            desc = "空气质量令人满意，基本无污染"
                        elif aqi_value <= 100:
                            level = "良"
                            color = "#FFEB3B"  # 黄色
                            bg_color = "#FFF9C4"  # 浅黄色背景
                            desc = "空气质量可接受，敏感人群应减少户外活动"
                        elif aqi_value <= 150:
                            level = "轻度污染"
                            color = "#FF9800"  # 橙色
                            bg_color = "#FFE0B2"  # 浅橙色背景
                            desc = "轻度污染，儿童等敏感人群应减少户外活动"
                        elif aqi_value <= 200:
                            level = "中度污染"
                            color = "#F44336"  # 红色
                            bg_color = "#FFCDD2"  # 浅红色背景
                            desc = "中度污染，应减少户外活动"
                        elif aqi_value <= 300:
                            level = "重度污染"
                            color = "#9C27B0"  # 紫色
                            bg_color = "#E1BEE7"  # 浅紫色背景
                            desc = "重度污染，应避免户外活动"
                        else:
                            level = "严重污染"
                            color = "#880E4F"  # 深紫色
                            bg_color = "#FCE4EC"  # 浅粉色背景
                            desc = "严重污染，应停止户外活动"
                            
                        # 更新文本和颜色
                        self.aqi_level_label.config(text=level, fg=color)
                        self.aqi_value_label.config(fg=color)
                        
                        # 绘制高级圆形指示器
                        if hasattr(self, 'aqi_indicator_canvas') and self.aqi_indicator_canvas:
                            self.aqi_indicator_canvas.delete("all")  # 清除旧图形
                            
                            # 绘制渐变边缘效果的圆
                            diameter = 40
                            x0, y0 = 5, 5
                            x1, y1 = x0 + diameter, y0 + diameter
                            
                            # 绘制外圈光晕效果
                            glow_width = 3
                            self.aqi_indicator_canvas.create_oval(
                                x0-glow_width, y0-glow_width, 
                                x1+glow_width, y1+glow_width, 
                                fill="", outline=color, width=glow_width
                            )
                            
                            # 绘制主圆
                            self.aqi_indicator_canvas.create_oval(
                                x0, y0, x1, y1, 
                                fill=color, outline=""
                            )
                            
                            # 添加等级文本，使用首字母
                            self.aqi_indicator_canvas.create_text(
                                x0 + diameter/2, y0 + diameter/2, 
                                text=level[0], 
                                fill="white", 
                                font=("Helvetica", 16, "bold")
                            )
                        
                        # 更新AQI描述标签
                        if hasattr(self, 'aqi_desc_label') and self.aqi_desc_label:
                            self.aqi_desc_label.config(text=desc)
                    except ValueError:
                        print(f"警告: AQI值 '{cleaned_data}' 无法转换为数字")
                        pass
                
                # 更新UV风险等级仪表盘
                if panel_key == "uv" and hasattr(self, 'uv_value_label'):
                    # 先尝试显示数值
                    try:
                        uv_value = float(cleaned_data)
                        self.uv_value_label.config(text=str(cleaned_data))
                        
                        # 根据UV值确定等级和颜色
                        if uv_value <= 2:
                            level = "低"
                            color = "#4CAF50"  # 绿色
                            bg_color = "#E8F5E9"  # 浅绿色背景
                            desc = "安全，可以户外活动"
                        elif uv_value <= 5:
                            level = "中"
                            color = "#FFEB3B"  # 黄色
                            bg_color = "#FFF9C4"  # 浅黄色背景
                            desc = "需要防晒，建议戴帽子、涂抹防晒霜"
                        elif uv_value <= 7:
                            level = "高"
                            color = "#FF9800"  # 橙色
                            bg_color = "#FFE0B2"  # 浅橙色背景
                            desc = "需要防晒措施，中午时段应避免户外活动"
                        elif uv_value <= 10:
                            level = "很高"
                            color = "#F44336"  # 红色
                            bg_color = "#FFCDD2"  # 浅红色背景
                            desc = "尽量避免户外活动，做好全面防护措施"
                        else:
                            level = "极高"
                            color = "#9C27B0"  # 紫色
                            bg_color = "#E1BEE7"  # 浅紫色背景
                            desc = "禁止户外活动，有皮肤损伤风险"
                            
                        self.uv_level_label.config(text=level, fg=color)
                        self.uv_value_label.config(fg=color)
                        
                        # 绘制进度条样式的指示器，增加视觉效果
                        if hasattr(self, 'uv_indicator_canvas') and self.uv_indicator_canvas:
                            self.uv_indicator_canvas.delete("all")  # 清除旧图形
                            total_width = self.uv_indicator_canvas.winfo_width() or 150  # 默认宽度150
                            
                            # UV指数最高为11，计算进度
                            progress = min(uv_value / 11.0, 1.0)
                            indicator_width = int(total_width * progress)
                            
                            # 绘制背景条 - 更美观的圆角矩形
                            bg_radius = 5  # 背景圆角半径
                            self.uv_indicator_canvas.create_rectangle(
                                0, 0, total_width, 20,
                                fill="#E0E0E0", outline="",
                                width=0, radius=bg_radius
                            )
                            
                            # 绘制渐变进度条 - 从左到右颜色渐变
                            if indicator_width > 0:
                                # 在进度条区域创建圆角矩形
                                progress_radius = 5  # 进度条圆角半径
                                self.uv_indicator_canvas.create_rectangle(
                                    0, 0, indicator_width, 20,
                                    fill=color, outline="",
                                    width=0, radius=progress_radius
                                )
                                
                                # 添加高光效果
                                highlight_height = 6
                                self.uv_indicator_canvas.create_rectangle(
                                    2, 2, indicator_width-2, highlight_height,
                                    fill="#FFFFFF", outline="",
                                    width=0, radius=2,
                                    stipple="gray25"  # 半透明效果
                                )
                            
                            # 添加刻度标记和标签
                            for i in range(6):
                                x_pos = int(total_width * i / 5)
                                # 刻度线
                                self.uv_indicator_canvas.create_line(
                                    x_pos, 20, x_pos, 25, 
                                    fill="#757575", width=1
                                )
                                # 刻度标签
                                self.uv_indicator_canvas.create_text(
                                    x_pos, 30, 
                                    text=str(i*2), 
                                    fill="#757575", 
                                    font=("Helvetica", 8)
                                )
                            
                            # 添加当前值标记
                            current_x = int(total_width * progress)
                            if current_x > 5 and current_x < total_width-5:  # 确保不会太靠边
                                # 在进度条上方显示小三角形指示当前位置
                                self.uv_indicator_canvas.create_polygon(
                                    current_x-5, 0,
                                    current_x+5, 0,
                                    current_x, -8,
                                    fill=color, outline="", 
                                    width=0
                                )
                        
                        # 更新UV描述标签
                        if hasattr(self, 'uv_desc_label') and self.uv_desc_label:
                            self.uv_desc_label.config(text=desc)
                            
                    except ValueError:
                        # 如果是文本（如"中"），直接显示
                        if cleaned_data in ["低", "中", "高", "很高", "极高"]:
                            level = cleaned_data
                            self.uv_value_label.config(text=level)
                            
                            # 设置颜色和描述
                            if level == "低":
                                color = "#4CAF50"  # 绿色
                                desc = "安全，可以户外活动"
                                uv_value = 1  # 为进度条设置大致数值
                            elif level == "中":
                                color = "#FFEB3B"  # 黄色
                                desc = "需要防晒，建议戴帽子、涂抹防晒霜"
                                uv_value = 4  # 为进度条设置大致数值
                            elif level == "高":
                                color = "#FF9800"  # 橙色
                                desc = "需要防晒措施，中午时段应避免户外活动"
                                uv_value = 6  # 为进度条设置大致数值
                            elif level == "很高":
                                color = "#F44336"  # 红色
                                desc = "尽量避免户外活动，做好全面防护措施"
                                uv_value = 9  # 为进度条设置大致数值
                            else:  # 极高
                                color = "#9C27B0"  # 紫色
                                desc = "禁止户外活动，有皮肤损伤风险"
                                uv_value = 11  # 为进度条设置大致数值
                                
                            self.uv_level_label.config(text=level, fg=color)
                            self.uv_value_label.config(fg=color)
                            
                            # 更新UV描述标签和进度条
                            if hasattr(self, 'uv_desc_label') and self.uv_desc_label:
                                self.uv_desc_label.config(text=desc)
                                
                            # 绘制进度条，基于文本级别设置进度值
                            if hasattr(self, 'uv_indicator_canvas') and self.uv_indicator_canvas:
                                self.uv_indicator_canvas.delete("all")
                                total_width = self.uv_indicator_canvas.winfo_width() or 150
                                progress = min(uv_value / 11.0, 1.0)
                                indicator_width = int(total_width * progress)
                                
                                # 与数值情况相同的进度条绘制代码
                                bg_radius = 5
                                self.uv_indicator_canvas.create_rectangle(
                                    0, 0, total_width, 20,
                                    fill="#E0E0E0", outline="",
                                    width=0, radius=bg_radius
                                )
                                
                                if indicator_width > 0:
                                    progress_radius = 5
                                    self.uv_indicator_canvas.create_rectangle(
                                        0, 0, indicator_width, 20,
                                        fill=color, outline="",
                                        width=0, radius=progress_radius
                                    )
                                    
                                    highlight_height = 6
                                    self.uv_indicator_canvas.create_rectangle(
                                        2, 2, indicator_width-2, highlight_height,
                                        fill="#FFFFFF", outline="",
                                        width=0, radius=2,
                                        stipple="gray25"
                                    )
                                
                                for i in range(6):
                                    x_pos = int(total_width * i / 5)
                                    self.uv_indicator_canvas.create_line(
                                        x_pos, 20, x_pos, 25, 
                                        fill="#757575", width=1
                                    )
                                    self.uv_indicator_canvas.create_text(
                                        x_pos, 30, 
                                        text=str(i*2), 
                                        fill="#757575", 
                                        font=("Helvetica", 8)
                                    )
                                
                                current_x = int(total_width * progress)
                                if current_x > 5 and current_x < total_width-5:
                                    self.uv_indicator_canvas.create_polygon(
                                        current_x-5, 0,
                                        current_x+5, 0,
                                        current_x, -8,
                                        fill=color, outline="",
                                        width=0
                                    )
                        
    def toggle_simulation(self):
        """切换是否使用模拟数据"""
        print("DEBUG: toggle_simulation 方法被调用")
        
        # 使用实例变量而非全局变量
        self.use_simulation = not self.use_simulation
        
        if self.use_simulation:
            print("DEBUG: 启用模拟数据模式")
            self.sim_button_text_var.set("关闭模拟数据")
            # 更新状态显示
            logging.info("已启用模拟数据模式")
            if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                self.connection_status_label_widget.config(text="状态: 使用模拟数据", fg=TEXT_COLOR_STATUS_SIM)
            
            # 更新所有传感器数据
            for topic_key, value in simulation_data.items():
                print(f"DEBUG: 正在模拟数据 - {topic_key}: {value}")
                full_topic = f"siot/{topic_key}"
                # 模拟消息格式
                message = mqtt.MQTTMessage()
                message.topic = full_topic.encode('utf-8')
                message.payload = value.encode('utf-8')
                # 直接调用消息处理函数
                self.on_message(None, None, message)
                
            # 定期刷新模拟数据
            self.root.after(5000, self.refresh_simulation_data)
        else:
            print("DEBUG: 关闭模拟数据模式")
            self.sim_button_text_var.set("启用模拟数据")
            logging.info("已关闭模拟数据模式")
            # 尝试重新连接MQTT
            self.connect_mqtt()
    
    def refresh_simulation_data(self):
        """刷新模拟数据，使其数值稍有变化"""
        print("DEBUG: refresh_simulation_data 方法被调用")
        
        # 使用实例变量而非全局变量
        if not hasattr(self, 'use_simulation') or not self.use_simulation:
            print("DEBUG: 模拟数据模式已关闭，不再刷新")
            return  # 如果已关闭模拟模式，则不再刷新
        
        print("DEBUG: 正在刷新模拟数据...")
        # 为一些数据增加一点随机变化
        updated_data = {}
        for key, value in simulation_data.items():
            try:
                # 尝试转换为浮点数并添加少量随机波动
                num_value = float(value)
                # 根据不同类型的数据设置不同的波动范围
                if key == "环境温度":
                    fluctuation = random.uniform(-0.3, 0.3)
                elif key == "环境湿度":
                    fluctuation = random.uniform(-1.0, 1.0)
                elif key == "aqi":
                    fluctuation = random.uniform(-2.0, 2.0)
                elif key == "噪音":
                    fluctuation = random.uniform(-1.5, 1.5)
                else:
                    fluctuation = random.uniform(-0.5, 0.5)
                
                # 更新值并转回字符串
                new_value = num_value + fluctuation
                updated_data[key] = f"{new_value:.1f}"
                print(f"DEBUG: 模拟数据更新 - {key}: {value} -> {updated_data[key]}")
            except ValueError:
                # 如果不是数值，保持原样
                updated_data[key] = value
                print(f"DEBUG: 保持原样的非数值数据 - {key}: {value}")
        
        # 使用更新的数据
        for topic_key, value in updated_data.items():
            full_topic = f"siot/{topic_key}"
            # 模拟消息格式
            message = mqtt.MQTTMessage()
            message.topic = full_topic.encode('utf-8')
            message.payload = value.encode('utf-8')
            # 直接调用消息处理函数
            self.on_message(None, None, message)
        
        # 继续定期刷新
        self.root.after(5000, self.refresh_simulation_data)

# 清除所有现有内容，以确保代码没有重复
# 添加主程序入口点
if __name__ == "__main__":
    print("DEBUG: __main__ 块已启动")
    
    # 尝试设置中文地区设置
    original_locale_time = locale.getlocale(locale.LC_TIME)
    try:
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
        print("DEBUG: 成功设置中文区域设置 zh_CN.UTF-8")
    except locale.Error:
        print("警告: 无法设置中文区域设置 (zh_CN.UTF-8)。尝试其他中文区域设置...")
        try:
            locale.setlocale(locale.LC_TIME, 'Chinese_China.936') # Windows特定设置
            print("DEBUG: 成功设置中文区域设置 Chinese_China.936")
        except locale.Error:
            print("警告: 无法设置 'Chinese_China.936'。星期几可能以默认语言显示。")
            # 如果设置失败，恢复到原始设置
            locale.setlocale(locale.LC_TIME, original_locale_time)

    try:
        print("DEBUG: 创建Tkinter根窗口...")
        root = tk.Tk()
        print("DEBUG: Tkinter根窗口创建成功")
        root.geometry("1280x768") # 设置默认大小
        root.configure(bg=PAGE_BG_COLOR)
        
        print("DEBUG: 初始化SmartCampusDashboard实例...")
        app = SmartCampusDashboard(root) # 创建应用实例，处理包括MQTT在内的所有设置
        
        print("DEBUG: 启动Tkinter主循环...")
        root.mainloop()
        print("DEBUG: Tkinter主循环已结束。")
    except Exception as e:
        import traceback
        print(f"ERROR: 应用程序运行时出错: {e}")
        traceback.print_exc()
        logging.error(f"应用程序启动失败: {e}", exc_info=True)
    
    # 恢复区域设置（如果更改了）
    try:
        locale.setlocale(locale.LC_TIME, original_locale_time)
    except Exception:
        pass # 忽略最终清理期间的错误
