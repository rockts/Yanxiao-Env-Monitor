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
import os
import json
import logging
import random
import time
import requests # For weather API
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk # Added ttk import
# 添加日志功能
import base64
import io
import threading
from datetime import datetime, timedelta
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import dates as mdates
import subprocess
import sys

try:
    from PIL import Image, ImageTk, UnidentifiedImageError
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告：Pillow库未安装或导入失败，视频/图像显示功能将不可用。请运行 'pip install Pillow' 进行安装。")

# --- Matplotlib Imports ---
try:
    import matplotlib.pyplot as plt # Added import for plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Corrected indentation
    MATPLOTLIB_AVAILABLE = True
    plt.style.use('dark_background') # Apply dark theme to matplotlib charts
    # 解决中文显示问题
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

# --- Color Constants for UI ---
TEXT_COLOR_DEFAULT = "#FFFFFF" # Default text color (assuming dark theme)
TEXT_COLOR_STATUS_CONNECTED = "#4CAF50"  # Green for connected
TEXT_COLOR_STATUS_ERROR = "#F44336"      # Red for errors/disconnected
TEXT_COLOR_STATUS_WARNING = "#FFC107"    # Amber/Yellow for warnings/connecting
TEXT_COLOR_STATUS_SIM = "#03A9F4"        # Blue for simulation mode
TEXT_COLOR_INFO = "#2196F3"          # Blue for general info
LABEL_TEXT_COLOR = "#E0E0E0"         # Light gray for labels
VALUE_TEXT_COLOR = "#FFFFFF"         # White for values
SECTION_TITLE_COLOR = "#4FC3F7"      # Light blue for section titles
ACCENT_COLOR = "#4CAF50"  # Added from simple_working_dashboard.py for gauges

# --- MQTT Configuration ---
# 尝试加载配置文件
try:
    # Correct base_dir for config (should be project root of dashboard)
    # __file__ is .../dashboard/src/core/app.py
    # script_dir is .../dashboard/src/core
    # src_dir is .../dashboard/src
    # dashboard_dir is .../dashboard/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    dashboard_dir = os.path.dirname(src_dir)
    config_file = os.path.join(dashboard_dir, "config", "config.json")
    print(f"DEBUG: Attempting to load config from: {config_file}") # DEBUG PRINT

    MQTT_BROKER_HOST_DEFAULT = "192.168.1.129"
    MQTT_BROKER_PORT_DEFAULT = 1883
    MQTT_CLIENT_ID_DEFAULT = "smart_campus_dashboard_client_default"
    MQTT_CAMERA_TOPIC_DEFAULT = "sc/camera/stream/default"
    MQTT_WEATHER_TOPIC_DEFAULT = "sc/weather/data/default"
    SIOT_SERVER_HTTP_DEFAULT = "http://192.168.1.129:8080"
    SIOT_USERNAME_DEFAULT = "siot_default"
    SIOT_PASSWORD_DEFAULT = "dfrobot_default"

    if os.path.exists(config_file):
        print(f"DEBUG: Config file found at: {config_file}") # DEBUG PRINT
        with open(config_file, 'r', encoding='utf-8') as f: # Added encoding
            config = json.load(f)
            print(f"DEBUG: Config loaded: {config}") # DEBUG PRINT
            
            mqtt_config = config.get("mqtt", {})
            SIOT_SERVER_HTTP = config.get("siot_server_http", SIOT_SERVER_HTTP_DEFAULT) # Assuming siot_server_http is top-level or adjust as needed
            SIOT_USERNAME = config.get("siot_username", SIOT_USERNAME_DEFAULT) # Assuming siot_username is top-level or adjust as needed
            SIOT_PASSWORD = config.get("siot_password", SIOT_PASSWORD_DEFAULT) # Assuming siot_password is top-level or adjust as needed

            MQTT_BROKER_HOST = mqtt_config.get("broker_host", MQTT_BROKER_HOST_DEFAULT)
            print(f"DEBUG: MQTT_BROKER_HOST from mqtt_config.get: {MQTT_BROKER_HOST}") # DEBUG PRINT
            MQTT_BROKER_PORT = mqtt_config.get("broker_port", MQTT_BROKER_PORT_DEFAULT)
            MQTT_CLIENT_ID = mqtt_config.get("client_id", MQTT_CLIENT_ID_DEFAULT)
            
            # Assuming camera_topic and weather_topic might be elsewhere or need defaults
            # For now, let's assume they might be under a general 'topics' key or similar if not under 'mqtt'
            # If they are meant to be top-level in config.json, adjust accordingly.
            MQTT_CAMERA_TOPIC = config.get("mqtt_camera_topic", "siot/摄像头")
            MQTT_WEATHER_TOPIC = config.get("mqtt_weather_topic", MQTT_WEATHER_TOPIC_DEFAULT)

            logging.info(f"成功加载配置文件: {config_file}")
            print(f"INFO: Successfully loaded config file: {config_file}") # DEBUG PRINT
            print(f"INFO: MQTT_BROKER_HOST set to: {MQTT_BROKER_HOST}") # DEBUG PRINT
            print(f"INFO: MQTT_BROKER_PORT set to: {MQTT_BROKER_PORT}") # DEBUG PRINT
            print(f"INFO: MQTT_CLIENT_ID set to: {MQTT_CLIENT_ID}") # DEBUG PRINT
    else:
        logging.warning(f"配置文件不存在: {config_file}，使用默认配置")
        print(f"WARNING: Config file NOT FOUND: {config_file}. Using default MQTT settings.") # DEBUG PRINT
        SIOT_SERVER_HTTP = SIOT_SERVER_HTTP_DEFAULT
        SIOT_USERNAME = SIOT_USERNAME_DEFAULT
        SIOT_PASSWORD = SIOT_PASSWORD_DEFAULT
        MQTT_BROKER_HOST = MQTT_BROKER_HOST_DEFAULT
        MQTT_BROKER_PORT = MQTT_BROKER_PORT_DEFAULT
        MQTT_CLIENT_ID = MQTT_CLIENT_ID_DEFAULT
        MQTT_CAMERA_TOPIC = "siot/摄像头"
        MQTT_WEATHER_TOPIC = MQTT_WEATHER_TOPIC_DEFAULT
        print(f"INFO: MQTT_BROKER_HOST set to default: {MQTT_BROKER_HOST}") # DEBUG PRINT
except Exception as e:
    logging.error(f"加载配置文件时出错: {e}，使用默认配置")
    print(f"ERROR: Exception during config load: {e}. Using default MQTT settings.") # DEBUG PRINT
    SIOT_SERVER_HTTP = SIOT_SERVER_HTTP_DEFAULT
    SIOT_USERNAME = SIOT_USERNAME_DEFAULT
    SIOT_PASSWORD = SIOT_PASSWORD_DEFAULT
    MQTT_BROKER_HOST = MQTT_BROKER_HOST_DEFAULT
    MQTT_BROKER_PORT = MQTT_BROKER_PORT_DEFAULT
    MQTT_CLIENT_ID = MQTT_CLIENT_ID_DEFAULT
    MQTT_CAMERA_TOPIC = "siot/摄像头"
    MQTT_WEATHER_TOPIC = MQTT_WEATHER_TOPIC_DEFAULT
    print(f"INFO: MQTT_BROKER_HOST set to default after exception: {MQTT_BROKER_HOST}") # DEBUG PRINT
MQTT_TOPICS = [
    "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
    "siot/紫外线指数", "siot/uv风险等级", "siot/噪音", "siot/摄像头", MQTT_WEATHER_TOPIC
]
mqtt_data_cache = {topic: "--" for topic in MQTT_TOPICS} # 初始化缓存
mqtt_data_cache[MQTT_CAMERA_TOPIC] = None # Initialize camera data as None
# 使用指定的API版本来初始化客户端，以消除弃用警告
print("DEBUG: Before mqtt.Client instantiation") # DEBUG PRINT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
print("DEBUG: After mqtt.Client instantiation") # DEBUG PRINT

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
FONT_PANEL_VALUE = ("Helvetica",25, "bold")
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
print("DEBUG: Global definitions complete, before class SmartCampusDashboard") # DEBUG PRINT

class SmartCampusDashboard:
    def __init__(self, root):
        self.root = root # 将传入的root参数赋值给实例变量self.root
        self.debug_mode = True # 初始化 debug_mode 属性

        # 确保在 __init__ 方法的早期（尤其是在调用 self.connect_mqtt() 之前）
        # 初始化 mqtt_config, MQTT_BROKER_HOST, 和 MQTT_BROKER_PORT 实例变量。
        # mqtt_config 应该是从JSON文件加载的全局配置字典。
        self.mqtt_config = mqtt_config
        self.MQTT_BROKER_HOST = self.mqtt_config.get('broker_host')
        self.MQTT_BROKER_PORT = self.mqtt_config.get('broker_port')

        # MQTT客户端初始化移到这里
        client_id = self.mqtt_config.get('client_id', f"dashboard_client_{random.randint(0, 10000)}")
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

        if hasattr(self, 'debug_mode') and self.debug_mode: # Check if debug_mode is set
            print("DEBUG: SmartCampusDashboard __init__ - ENTER")
        else:
            # Fallback or ensure debug_mode is initialized if this message is critical
            print("DEBUG: SmartCampusDashboard __init__ - ENTER (debug_mode might not be initialized yet)")
        
        # Initialize MQTT connection state attributes
        self._mqtt_connected = False
        self._reconnect_attempts = 0
        self._mqtt_reconnect_thread = None

        # Initialize StringVars for UI elements that need dynamic text
        self.time_var = tk.StringVar()
        self.time_var.set("正在加载时间...")

        self.connection_status_var = tk.StringVar() # For connection status text
        self.connection_status_var.set("状态: 未连接") # Initial status

        self.sim_button_text_var = tk.StringVar()
        self.sim_button_text_var.set("启用模拟数据")

        # Initialize data_vars for sensor readings
        self.data_vars = {} # Will store StringVars for each sensor panel

        # Initialize last data received time
        self.last_data_received_time = None
        self.last_video_frame_time = None
        self.video_frames_received = 0

        # Initialize chart data history
        self.chart_data_history = {
            "temp": deque(maxlen=CHART_HISTORY_MAXLEN),
            "humi": deque(maxlen=CHART_HISTORY_MAXLEN),
            "noise": deque(maxlen=CHART_HISTORY_MAXLEN)
        }
        self.last_chart_update = time.time() # Initialize last chart update time

        # Gauge canvases - initialized to None
        self.gauge_aqi_canvas = None
        # self.gauge_eco2_canvas = None # Renamed
        self.gauge_uv_risk_canvas = None # Added for clarity

        # Chart figures, axes, and canvas widgets - initialized to None
        self.fig_temp_chart = None
        self.ax_temp_chart = None
        self.chart_canvas_widget_temp = None
        self.fig_humi_chart = None
        self.ax_humi_chart = None
        self.chart_canvas_widget_humi = None
        self.fig_noise_chart = None
        self.ax_noise_chart = None
        self.chart_canvas_widget_noise = None


        # Initialize panel_configs (moved from global to instance variable)
        self.panel_configs = {
            "temp": {"display_title": "环境温度", "unit": "°C", "icon": "🌡️", "base_topic_name": "siot/环境温度", "data_type": "numeric", "chartable": True},
            "humi": {"display_title": "环境湿度", "unit": "%RH", "icon": "💧", "base_topic_name": "siot/环境湿度", "data_type": "numeric", "chartable": True},
            "aqi": {"display_title": "空气质量指数", "unit": "级", "icon": "💨", "base_topic_name": "siot/aqi", "data_type": "numeric_level", "gauge_max": 5, "gauge": True, "levels": ["非常好", "好", "一般", "差", "极差"]},
            "tvoc": {"display_title": "TVOC", "unit": "ppb", "icon": "🌿", "base_topic_name": "siot/tvoc", "data_type": "numeric"},
            "eco2": {"display_title": "eCO2", "unit": "ppm", "icon": "☁️", "base_topic_name": "siot/eco2", "data_type": "numeric", "gauge_max": 2000, "gauge": False},
            "uv_index": {"display_title": "紫外线指数", "unit": "", "icon": "☀️", "base_topic_name": "siot/紫外线指数", "data_type": "numeric"},
            "uv_risk": {"display_title": "UV风险等级", "unit": "级", "icon": "⚠️", "base_topic_name": "siot/uv风险等级", "data_type": "string_level", "gauge_max": 4, "gauge": True, "levels": ["低", "中", "高", "很高", "极高"]},
            "noise": {"display_title": "噪音水平", "unit": "dB", "icon": "🔊", "base_topic_name": "siot/噪音", "data_type": "numeric", "chartable": True},
            "weather": {"display_title": "天气状况", "unit": "", "icon": "🌦️", "base_topic_name": "weather/data", "data_type": "weather_info"},
        }
        # Populate self.data_vars based on panel_configs
        for key, config in self.panel_configs.items():
            self.data_vars[key] = tk.StringVar(value="--")
        
        self.video_photo_image = None # To store the PhotoImage object for the video frame

        # Initialize use_simulation 实例变量
        self.use_simulation = False # 默认不使用模拟数据

        # --- UI Style Configuration ---
        self.style = ttk.Style()
        # Define styles for connection status label
        self.style.configure("Status.TLabel", padding=2, font=FONT_STATUS, background=PAGE_BG_COLOR) # Base style
        self.style.configure("Status.Connected.TLabel", foreground=TEXT_COLOR_STATUS_CONNECTED, font=FONT_STATUS, background=PAGE_BG_COLOR)
        self.style.configure("Status.Error.TLabel", foreground=TEXT_COLOR_STATUS_ERROR, font=FONT_STATUS, background=PAGE_BG_COLOR)
        self.style.configure("Status.Warning.TLabel", foreground=TEXT_COLOR_STATUS_WARNING, font=FONT_STATUS, background=PAGE_BG_COLOR)
        self.style.configure("Status.Sim.TLabel", foreground=TEXT_COLOR_STATUS_SIM, font=FONT_STATUS, background=PAGE_BG_COLOR)
        self.style.configure("Status.Default.TLabel", foreground=TEXT_COLOR_DEFAULT, font=FONT_STATUS, background=PAGE_BG_COLOR)


        self.setup_ui() 
        # Ensure gauges are drawn initially after UI setup and canvas creation
        self.root.after(250, self.initial_gauge_draw) # Increased delay slightly

        self.connect_mqtt()
        self.start_weather_updates()
        self.start_time_updates()
        self.start_system_status_check()
        
        print("DEBUG: SmartCampusDashboard __init__ - EXIT") # ADDED

    def update_connection_status_display(self, connected, status_text=None):
        """更新MQTT连接状态显示"""
        try:
            self._mqtt_connected = connected
            current_style = "Status.Default.TLabel"
            
            if connected:
                status_msg = "状态: 已连接到MQTT服务器"
                current_style = "Status.Connected.TLabel"
                logging.info(status_msg)
            else:
                if status_text:
                    status_msg = status_text
                else:
                    status_msg = "状态: 连接已断开" # Default disconnected message
                current_style = "Status.Error.TLabel"
                logging.warning(status_msg)
            
            # Schedule the UI update to run in the main thread
            def _update():
                if hasattr(self, 'connection_status_var'):
                    self.connection_status_var.set(status_msg)
                
                if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                    # The text is already handled by textvariable, so just configure style
                    self.connection_status_label_widget.configure(style=current_style)
            
            if self.root: # Ensure root window exists
                 self.root.after(0, _update)

        except Exception as e:
            logging.error(f"更新连接状态显示时出错: {e}")

    def setup_ui(self):
        print("DEBUG: SmartCampusDashboard setup_ui - ENTER")
        self.root.title(APP_TITLE)
        self.root.geometry("1440x900")  # Increased size for three columns
        self.root.configure(bg=PAGE_BG_COLOR)

        # --- Main Application Frame ---
        app_frame = ttk.Frame(self.root, style='App.TFrame')
        app_frame.pack(expand=True, fill=tk.BOTH)
        self.style.configure('App.TFrame', background=PAGE_BG_COLOR)

        # --- Top Bar (Title, Time, Status) ---
        top_bar_frame = ttk.Frame(app_frame, style='TopBar.TFrame', padding=(10,5))
        top_bar_frame.pack(fill=tk.X)
        self.style.configure('TopBar.TFrame', background=PAGE_BG_COLOR) # Darker background for top bar

        # Configure columns for centering title
        top_bar_frame.columnconfigure(0, weight=1) # Left spacer
        top_bar_frame.columnconfigure(1, weight=0) # Title (no extra space)
        top_bar_frame.columnconfigure(2, weight=1) # Right spacer (contains time and status)

        title_label = ttk.Label(top_bar_frame, text=APP_TITLE, font=FONT_APP_TITLE, style='Title.TLabel')
        title_label.grid(row=0, column=1, sticky="ew") # Place in middle column
        self.style.configure('Title.TLabel', background=PAGE_BG_COLOR, foreground=TEXT_COLOR_HEADER)

        # Frame for time and status on the right
        time_status_frame = ttk.Frame(top_bar_frame, style='TopBar.TFrame')
        time_status_frame.grid(row=0, column=2, sticky="e") # Align to the east (right)

        self.connection_status_label_widget = ttk.Label(time_status_frame, textvariable=self.connection_status_var, style="Status.Default.TLabel")
        self.connection_status_label_widget.pack(side=tk.RIGHT, padx=(0,10), pady=5) # Add some padding to the right of status
        
        time_label = ttk.Label(time_status_frame, textvariable=self.time_var, font=FONT_TIMESTAMP, style='Time.TLabel')
        time_label.pack(side=tk.RIGHT, padx=10, pady=5)
        self.style.configure('Time.TLabel', background=PAGE_BG_COLOR, foreground=TEXT_COLOR_HEADER)
        self.update_connection_status_display(self._mqtt_connected)

        # --- Main Content Area (Three Columns) ---
        content_area_frame = ttk.Frame(app_frame, style='ContentArea.TFrame', padding=10)
        content_area_frame.pack(expand=True, fill=tk.BOTH)
        self.style.configure('ContentArea.TFrame', background=PAGE_BG_COLOR)

        # Configure columns to have a 3:4:3 ratio for resizing (Left:Middle:Right)
        content_area_frame.columnconfigure(0, weight=3) # Left column
        content_area_frame.columnconfigure(1, weight=4) # Middle column
        content_area_frame.columnconfigure(2, weight=3) # Right column
        content_area_frame.rowconfigure(0, weight=1)    # Allow row to expand

        # --- Left Column: Sensor Data Panels ---
        left_column_frame = ttk.Frame(content_area_frame, style='Column.TFrame', padding=5)
        left_column_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        self.style.configure('Column.TFrame', background=PANEL_BG_COLOR) # Slightly lighter for column background

        # --- Middle Column: Video, Gauges, AI ---
        middle_column_frame = ttk.Frame(content_area_frame, style='Column.TFrame', padding=5)
        middle_column_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # --- Right Column: Charts ---
        right_column_frame = ttk.Frame(content_area_frame, style='Column.TFrame', padding=5)
        right_column_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0))

        # Populate Left Column (Sensor Panels)
        self.populate_left_column(left_column_frame)

        # Populate Middle Column (Video, Gauges, AI)
        self.populate_middle_column(middle_column_frame)

        # Populate Right Column (Charts)
        self.populate_right_column(right_column_frame)
        
        # Add a bottom status bar for version and simulation button
        bottom_bar_frame = ttk.Frame(app_frame, style='BottomBar.TFrame', padding=(10,5))
        bottom_bar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.style.configure('BottomBar.TFrame', background=PAGE_BG_COLOR)

        version_label = ttk.Label(bottom_bar_frame, text=APP_VERSION, font=FONT_STATUS, style='Version.TLabel')
        version_label.pack(side=tk.LEFT, padx=10)
        self.style.configure('Version.TLabel', background=PAGE_BG_COLOR, foreground=TEXT_COLOR_VERSION)

        self.sim_button_widget = ttk.Button(bottom_bar_frame, textvariable=self.sim_button_text_var, command=self.toggle_simulation_mode, style='Sim.TButton')
        self.sim_button_widget.pack(side=tk.RIGHT, padx=10) # Added pack for the button

    def populate_left_column(self, parent_frame):
        """Populates the left column with sensor data panels."""
        if self.debug_mode: print("DEBUG: populate_left_column - ENTER")
        parent_frame.columnconfigure(0, weight=1)

        left_panel_order = ["weather", "eco2", "tvoc", "uv_index", "noise"]

        for i, key in enumerate(left_panel_order):
            if key not in self.panel_configs:
                logging.warning(f"populate_left_column: Key '{key}' not found in panel_configs. Skipping.")
                if self.debug_mode: print(f"DEBUG: populate_left_column - Key '{key}' not in panel_configs.")
                continue
            
            config = self.panel_configs[key]
            # Increased internal padding and pady for grid
            panel_frame = ttk.Frame(parent_frame, style='DataPanel.TFrame', relief=tk.RIDGE, borderwidth=1, padding=(8,5))
            panel_frame.grid(row=i, column=0, sticky="new", pady=4, padx=5) # Increased pady
            parent_frame.rowconfigure(i, weight=0)

            self.style.configure('DataPanel.TFrame', background=PANEL_BG_COLOR)

            panel_frame.columnconfigure(0, weight=0) # Icon
            panel_frame.columnconfigure(1, weight=1) # Text content

            icon_label = ttk.Label(panel_frame, text=config.get("icon", " "), font=FONT_PANEL_ICON, style='PanelIcon.TLabel')
            # Adjusted rowspan for weather, sticky "n", more padx, pady for weather icon
            icon_label.grid(row=0, column=0, rowspan=3 if key == "weather" else 1, sticky="n", padx=(0, 8), pady=(5 if key == "weather" else 2))
            self.style.configure('PanelIcon.TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR_PANEL_TITLE)
            
            text_content_frame = ttk.Frame(panel_frame, style='PanelText.TFrame')
            text_content_frame.grid(row=0, column=1, sticky="new") # Changed sticky to new
            self.style.configure('PanelText.TFrame', background=PANEL_BG_COLOR)

            if key == "weather":
                text_content_frame.columnconfigure(0, weight=1) # Allow weather section to expand

                title_label = ttk.Label(text_content_frame, text=f"{config.get('display_title', key)}", font=FONT_PANEL_LABEL, style='PanelTitleSmall.TLabel')
                title_label.grid(row=0, column=0, sticky='w', pady=(0,3)) # Title for weather section
                
                if "weather_temp" not in self.data_vars: self.data_vars["weather_temp"] = tk.StringVar(value="--")
                if "weather_wind" not in self.data_vars: self.data_vars["weather_wind"] = tk.StringVar(value="--")
                if "weather_humidity" not in self.data_vars: self.data_vars["weather_humidity"] = tk.StringVar(value="--")

                # Temperature
                temp_frame = ttk.Frame(text_content_frame, style='PanelText.TFrame')
                temp_frame.grid(row=1, column=0, sticky='ew', pady=1)
                ttk.Label(temp_frame, text="温度:", font=FONT_PANEL_LABEL, style='PanelTitleSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(temp_frame, textvariable=self.data_vars["weather_temp"], font=FONT_PANEL_VALUE, style='PanelValueSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(temp_frame, text="°C", font=FONT_PANEL_UNIT, style='PanelUnit.TLabel').pack(side=tk.LEFT)

                # Wind
                wind_frame = ttk.Frame(text_content_frame, style='PanelText.TFrame')
                wind_frame.grid(row=2, column=0, sticky='ew', pady=1)
                ttk.Label(wind_frame, text="风速:", font=FONT_PANEL_LABEL, style='PanelTitleSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(wind_frame, textvariable=self.data_vars["weather_wind"], font=FONT_PANEL_VALUE, style='PanelValueSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(wind_frame, text="m/s", font=FONT_PANEL_UNIT, style='PanelUnit.TLabel').pack(side=tk.LEFT)

                # Humidity
                humi_frame = ttk.Frame(text_content_frame, style='PanelText.TFrame')
                humi_frame.grid(row=3, column=0, sticky='ew', pady=1)
                ttk.Label(humi_frame, text="湿度:", font=FONT_PANEL_LABEL, style='PanelTitleSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(humi_frame, textvariable=self.data_vars["weather_humidity"], font=FONT_PANEL_VALUE, style='PanelValueSmall.TLabel').pack(side=tk.LEFT, padx=(0,2))
                ttk.Label(humi_frame, text="%RH", font=FONT_PANEL_UNIT, style='PanelUnit.TLabel').pack(side=tk.LEFT)
            else: # Non-weather items
                # Using a frame to group label, value, unit for better control with pack
                item_frame = ttk.Frame(text_content_frame, style='PanelText.TFrame')
                item_frame.pack(fill=tk.X, anchor='w') # Fill horizontally, anchor west

                title_str = config.get("display_title", key)
                title_label = ttk.Label(item_frame, text=f"{title_str}:", font=FONT_PANEL_LABEL, style='PanelTitleSmall.TLabel')
                title_label.pack(side=tk.LEFT, padx=(0,5))
                self.style.configure('PanelTitleSmall.TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR_PANEL_TITLE)

                value_label = ttk.Label(item_frame, textvariable=self.data_vars[key], font=FONT_PANEL_VALUE, style='PanelValueSmall.TLabel')
                value_label.pack(side=tk.LEFT, padx=(0,5))
                self.style.configure('PanelValueSmall.TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR_VALUE)

                unit_str = config.get("unit", "")
                if unit_str:
                    unit_label = ttk.Label(item_frame, text=f"{unit_str}", font=FONT_PANEL_UNIT, style='PanelUnit.TLabel')
                    unit_label.pack(side=tk.LEFT)
                self.style.configure('PanelUnit.TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR_UNIT)
        
        if self.debug_mode: print("DEBUG: populate_left_column - EXIT")

    def populate_middle_column(self, parent_frame):
        """Populates the middle column with video, gauges, and AI suggestions."""
        if self.debug_mode: print("DEBUG: populate_middle_column - ENTER")
        parent_frame.rowconfigure(0, weight=3)  # Video gets more space
        parent_frame.rowconfigure(1, weight=1)  # Gauges
        parent_frame.rowconfigure(2, weight=2)  # AI suggestions
        parent_frame.columnconfigure(0, weight=1)

        # --- Video Stream Area ---
        video_frame = ttk.LabelFrame(parent_frame, text="📹 实时监控", style='Section.TLabelframe', padding=5)
        video_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        self.style.configure('Section.TLabelframe', background=PANEL_BG_COLOR, bordercolor=BORDER_LINE_COLOR)
        self.style.configure('Section.TLabelframe.Label', font=FONT_PANEL_TITLE, foreground=TEXT_COLOR_PANEL_TITLE, background=PANEL_BG_COLOR)
        
        self.camera_image_label = ttk.Label(video_frame, background=VIDEO_BG_COLOR, anchor=tk.CENTER)
        self.camera_image_label.pack(expand=True, fill=tk.BOTH)
        # Placeholder text until first frame
        self.camera_image_label.configure(text="等待视频信号...", font=FONT_PANEL_LABEL, foreground=TEXT_COLOR_NORMAL)


        # --- Gauges Area (Two side-by-side) ---
        gauges_frame_container = ttk.LabelFrame(parent_frame, text="📊 等级仪表盘", style='Section.TLabelframe', padding=5)
        gauges_frame_container.grid(row=1, column=0, sticky="nsew", pady=5)
        gauges_frame_container.columnconfigure(0, weight=1)
        gauges_frame_container.columnconfigure(1, weight=1)
        gauges_frame_container.rowconfigure(0, weight=1)

        # Gauge 1 (AQI)
        self.gauge_aqi_canvas = tk.Canvas(gauges_frame_container, bg=PANEL_BG_COLOR, highlightthickness=0)
        self.gauge_aqi_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Gauge 2 (UV Risk) - formerly gauge_eco2_canvas
        self.gauge_uv_risk_canvas = tk.Canvas(gauges_frame_container, bg=PANEL_BG_COLOR, highlightthickness=0)
        self.gauge_uv_risk_canvas.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # --- AI Suggestions Area ---
        ai_frame = ttk.LabelFrame(parent_frame, text="💡 AI健康建议", style='Section.TLabelframe', padding=5)
        ai_frame.grid(row=2, column=0, sticky="nsew", pady=(5,0))
        
        self.ai_advice_text_widget = tk.Text(ai_frame, wrap=tk.WORD, height=6, font=FONT_AI_ADVICE, 
                                             bg=PANEL_BG_COLOR, fg=TEXT_COLOR_AI_ADVICE, 
                                             relief=tk.FLAT, highlightthickness=0,
                                             padx=5, pady=5)
        self.ai_advice_text_widget.pack(expand=True, fill=tk.BOTH)
        self.ai_advice_text_widget.insert(tk.END, "AI建议正在加载...")
        self.ai_advice_text_widget.config(state=tk.DISABLED)
        print("DEBUG: populate_middle_column - EXIT")

    def populate_right_column(self, parent_frame):
        """填充右侧栏的图表。"""
        if self.debug_mode: print("DEBUG: populate_right_column called")
        # parent_frame IS the right_column_frame, no need to create another one and pack it.
        # Charts will be packed directly into parent_frame.

        # Temperature Chart
        # Reduced figsize slightly
        self.fig_temp, self.ax_temp = plt.subplots(figsize=(4, 2.2)) # Was (5, 2.5)
        self.ax_temp.set_title("温度变化 (°C)")
        self.ax_temp.set_xlabel("时间")
        self.ax_temp.set_ylabel("温度 (°C)")
        self.line_temp, = self.ax_temp.plot([], [], marker='o', markersize=3, linestyle='-', color='r') # Smaller markers
        self.canvas_temp = FigureCanvasTkAgg(self.fig_temp, master=parent_frame) # Use parent_frame
        self.canvas_temp_widget = self.canvas_temp.get_tk_widget()
        self.canvas_temp_widget.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        self.fig_temp.tight_layout()

        # Humidity Chart
        # Reduced figsize slightly
        self.fig_humi, self.ax_humi = plt.subplots(figsize=(4, 2.2)) # Was (5, 2.5)
        self.ax_humi.set_title("湿度变化 (%)")
        self.ax_humi.set_xlabel("时间")
        self.ax_humi.set_ylabel("湿度 (%)")
        self.line_humi, = self.ax_humi.plot([], [], marker='o', markersize=3, linestyle='-', color='b') # Smaller markers
        self.canvas_humi = FigureCanvasTkAgg(self.fig_humi, master=parent_frame) # Use parent_frame
        self.canvas_humi_widget = self.canvas_humi.get_tk_widget()
        self.canvas_humi_widget.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        self.fig_humi.tight_layout()

        # Noise Chart
        # Reduced figsize slightly
        self.fig_noise, self.ax_noise = plt.subplots(figsize=(4, 2.2)) # Was (5, 2.5)
        self.ax_noise.set_title("噪声水平 (dB)")
        self.ax_noise.set_xlabel("时间")
        self.ax_noise.set_ylabel("噪声 (dB)") # Corrected from "噪音" to "噪声" to match title
        self.line_noise, = self.ax_noise.plot([], [], marker='o', markersize=3, linestyle='-', color='g') # Smaller markers
        self.canvas_noise = FigureCanvasTkAgg(self.fig_noise, master=parent_frame) # Use parent_frame
        self.canvas_noise_widget = self.canvas_noise.get_tk_widget()
        self.canvas_noise_widget.pack(fill=tk.BOTH, expand=True)
        self.fig_noise.tight_layout()

        # Initialize chart data storage
        self.chart_data = {
            # Ensure keys here match keys used in update_chart and panel_configs for chartable items
            "temp": {"times": [], "values": [], "line": self.line_temp, "ax": self.ax_temp, "canvas": self.canvas_temp, "fig": self.fig_temp},
            "humi": {"times": [], "values": [], "line": self.line_humi, "ax": self.ax_humi, "canvas": self.canvas_humi, "fig": self.fig_humi},
            "noise": {"times": [], "values": [], "line": self.line_noise, "ax": self.ax_noise, "canvas": self.canvas_noise, "fig": self.fig_noise}
        }

    def toggle_simulation_mode(self):
        """切换模拟数据模式。"""
        self.use_simulation = not self.use_simulation
        if self.use_simulation:
            self.sim_button_text_var.set("禁用模拟数据")
            self.update_connection_status_display(False, status_text="模拟模式已启用")
            logging.info("模拟数据模式已启用")
            # Optionally, trigger an update with simulation data here
        else:
            self.sim_button_text_var.set("启用模拟数据")
            # Re-evaluate actual connection status
            self.update_connection_status_display(self._mqtt_connected, status_text="模拟模式已禁用 - 尝试连接")
            logging.info("模拟数据模式已禁用")
            if not self._mqtt_connected:
                self.connect_mqtt() # Try to reconnect if not connected

    def initial_gauge_draw(self):
        """Draws the gauges for the first time after UI is set up."""
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print("DEBUG: SmartCampusDashboard initial_gauge_draw - ENTER")
        
        # Ensure this method is called after populate_middle_column has created gauge canvases
        # For example, self.gauge_aqi_canvas and self.gauge_uv_risk_canvas should exist.

        for key, config in self.panel_configs.items():
            if config.get("gauge"):
                current_value_str = self.data_vars[key].get()
                
                if key == "aqi" and hasattr(self, 'gauge_aqi_canvas') and self.gauge_aqi_canvas:
                    current_value = 0 # Default
                    try:
                        if current_value_str != "--" and current_value_str is not None: # Added None check
                           current_value = int(float(current_value_str)) # AQI levels are often integer indices
                    except ValueError:
                        logging.warning(f"Initial gauge draw for AQI: Could not convert '{current_value_str}' to int.")
                    self.update_gauge(self.gauge_aqi_canvas, current_value, config.get("gauge_max", 5), "AQI", config.get("levels"))
                
                elif key == "uv_risk" and hasattr(self, 'gauge_uv_risk_canvas') and self.gauge_uv_risk_canvas:
                    level_value = 0 # Default to first level (e.g., "低")
                    levels = config.get("levels", [])
                    if current_value_str in levels:
                        level_value = levels.index(current_value_str)
                    elif current_value_str != "--" and current_value_str is not None: # Added None check
                        try:
                            # If current_value_str is a number, try to use it as an index
                            level_value = int(float(current_value_str))
                            if not (0 <= level_value < len(levels)):
                                logging.warning(f"Initial gauge draw for UV Risk: Index {level_value} out of bounds for levels. Resetting to 0.")
                                level_value = 0 
                        except ValueError:
                             logging.warning(f"Initial gauge draw for UV Risk: Value '{current_value_str}' is not a recognized level and not a valid index. Resetting to 0.")
                             level_value = 0 # Reset to default if not a recognized string or valid index
                    
                    self.update_gauge(self.gauge_uv_risk_canvas, level_value, config.get("gauge_max", 4), "UV Risk", levels)

        if hasattr(self, 'debug_mode') and self.debug_mode:
            print("DEBUG: SmartCampusDashboard initial_gauge_draw - EXIT")

    # Ensure other methods like connect_mqtt, start_weather_updates etc. are below this if they are part of the class.
    # The end of the file might look like this:

    def connect_mqtt(self):
        """连接MQTT服务器"""
        try:
            # 创建MQTT客户端
            client_id = f"SmartCampusDashboard_{random.randint(1000, 9999)}"
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
            
            # 设置回调函数
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            # 设置认证（如果需要）
            mqtt_config = self.config.get("mqtt", {})
            username = mqtt_config.get("username")
            password = mqtt_config.get("password")
            if username and password:
                self.mqtt_client.username_pw_set(username, password)
            
            # 连接到MQTT代理
            host = mqtt_config.get("host", "127.0.0.1")
            port = mqtt_config.get("port", 1883)
            
            print(f"正在连接到MQTT服务器: {host}:{port}")
            self.mqtt_client.connect_async(host, port, 60)
            self.mqtt_client.loop_start()
            
            self.update_connection_status_display(False, "正在连接MQTT服务器...")
            
        except Exception as e:
            print(f"MQTT连接失败: {e}")
            self.update_connection_status_display(False, f"MQTT连接失败: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT连接成功回调"""
        if rc == 0:
            print("MQTT连接成功！")
            self.update_connection_status_display(True, "MQTT连接成功")
            
            # 订阅主题
            mqtt_topics = self.config.get("mqtt", {}).get("topics", [])
            for topic in mqtt_topics:
                client.subscribe(topic)
                print(f"已订阅主题: {topic}")
                
            # 启用实时数据模式
            self.use_simulation = False
        else:
            print(f"MQTT连接失败，返回码: {rc}")
            self.update_connection_status_display(False, f"MQTT连接失败 (码: {rc})")
            # 启用模拟数据模式
            self.use_simulation = True

    def on_message(self, client, userdata, msg):
        """MQTT消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8', errors='ignore')
            
            print(f"收到MQTT消息: {topic} = {payload}")
            
            # 处理传感器数据
            topic_parts = topic.split('/')
            if len(topic_parts) >= 2:
                sensor_name = topic_parts[-1]  # 取最后一部分作为传感器名称
                
                # 更新数据
                if sensor_name in self.data_vars:
                    self.data_vars[sensor_name].set(payload)
                    
                    # 如果是仪表盘数据，更新仪表盘
                    if sensor_name in self.panel_configs:
                        config = self.panel_configs[sensor_name]
                        if config.get("gauge"):
                            self.update_gauge_data(sensor_name, payload)
                
            # 处理视频数据
            if "视频" in topic or "video" in topic.lower():
                self.process_video_frame(payload)
                
        except Exception as e:
            print(f"处理MQTT消息时出错: {e}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        """MQTT断开连接回调"""
        print(f"MQTT连接已断开，返回码: {rc}")
        self.update_connection_status_display(False, "MQTT连接已断开")
        
        # 启用模拟数据模式
        self.use_simulation = True
        
        # 尝试重连（10秒后）
        self.root.after(10000, self.connect_mqtt)

    def start_weather_updates(self):
        """启动天气数据更新"""
        try:
            print("启动天气数据更新...")
            # 首次立即获取
            self.fetch_weather_data()
            # 每30分钟更新一次
            self.root.after(30 * 60 * 1000, self.start_weather_updates)
        except Exception as e:
            print(f"天气数据更新失败: {e}")
            # 即使失败也要继续定期尝试
            self.root.after(30 * 60 * 1000, self.start_weather_updates)

    def fetch_weather_data(self):
        """获取天气数据"""
        try:
            import requests
            
            api_key = "d24595021efb5faa04f4f6744c94086f"
            city = "Tianshui"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=zh_cn"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                # 更新天气数据
                if "weather_desc" in self.data_vars:
                    weather_desc = data.get("weather", [{}])[0].get("description", "未知")
                    self.data_vars["weather_desc"].set(weather_desc)
                    
                if "wind_speed" in self.data_vars:
                    wind_speed = data.get("wind", {}).get("speed", 0)
                    self.data_vars["wind_speed"].set(f"{wind_speed:.1f}")
                    
                print("天气数据获取成功")
            else:
                print(f"天气API返回错误: {data}")
                
        except Exception as e:
            print(f"获取天气数据失败: {e}")

    def start_time_updates(self):
        """启动时间更新"""
        try:
            current_time = time.strftime("%H:%M:%S")
            if hasattr(self, 'time_var'):
                self.time_var.set(current_time)
            
            # 每秒更新一次
            self.root.after(1000, self.start_time_updates)
        except Exception as e:
            print(f"时间更新失败: {e}")
            # 继续尝试
            self.root.after(1000, self.start_time_updates)

    def start_system_status_check(self):
        """启动系统状态检查"""
        try:
            print("系统状态检查...")
            
            # 检查MQTT连接状态
            if self.mqtt_client and self.mqtt_client.is_connected():
                print("MQTT连接正常")
            else:
                print("MQTT连接异常")
                
            # 检查数据更新状态
            current_time = time.time()
            if hasattr(self, 'last_data_update'):
                time_since_update = current_time - self.last_data_update
                if time_since_update > 300:  # 5分钟无数据
                    print("警告：长时间未收到数据")
                    if not self.use_simulation:
                        print("切换到模拟数据模式")
                        self.use_simulation = True
            
            # 每分钟检查一次
            self.root.after(60000, self.start_system_status_check)
            
        except Exception as e:
            print(f"系统状态检查失败: {e}")
            self.root.after(60000, self.start_system_status_check)

    def update_gauge(self, canvas, value, max_value, title, levels=None):
        """更新仪表盘显示"""
        if not canvas:
            return
            
        try:
            # 清除画布
            canvas.delete("all")
            
            # 画布尺寸
            width = canvas.winfo_width() or 200
            height = canvas.winfo_height() or 200
            
            # 中心点和半径
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 2 - 20
            
            # 绘制外圆
            canvas.create_oval(center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius,
                             outline="#CCCCCC", width=2)
            
            # 绘制刻度
            import math
            for i in range(6):  # 6个刻度点
                angle = math.radians(-180 + i * 36)  # 180度范围，6个点
                x1 = center_x + (radius - 10) * math.cos(angle)
                y1 = center_y + (radius - 10) * math.sin(angle)
                x2 = center_x + radius * math.cos(angle)
                y2 = center_y + radius * math.sin(angle)
                canvas.create_line(x1, y1, x2, y2, fill="#CCCCCC", width=2)
            
            # 计算指针角度
            if max_value > 0:
                ratio = min(value / max_value, 1.0)
            else:
                ratio = 0
            needle_angle = math.radians(-180 + ratio * 180)
            
            # 绘制指针
            needle_x = center_x + (radius - 30) * math.cos(needle_angle)
            needle_y = center_y + (radius - 30) * math.sin(needle_angle)
            canvas.create_line(center_x, center_y, needle_x, needle_y,
                             fill="#FF6666", width=4)
            
            # 绘制中心圆
            canvas.create_oval(center_x - 8, center_y - 8,
                             center_x + 8, center_y + 8,
                             fill="#FF6666", outline="#FF6666")
            
            # 显示数值
            if levels and isinstance(value, int) and 0 <= value < len(levels):
                display_text = levels[value]
            else:
                display_text = str(value)
                
            canvas.create_text(center_x, center_y + 40,
                             text=display_text,
                             fill="#FFFFFF", font=("Arial", 12, "bold"))
            
            # 显示标题
            canvas.create_text(center_x, center_y - 40,
                             text=title,
                             fill="#FFFFFF", font=("Arial", 10))
            
        except Exception as e:
            print(f"更新仪表盘失败: {e}")

    def update_gauge_data(self, sensor_name, value_str):
        """更新仪表盘数据"""
        try:
            config = self.panel_configs.get(sensor_name, {})
            if not config.get("gauge"):
                return
                
            if sensor_name == "aqi" and hasattr(self, 'gauge_aqi_canvas'):
                try:
                    value = int(float(value_str))
                    max_value = config.get("gauge_max", 5)
                    levels = config.get("levels")
                    self.update_gauge(self.gauge_aqi_canvas, value, max_value, "AQI", levels)
                except ValueError:
                    pass
                    
            elif sensor_name == "uv_risk" and hasattr(self, 'gauge_uv_risk_canvas'):
                levels = config.get("levels", [])
                if value_str in levels:
                    level_value = levels.index(value_str)
                    max_value = len(levels) - 1
                    self.update_gauge(self.gauge_uv_risk_canvas, level_value, max_value, "UV风险", levels)
                    
        except Exception as e:
            print(f"更新仪表盘数据失败: {e}")

    def process_video_frame(self, payload):
        """处理视频帧数据"""
        try:
            if not PIL_AVAILABLE:
                return
                
            # 尝试解码base64数据
            import base64
            import io
            from PIL import Image, ImageTk
            
            image_data = base64.b64decode(payload)
            image = Image.open(io.BytesIO(image_data))
            
            # 调整图像大小
            video_width = self.config.get("video", {}).get("width", 480)
            video_height = self.config.get("video", {}).get("height", 360)
            image = image.resize((video_width, video_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 更新视频显示
            if hasattr(self, 'camera_image_label') and self.camera_image_label:
                self.camera_image_label.configure(image=photo)
                self.camera_image_label.image = photo  # 保持引用
                
            print("视频帧更新成功")
            
        except Exception as e:
            print(f"处理视频帧失败: {e}")

# 启动应用程序的代码
if __name__ == "__main__":
    print("DEBUG: __main__ - ENTER")
    root = tk.Tk()
    app = SmartCampusDashboard(root)
    root.mainloop()
    print("DEBUG: __main__ - EXIT")
