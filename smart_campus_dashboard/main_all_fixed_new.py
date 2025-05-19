print("脚本开始执行...") # DEBUG: Script start
# -*- coding: utf-8 -*-
# 确保导入json库
# 新增：用于Basic Authentication
# 新增：用于URL编码Topic
# 新增：用于MQTT通信
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
SIOT_SERVER_HTTP = "http://192.168.1.129:8080"
SIOT_USERNAME = "siot"
SIOT_PASSWORD = "dfrobot"

MQTT_BROKER_HOST = "192.168.1.129"
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "smart_campus_dashboard_client_001" # 确保客户端ID唯一
MQTT_CAMERA_TOPIC = "sc/camera/stream" # 修改为实际使用的Topic
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

APP_VERSION = "v1.1.0" # Updated for new design
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
        self.last_data_received_time = None # 追踪最后一次数据接收时间
        self.last_chart_update = None # 追踪最后一次图表更新时间

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

        print("DEBUG: SmartCampusDashboard initialized")

    def create_main_layout(self, parent_frame):
        print("DEBUG: self.create_main_layout called")

        main_regions_frame = tk.Frame(parent_frame, bg=PAGE_BG_COLOR)
        main_regions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Adjusted column weights: Left:3, Middle:2 (narrower), Right:5 (wider)
        main_regions_frame.grid_columnconfigure(0, weight=3)
        main_regions_frame.grid_columnconfigure(1, weight=2, minsize=250) # Middle region, narrower with reduced minsize
        main_regions_frame.grid_columnconfigure(2, weight=5) # Right region, wider
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
        
            content_row_frame = tk.Frame(panel_frame, bg=PANEL_BG_COLOR)
            content_row_frame.pack(fill="x")
        
            if icon_char:
                icon_label = tk.Label(content_row_frame, text=icon_char, font=FONT_PANEL_ICON, fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR)
                icon_label.pack(side="left", padx=(0, 5))
        
            title_label = tk.Label(content_row_frame, text=display_title + ":", font=FONT_PANEL_LABEL, fg=TEXT_COLOR_PANEL_TITLE, bg=PANEL_BG_COLOR)
            title_label.pack(side="left", padx=(0,5))
        
            value_unit_frame = tk.Frame(content_row_frame, bg=PANEL_BG_COLOR)
            value_unit_frame.pack(side="right")
        
            if key in self.data_vars and self.data_vars[key] is not None:
                value_label = tk.Label(value_unit_frame, textvariable=self.data_vars[key], font=FONT_PANEL_VALUE, fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
                value_label.pack(side="left", anchor="s")
            else:
                tk.Label(value_unit_frame, text="--", font=FONT_PANEL_VALUE, fg="red", bg=PANEL_BG_COLOR).pack(side="left", anchor="s")
                print(f"DEBUG: self.data_vars missing or None for key: {key} in create_main_layout")
        
            if unit:
                unit_label = tk.Label(value_unit_frame, text=unit, font=FONT_PANEL_UNIT, fg=TEXT_COLOR_UNIT, bg=PANEL_BG_COLOR)
                unit_label.pack(side="left", anchor="s", padx=(3,0), pady=(0,3))
                
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

        # --- Middle Region (Video Top, AI Bottom) ---
        middle_region_frame = tk.Frame(main_regions_frame, bg=PAGE_BG_COLOR, padx=5, pady=5)
        middle_region_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        middle_region_frame.grid_rowconfigure(0, weight=4)
        middle_region_frame.grid_rowconfigure(1, weight=1)
        middle_region_frame.grid_columnconfigure(0, weight=1)

        video_outer_frame = tk.Frame(middle_region_frame, bg=VIDEO_BG_COLOR,
                                     highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        video_outer_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        tk.Label(video_outer_frame, text="实时监控视频", font=FONT_PANEL_TITLE, fg=TEXT_COLOR_PANEL_TITLE, bg=VIDEO_BG_COLOR).pack(anchor="nw", padx=10, pady=5)
        
        # Temporarily set a bright background to debug video label visibility and size
        self.camera_image_label = tk.Label(video_outer_frame, bg="magenta") # DEBUG: Bright color for visibility
        self.camera_image_label.pack(expand=True, fill="both")

        ai_advice_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR, pady=5, padx=10,
                                   highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        ai_advice_frame.grid(row=1, column=0, sticky="nsew", pady=(5,0))

        tk.Label(ai_advice_frame, text="AI建议", font=FONT_AI_SECTION_TITLE, fg=TEXT_COLOR_AI_TITLE, bg=PANEL_BG_COLOR).pack(anchor="nw", padx=10, pady=5)

        self.ai_advice_text_widget = tk.Text(ai_advice_frame, height=5, wrap=tk.WORD, bg=PANEL_BG_COLOR, fg=TEXT_COLOR_AI_ADVICE,
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
        self._debug_video_update_counter += 1
        # print(f"DEBUG: update_camera_stream called (call #{self._debug_video_update_counter})")

        if not PIL_AVAILABLE:
            if self._debug_video_update_counter % 50 == 1: # Log less frequently
                print("DEBUG: Pillow (PIL) not available, cannot process video stream.")
            return

        try:
            if not isinstance(data, dict) or "image" not in data:
                if self._debug_video_update_counter % 10 == 1: # Log less frequently
                    print(f"DEBUG: Invalid or missing 'image' key in camera data. Data type: {type(data)}")
                return

            image_data_b64 = data["image"]
            if not image_data_b64:
                if self._debug_video_update_counter % 10 == 1: # Log less frequently
                    print("DEBUG: 'image' key present but data is empty.")
                return

            # print(f"DEBUG: image_data_b64 (first 64 chars): {image_data_b64[:64]}")
            
            try:
                image_bytes = base64.b64decode(image_data_b64)
            except base64.binascii.Error as b64_error:
                print(f"ERROR: Base64 decoding error: {b64_error}. Is the image data correctly base64 encoded? Data (first 64): {image_data_b64[:64]}")
                return
            except Exception as e:
                print(f"ERROR: Unexpected error during base64 decoding: {type(e).__name__} - {e}")
                return

            # print(f"DEBUG: Decoded image_bytes length: {len(image_bytes)}")
            if not image_bytes:
                print("ERROR: Decoded image_bytes is empty.")
                return

            try:
                img_io = io.BytesIO(image_bytes)
                image = Image.open(img_io)
            except UnidentifiedImageError as uie:
                print(f"ERROR: Pillow UnidentifiedImageError - Cannot identify image file. Is the base64 data a valid image? Details: {uie}")
                return
            except OSError as ose: # Catch OS errors during Image.open, e.g., file not found, permissions
                print(f"ERROR: Pillow OSError during Image.open: {ose}")
                return
            except Exception as e:
                print(f"ERROR: Unexpected error during Image.open: {type(e).__name__} - {e}")
                return
                
            # print(f"DEBUG: Image opened: mode={image.mode}, size={image.size}, format={image.format}")

            container_width = self.camera_image_label.winfo_width()
            container_height = self.camera_image_label.winfo_height()

            if container_width <= 10 or container_height <= 10:
                # Fallback if container size is not yet determined, use a smaller default
                target_width, target_height = 220, 165 # Approx 4:3, fits in 250 width minsize column
            else:
                target_width, target_height = container_width, container_height
            
            original_width, original_height = image.size
            if original_width == 0 or original_height == 0:
                print("ERROR: Original image dimensions are zero.")
                return

            aspect_ratio = original_width / float(original_height) # Ensure float division

            # Calculate new dimensions to fit into target_width, target_height while maintaining aspect ratio
            if target_width / aspect_ratio <= target_height:
                new_width = target_width
                new_height = int(new_width / aspect_ratio) if aspect_ratio > 0 else target_width # handle aspect_ratio = 0
            else:
                new_height = target_height
                new_width = int(new_height * aspect_ratio)

            if new_width <= 0: new_width = 1 # Ensure positive dimensions
            if new_height <= 0: new_height = 1 # Ensure positive dimensions
            
            try:
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            except OSError as ose: # Catch OS errors during resize (e.g. related to image data)
                print(f"ERROR: Pillow OSError during image.resize: {ose}")
                return
            except Exception as e:
                print(f"ERROR: Unexpected error during image.resize: {type(e).__name__} - {e}")
                return

            # print(f"DEBUG: Image resized to: {image.size}")

            try:
                self.video_photo_image = ImageTk.PhotoImage(image)
            except RuntimeError as rte: # Catches some Tkinter internal errors with malformed images
                 print(f"ERROR: RuntimeError creating ImageTk.PhotoImage: {rte}. This can happen with corrupted image data or Tkinter issues.")
                 return
            except Exception as e:
                print(f"ERROR: Unexpected error creating ImageTk.PhotoImage: {type(e).__name__} - {e}")
                return

            # print("DEBUG: ImageTk.PhotoImage created successfully.")

            if self.camera_image_label:
                # Remove explicit width/height setting on label, image is already resized
                self.camera_image_label.config(image=self.video_photo_image)
                self.camera_image_label.image = self.video_photo_image # Keep a reference!
                # if self._debug_video_update_counter % 20 == 1: # Log less frequently
                #     print(f"DEBUG: self.camera_image_label updated with new image {new_width}x{new_height}.")
            else:
                # This case should ideally not happen if UI is set up correctly
                print("ERROR: self.camera_image_label is None, cannot update video stream.")

        except Exception as e:
            # This is a general catch-all for unexpected errors within the update_camera_stream logic itself
            print(f"FATAL ERROR in update_camera_stream: {type(e).__name__} - {e}")
            # Optionally, re-raise or handle more gracefully depending on desired app behavior
            # For now, just printing to avoid crashing the entire app if possible, though SIGABRT suggests this might not be enough.

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
            print(f"DEBUG: Attempting to connect to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} with client ID {MQTT_CLIENT_ID}, User: {SIOT_USERNAME}")
            self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            self.mqtt_client.loop_start()
            print("DEBUG: MQTT client loop_start called.")
        except socket.error as e:
            print(f"MQTT连接错误: {e} - 无法连接到代理。")
            self.update_connection_status_display(False, f"连接错误: {e}")
        except Exception as e: # Catch other potential errors like paho.mqtt.client.WebsocketConnectionError
            print(f"MQTT连接期间发生未知错误: {type(e).__name__} - {e}")
            self.update_connection_status_display(False, f"未知错误: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"DEBUG: MQTT on_connect called with rc: {mqtt.connack_string(rc)}, flags: {flags}, properties: {properties}")
        if rc == 0: # Connection successful
            self.update_connection_status_display(True)
            print("MQTT连接成功，订阅主题...")
            # 使用通配符订阅所有SIOT主题
            client.subscribe("siot/#")
            print("  已订阅: siot/# (通配符订阅)")
            
            # 同时保留对特定主题的订阅
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                print(f"  已订阅: {topic}")
            # Also subscribe to weather topic if not already in MQTT_TOPICS for general messages
            if MQTT_WEATHER_TOPIC not in MQTT_TOPICS:
                 client.subscribe(MQTT_WEATHER_TOPIC)
                 print(f"  已订阅天气主题: {MQTT_WEATHER_TOPIC}")
            self.fetch_weather_data() # Fetch initial weather data on connect
        elif rc == 5: # Not authorized
            print("MQTT连接失败，状态码：Not authorized")
            self.update_connection_status_display(False, "MQTT认证失败")
        else:
            error_string = mqtt.connack_string(rc)
            print(f"MQTT连接失败，状态码：{rc} ({error_string})")
            self.update_connection_status_display(False, f"MQTT连接失败: {error_string} (码 {rc})")

    def on_disconnect(self, client, userdata, flags, rc, properties=None): # Added flags for V2
        # rc is a DisconnectReasonCode instance for V2, or an int for V1
        if isinstance(rc, int): # V1 compatibility or unexpected
            reason_code_int = rc
            reason_string = f"Return code: {rc}"
        else: # V2, rc is a ReasonCode object
            reason_code_int = rc.value if hasattr(rc, 'value') else -1 # Get int value if possible
            reason_string = str(rc)

        print(f"DEBUG: MQTT on_disconnect: client={client}, userdata={userdata}, flags={flags}, rc(reason)={reason_string}, properties={properties}")
        
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

        payload_str = ""
        try:
            # Try to decode as UTF-8. If it fails, it might be raw bytes for an image,
            # but for camera, we expect base64 encoded string, often within JSON.
            payload_str = msg.payload.decode('utf-8')
        except UnicodeDecodeError:
            # If it's the camera topic and decoding fails, it's problematic as we expect string data.
            # For other topics, it might be binary, but our current sensors send strings.
            print(f"ERROR: UnicodeDecodeError for topic {msg.topic}. Payload might not be UTF-8.")
            # If it's camera topic, we probably can't proceed with current logic.
            if msg.topic == self.MQTT_CAMERA_TOPIC:
                print(f"ERROR: Camera topic {msg.topic} received non-UTF-8 payload. Cannot process as base64 string.")
                return
            # For other topics, this would be an unexpected error.
            # For now, just return, or handle as appropriate if binary data is expected for some topics.
            return

        topic_str = msg.topic
        print(f"DEBUG: MQTT on_message: Topic: {topic_str}, Raw Payload: {payload_str[:120]}") # Log raw payload

        # Simplified topic to key mapping based on panel_configs
        matched_key = None
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
                    break
                # 2. 处理通配符情况（例如从 'siot/#' 订阅到的主题）
                if topic_str.startswith("siot/"):
                    topic_part = topic_str.split("/", 1)[1]
                    # 精确匹配主题名
                    if config_data["base_topic_name"] == topic_part:
                        matched_key = key
                        break
                    # 尝试模糊匹配（针对某些主题可能有前缀或后缀的情况）
                    if topic_part.find(config_data["base_topic_name"]) >= 0:
                        print(f"模糊匹配主题: {topic_str} 映射到 {key}")
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
                # Attempt to decode payload as JSON first
                try:
                    json_data = json.loads(payload_str)
                    if isinstance(json_data, dict) and "image" in json_data:
                        image_data_b64 = json_data["image"]
                        print("DEBUG: Extracted image_data_b64 from JSON payload for camera.") # New log
                    else:
                        print(f"DEBUG: JSON payload on camera topic, but no 'image' key or not a dict. Keys: {json_data.keys() if isinstance(json_data, dict) else 'Not a dict'}")
                except json.JSONDecodeError:
                    print("DEBUG: Camera payload is not JSON, trying as raw/dataURI.") # New log
                    if payload_str.startswith("data:image"):
                        image_data_b64 = payload_str.split(',', 1)[1] if ',' in payload_str else None
                        if image_data_b64:
                            print("DEBUG: Extracted image_data_b64 from data URI for camera.") # New log
                        else:
                            print("DEBUG: Could not extract base64 from data URI for camera.")
                    elif len(payload_str) > 100: # Heuristic for likely base64
                        image_data_b64 = payload_str
                        print("DEBUG: Assuming raw payload is image_data_b64 for camera.") # New log
                    else:
                        print(f"DEBUG: Payload on camera topic is short and not JSON/dataURI. Length: {len(payload_str)}")

                if image_data_b64:
                    print(f"DEBUG: Queueing camera frame update. image_data_b64 (first 30): {image_data_b64[:30]}") # New log
                    self.root.after(0, self.update_camera_stream, {"image": image_data_b64})
                else:
                    print(f"DEBUG: No image_data_b64 extracted for camera topic {topic_str}. Payload (first 100): {payload_str[:100]}")
            except Exception as e:
                print(f"ERROR: Exception in on_message for camera topic {topic_str} before queueing update_camera_stream: {type(e).__name__} - {e}")
            return # Explicit return after handling camera topic

        elif matched_key:
            # print(f"DEBUG: Matched topic {topic_str} to key {matched_key}")
            try:
                data_value = payload_str # Assume payload is the direct value for sensors
                # Attempt to convert to float if possible, otherwise keep as string
                try:
                    data_value = float(payload_str)
                    # If it's an integer, convert to int for cleaner display
                    if data_value.is_integer():
                        data_value = int(data_value)
                except ValueError:
                    pass # Keep as string if not a float

                self.root.after(0, self.update_sensor_data, matched_key, data_value)
            except Exception as e:
                print(f"ERROR: Exception processing sensor data for topic {topic_str}, key {matched_key}: {type(e).__name__} - {e}")
        else:
            print(f"Warning: Received message on unhandled topic: {topic_str}. Payload: {payload_str[:100]}")

    def update_sensor_data(self, panel_key, data_value): # Renamed 'topic' to 'panel_key', 'data_str' to 'data_value'
        print(f"DEBUG: SmartCampusDashboard.update_sensor_data called. Key: {panel_key}, Data: {str(data_value)[:50]}")
        # 记录最后一次数据接收时间
        self.last_data_received_time = datetime.now()
        
        if self.use_simulation:
            print("模拟模式已启用，忽略真实传感器数据。")
            return

        # The 'panel_key' argument is already the correct key for panel_configs and data_vars,
        # as determined in on_message.
        if panel_key and panel_key in self.data_vars:
            self.data_vars[panel_key].set(str(data_value)) # Ensure string for StringVar

            if panel_key in self.panel_configs: # Use self.panel_configs
                 print(f"UI更新: {self.panel_configs[panel_key]['display_title']} = {data_value}")
            else:
                 print(f"UI更新: (未知标题 for key {panel_key}) = {data_value}")

            # 更新图表历史数据，使用(timestamp, value)格式
            try:
                numeric_value = float(data_value) # 将数据值转换为浮点数
                current_time = datetime.now()     # 获取当前时间
                
                # 限制历史数据长度，避免内存过度使用
                max_history_points = 30
                
                if panel_key == "temp":
                    # 添加新的数据点（时间和值）
                    self.chart_data_history['temperature'].append((current_time, numeric_value))
                    # 如果历史数据超过最大长度，移除最早的数据点
                    if len(self.chart_data_history['temperature']) > max_history_points:
                        self.chart_data_history['temperature'].popleft()
                        
                elif panel_key == "humi":
                    self.chart_data_history['humidity'].append((current_time, numeric_value))
                    if len(self.chart_data_history['humidity']) > max_history_points:
                        self.chart_data_history['humidity'].popleft()
                        
                elif panel_key == "noise": 
                    self.chart_data_history['noise'].append((current_time, numeric_value))
                    if len(self.chart_data_history['noise']) > max_history_points:
                        self.chart_data_history['noise'].popleft()
                
                print(f"DEBUG: 更新图表数据 - {panel_key}, 值: {numeric_value}, 时间: {current_time.strftime('%H:%M:%S')}")

            except (ValueError, TypeError) as e:
                print(f"警告: 无法将来自键 {panel_key} 的数据 '{data_value}' ({type(data_value).__name__}) 转换为数值以更新图表: {e}")
            
            # 控制图表更新频率，如果是温度更新才触发图表更新，避免每个数据都更新导致性能问题
            if panel_key == "temp":
                self.update_charts() # 只有温度更新时才重绘图表
            elif not hasattr(self, 'last_chart_update') or (datetime.now() - self.last_chart_update).total_seconds() > 10:
                # 或者如果已经10秒没有更新图表，则更新图表
                self.update_charts()
                self.last_chart_update = datetime.now()
        else:
            print(f"警告: update_sensor_data 收到未映射或未知的键: {panel_key}")
        
        self.update_ai_advice() # Update AI advice based on new data

    def toggle_simulation(self):
        self.use_simulation = not self.use_simulation
        if self.use_simulation:
            self.sim_button_text_var.set("禁用模拟数据")
            print("模拟数据已启用")
            for p_key, sim_val in simulation_data.items(): # Iterate through simulation_data keys (e.g., "环境温度")
                config_key_to_update = None
                # for panel_config_key, config_details in panel_configs.items(): # Use self.panel_configs
                for panel_config_key, config_details in self.panel_configs.items():
                    if config_details["base_topic_name"] == p_key:
                        config_key_to_update = panel_config_key # This is "temp", "humi", etc.
                        break
                
                if config_key_to_update and config_key_to_update in self.data_vars:
                    self.data_vars[config_key_to_update].set(sim_val)
                    # print(f"  模拟: {panel_configs[config_key_to_update]['display_title']} = {sim_val}") # Use self.panel_configs
                    print(f"  模拟: {self.panel_configs[config_key_to_update]['display_title']} = {sim_val}")
            
            sim_weather = {"weather": [{"description": "晴朗（模拟）", "icon": "01d"}], "main": {"temp": 22.5, "humidity": 55}, "wind": {"speed": 1.5}}
            self.update_weather_display(sim_weather)
            print("  模拟: 天气数据已更新")

            # Clear and populate chart histories using self.chart_data_history
            self.chart_data_history['temperature'].clear()
            self.chart_data_history['humidity'].clear()
            self.chart_data_history['noise'].clear()
            
            # 创建模拟数据，包括时间戳
            now = datetime.now()
            # 为模拟数据创建过去30分钟内的不同时间点
            sim_times = [now - timedelta(minutes=i*5) for i in range(5, 0, -1)]
            sim_temps = [22, 22.5, 23, 22.8, 23.2]
            sim_humis = [50, 52, 51, 53, 52]
            sim_noises = [40, 42, 41, 43, 40]
            
            # 添加带时间戳的数据
            for i in range(5):
                self.chart_data_history['temperature'].append((sim_times[i], sim_temps[i]))
                self.chart_data_history['humidity'].append((sim_times[i], sim_humis[i]))
                self.chart_data_history['noise'].append((sim_times[i], sim_noises[i]))

        else: # Disabling simulation
            self.sim_button_text_var.set("启用模拟数据")
            print("模拟数据已禁用")
            for p_key in self.data_vars.keys():
                self.data_vars[p_key].set("--") 
            
            # Clear chart histories
            self.chart_data_history['temperature'].clear()
            self.chart_data_history['humidity'].clear()
            self.chart_data_history['noise'].clear()
            # If using self.chart_timestamps, clear them here too

            self.fetch_weather_data()
            if self.mqtt_client and self.mqtt_client.is_connected():
                print("MQTT已连接，将接收真实数据。")
            else:
                print("MQTT未连接，尝试重新连接以获取真实数据...")
                self.connect_mqtt() # Attempt to reconnect if not connected

        self.update_charts()
        self.update_ai_advice()
        self.update_connection_status_display(self.mqtt_client.is_connected() if self.mqtt_client else False, sim_mode=self.use_simulation)


    def fetch_weather_data(self):
        print(f"DEBUG: Attempting to fetch weather data from {WEATHER_API_URL}")
        try:
            response = requests.get(WEATHER_API_URL, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            weather_data = response.json()
            print("天气数据获取成功 (fetch_weather_data)")
            self.weather_data_cache = weather_data # Cache it
            self.update_weather_display(weather_data)
            self.last_weather_fetch_time = time.time()

            # Publish weather data to MQTT topic
            if self.mqtt_client and self.mqtt_client.is_connected():
                try:
                    self.mqtt_client.publish(MQTT_WEATHER_TOPIC, json.dumps(weather_data), qos=1)
                    print(f"天气数据已发布到 MQTT 主题: {MQTT_WEATHER_TOPIC}")
                except Exception as e:
                    print(f"发布天气数据到 MQTT 时出错: {e}")
            
        except requests.exceptions.Timeout:
            print(f"获取天气数据超时: {WEATHER_API_URL}")
            self.update_weather_display(None, error_msg="天气获取超时")
        except requests.exceptions.RequestException as e:
            print(f"获取天气数据时发生网络错误: {e}")
            self.update_weather_display(None, error_msg=f"天气接口错误: {e}")
        except json.JSONDecodeError:
            print("解析天气API响应时发生JSON解码错误。")
            self.update_weather_display(None, error_msg="天气数据格式错误")
        except Exception as e:
            print(f"获取或处理天气数据时发生未知错误: {e}")
            self.update_weather_display(None, error_msg=f"未知天气错误: {e}")

    def fetch_weather_data_periodic(self):
        # Fetch immediately, then schedule next
        if not self.use_simulation: # Only fetch if not in simulation mode
             self.fetch_weather_data()
        
        # Schedule next call regardless of simulation mode, fetch_weather_data itself checks use_simulation
        self.root.after(WEATHER_FETCH_INTERVAL * 1000, self.fetch_weather_data_periodic)
        print(f"DEBUG: 下一次天气数据获取计划在 {WEATHER_FETCH_INTERVAL // 60} 分钟后。")


    def update_weather_display(self, weather_data, error_msg=None):
        print(f"DEBUG: update_weather_display called. Data: {'Present' if weather_data else 'None'}. Error: {error_msg}")
        if self.use_simulation and not weather_data: # If in sim mode and no explicit sim weather data passed
            # This case is handled by toggle_simulation setting sim weather.
            # If called otherwise during sim mode without data, it might clear sim weather.
            # Let's assume toggle_simulation is the source of truth for sim weather.
            print("DEBUG: In simulation mode, weather display updated by toggle_simulation.")
            # return # Or ensure sim weather is reapplied if this is called unexpectedly
        
        if error_msg:
            if "weather_desc" in self.data_vars: self.data_vars["weather_desc"].set(error_msg)
            if "wind_speed" in self.data_vars: self.data_vars["wind_speed"].set("--")
            # Temperature and humidity from weather API are usually separate from sensor temp/humi
            # If panel_configs has specific keys for API temp/humi, update them here.
            # For now, assuming "temp" and "humi" in panel_configs are for local sensors.
            # If you add panel_configs entries like "outdoor_temp", update them here:
            # if "outdoor_temp" in self.data_vars: self.data_vars["outdoor_temp"].set(f"{api_temp}°C")

            print(f"天气数据显示错误: {error_msg}")
            return

        if weather_data and isinstance(weather_data, dict):
            try:
                description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
                # icon_code = weather_data.get('weather', [{}])[0].get('icon', '') # For icon display later
                api_temp = weather_data.get('main', {}).get('temp', '--')
                api_humidity = weather_data.get('main', {}).get('humidity', '--') # Weather API humidity
                wind_speed = weather_data.get('wind', {}).get('speed', '--')

                if "weather_desc" in self.data_vars: self.data_vars["weather_desc"].set(description)
                if "wind_speed" in self.data_vars: self.data_vars["wind_speed"].set(f"{wind_speed}")
                
                # Update specific weather related panels if they exist, e.g. "室外温度"
                # For now, panel_configs["temp"] and ["humi"] are for local sensors.
                # If you add panel_configs entries like "outdoor_temp", update them here:
                # if "outdoor_temp" in self.data_vars: self.data_vars["outdoor_temp"].set(f"{api_temp}°C")

                print(f"天气数据更新成功: {description}, 温度: {api_temp}°C, 湿度: {api_humidity}%, 风速: {wind_speed}m/s")
            except Exception as e:
                print(f"解析天气数据时出错: {e}. 数据: {str(weather_data)[:200]}")
                if "weather_desc" in self.data_vars: self.data_vars["weather_desc"].set("天气数据解析错误")
                if "wind_speed" in self.data_vars: self.data_vars["wind_speed"].set("--")
        elif not self.use_simulation : # No data and not an error, and not in simulation
            if "weather_desc" in self.data_vars: self.data_vars["weather_desc"].set("天气数据不可用")
            if "wind_speed" in self.data_vars: self.data_vars["wind_speed"].set("--")
            print("天气数据不可用 (update_weather_display)")


    def update_connection_status_display(self, is_connected, status_text=None, sim_mode=None):
        if sim_mode is None:
            sim_mode = self.use_simulation # Use current simulation mode if not specified

        if sim_mode:
            self.connection_status_var.set("状态: 模拟数据模式")
            if self.connection_status_label_widget:
                self.connection_status_label_widget.config(fg=TEXT_COLOR_STATUS_SIM)
        elif is_connected:
            self.connection_status_var.set(status_text or "MQTT状态: 已连接")
            if self.connection_status_label_widget:
                self.connection_status_label_widget.config(fg=TEXT_COLOR_STATUS_OK)
        else:
            self.connection_status_var.set(status_text or "MQTT状态: 连接已断开")
            if self.connection_status_label_widget:
                self.connection_status_label_widget.config(fg=TEXT_COLOR_STATUS_FAIL)
        print(f"DEBUG: Connection status updated: {self.connection_status_var.get()}")


    def update_charts(self):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            # Update Temperature Chart
            if self.ax_temp_chart and self.chart_canvas_widget_temp and self.chart_data_history['temperature']:
                self.ax_temp_chart.clear()
                
                # 分离时间和值数据
                times, temps = [], []
                if self.chart_data_history['temperature']:
                    times, temps = zip(*self.chart_data_history['temperature'])
                
                if times and temps:  # 确保有数据
                    self.ax_temp_chart.plot(times, temps, marker='o', linestyle='-', color=CHART_LINE_COLOR, markersize=3)
                    self.ax_temp_chart.set_title("温度 (°C)", color=CHART_TEXT_COLOR, fontsize=10)
                    self.ax_temp_chart.set_facecolor(CHART_BG_COLOR)
                    self.ax_temp_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_temp_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_temp_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
                    self.ax_temp_chart.spines['top'].set_color(CHART_BG_COLOR)
                    self.ax_temp_chart.spines['right'].set_color(CHART_BG_COLOR)
                    self.ax_temp_chart.spines['left'].set_color(CHART_TEXT_COLOR)
    
                    # 为Y轴添加合适的范围，避免大幅波动
                    min_temp, max_temp = min(temps), max(temps)
                    temp_range = max_temp - min_temp
                    if temp_range < 2:  # 如果范围太小，扩展视图
                        self.ax_temp_chart.set_ylim([min_temp - 1, max_temp + 1])
                    else:
                        self.ax_temp_chart.set_ylim([min_temp - 0.1 * temp_range, max_temp + 0.1 * temp_range])
    
                    # Add X and Y labels
                    self.ax_temp_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
                    self.ax_temp_chart.set_ylabel("温度 (°C)", color=CHART_TEXT_COLOR, fontsize=8)
                    # Format X-axis to show time in H:M format
                    # 使用AutoDateLocator而不是MinuteLocator，以优化时间轴显示
                    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                    formatter = mdates.DateFormatter('%H:%M')
                    self.ax_temp_chart.xaxis.set_major_locator(locator)
                    self.ax_temp_chart.xaxis.set_major_formatter(formatter)
                    # 不使用autofmt_xdate，避免性能问题
                    # self.fig_temp_chart.autofmt_xdate()
                    self.fig_temp_chart.tight_layout(pad=0.5) # Apply tight_layout after all settings
    
                    # 更新现有图表，不销毁和重建面板
                    if not hasattr(self, 'temp_chart_panel') or self.temp_chart_panel is None:
                        # 只有在需要时才创建新面板
                        self.temp_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                        self.temp_chart_panel.grid(row=0, column=0, sticky="nsew", pady=(0,5))
                        self.chart_canvas_widget_temp = FigureCanvasTkAgg(self.fig_temp_chart, master=self.temp_chart_panel)
                        self.chart_canvas_widget_temp.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
                    
                    # 只重新绘制Canvas，而不是重建整个面板
                    self.chart_canvas_widget_temp.draw()
                else:
                    print("DEBUG: 温度图表数据为空，无法更新")

            # Update Humidity Chart
            if self.ax_humi_chart and self.chart_canvas_widget_humi and self.chart_data_history['humidity']:
                self.ax_humi_chart.clear()
                
                # 分离时间和值数据
                times, humis = [], []
                if self.chart_data_history['humidity']:
                    times, humis = zip(*self.chart_data_history['humidity'])
                    
                if times and humis:  # 确保有数据
                    self.ax_humi_chart.plot(times, humis, marker='o', linestyle='-', color=CHART_LINE_COLOR, markersize=3)
                    self.ax_humi_chart.set_title("湿度 (%RH)", color=CHART_TEXT_COLOR, fontsize=10)
                    self.ax_humi_chart.set_facecolor(CHART_BG_COLOR)
                    self.ax_humi_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_humi_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_humi_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
                    self.ax_humi_chart.spines['top'].set_color(CHART_BG_COLOR)
                    self.ax_humi_chart.spines['right'].set_color(CHART_BG_COLOR)
                    self.ax_humi_chart.spines['left'].set_color(CHART_TEXT_COLOR)
                    
                    # 为Y轴添加合适的范围，避免大幅波动
                    min_humi, max_humi = min(humis), max(humis)
                    humi_range = max_humi - min_humi
                    if humi_range < 2:  # 如果范围太小，扩展视图
                        self.ax_humi_chart.set_ylim([min_humi - 1, max_humi + 1])
                    else:
                        self.ax_humi_chart.set_ylim([min_humi - 0.1 * humi_range, max_humi + 0.1 * humi_range])

                    # Add X and Y labels, remove old title
                    self.ax_humi_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
                    self.ax_humi_chart.set_ylabel("湿度 (%RH)", color=CHART_TEXT_COLOR, fontsize=8)
                    # Format X-axis to show time in H:M format
                    # 使用AutoDateLocator而不是MinuteLocator，以优化时间轴显示
                    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                    formatter = mdates.DateFormatter('%H:%M')
                    self.ax_humi_chart.xaxis.set_major_locator(locator)
                    self.ax_humi_chart.xaxis.set_major_formatter(formatter)
                    # 不使用autofmt_xdate，避免性能问题
                    # self.fig_humi_chart.autofmt_xdate()
                    self.fig_humi_chart.tight_layout(pad=0.5)

                    # 更新现有图表，不销毁和重建面板
                    if not hasattr(self, 'humi_chart_panel') or self.humi_chart_panel is None:
                        # 只有在需要时才创建新面板
                        self.humi_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                        self.humi_chart_panel.grid(row=1, column=0, sticky="nsew", pady=5)
                        self.chart_canvas_widget_humi = FigureCanvasTkAgg(self.fig_humi_chart, master=self.humi_chart_panel)
                        self.chart_canvas_widget_humi.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
                    
                    # 只重新绘制Canvas，而不是重建整个面板
                    self.chart_canvas_widget_humi.draw()
                else:
                    print("DEBUG: 湿度图表数据为空，无法更新")

            # Update Noise Chart
            if self.ax_noise_chart and self.chart_canvas_widget_noise and self.chart_data_history['noise']:
                self.ax_noise_chart.clear()
                
                # 分离时间和值数据
                times, noises = [], []
                if self.chart_data_history['noise']:
                    times, noises = zip(*self.chart_data_history['noise'])
                    
                if times and noises:  # 确保有数据
                    self.ax_noise_chart.plot(times, noises, marker='o', linestyle='-', color=CHART_LINE_COLOR, markersize=3)
                    self.ax_noise_chart.set_title("噪音 (dB)", color=CHART_TEXT_COLOR, fontsize=10)
                    self.ax_noise_chart.set_facecolor(CHART_BG_COLOR)
                    self.ax_noise_chart.tick_params(axis='x', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_noise_chart.tick_params(axis='y', colors=CHART_TEXT_COLOR, labelsize=8)
                    self.ax_noise_chart.spines['bottom'].set_color(CHART_TEXT_COLOR)
                    self.ax_noise_chart.spines['top'].set_color(CHART_BG_COLOR)
                    self.ax_noise_chart.spines['right'].set_color(CHART_BG_COLOR)
                    self.ax_noise_chart.spines['left'].set_color(CHART_TEXT_COLOR)
                    
                    # 为Y轴添加合适的范围，避免大幅波动
                    min_noise, max_noise = min(noises), max(noises)
                    noise_range = max_noise - min_noise
                    if noise_range < 2:  # 如果范围太小，扩展视图
                        self.ax_noise_chart.set_ylim([min_noise - 1, max_noise + 1])
                    else:
                        self.ax_noise_chart.set_ylim([min_noise - 0.1 * noise_range, max_noise + 0.1 * noise_range])
                    
                    # Add X and Y labels, remove old title
                    self.ax_noise_chart.set_xlabel("时间", color=CHART_TEXT_COLOR, fontsize=8)
                    self.ax_noise_chart.set_ylabel("噪音 (dB)", color=CHART_TEXT_COLOR, fontsize=8)
                    # Format X-axis to show time in H:M format
                    # 使用AutoDateLocator而不是MinuteLocator，以优化时间轴显示
                    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                    formatter = mdates.DateFormatter('%H:%M')
                    self.ax_noise_chart.xaxis.set_major_locator(locator)
                    self.ax_noise_chart.xaxis.set_major_formatter(formatter)
                    # 不使用autofmt_xdate，避免性能问题
                    # self.fig_noise_chart.autofmt_xdate()
                    self.fig_noise_chart.tight_layout(pad=0.5)
                    
                    # 更新现有图表，不销毁和重建面板
                    if not hasattr(self, 'noise_chart_panel') or self.noise_chart_panel is None:
                        # 只有在需要时才创建新面板
                        self.noise_chart_panel = tk.Frame(self.charts_frame, bg=CHART_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
                        self.noise_chart_panel.grid(row=2, column=0, sticky="nsew", pady=(5,0))
                        self.chart_canvas_widget_noise = FigureCanvasTkAgg(self.fig_noise_chart, master=self.noise_chart_panel)
                        self.chart_canvas_widget_noise.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
                    
                    # 只重新绘制Canvas，而不是重建整个面板
                    self.chart_canvas_widget_noise.draw()
                else:
                    print("DEBUG: 噪音图表数据为空，无法更新")
            
            # print("DEBUG: Charts updated")
        except Exception as e:
            print(f"更新图表时出错: {e}")

    def update_ai_advice(self):
        if not self.ai_advice_text_widget:
            return

        advice = "AI建议:\n"
        try:
            temp_str = self.data_vars.get("temp", tk.StringVar(value="--")).get()
            humi_str = self.data_vars.get("humi", tk.StringVar(value="--")).get()
            aqi_str = self.data_vars.get("aqi", tk.StringVar(value="--")).get()
            eco2_str = self.data_vars.get("eco2", tk.StringVar(value="--")).get()

            # Temperature advice
            if temp_str != "--":
                temp = float(temp_str)
                if temp > 30: advice += "- 温度较高 ({:.1f}°C)，注意防暑降温。\n".format(temp)
                elif temp < 10: advice += "- 温度较低 ({:.1f}°C)，注意保暖。\n".format(temp)
                else: advice += "- 温度适宜 ({:.1f}°C)。\n".format(temp)
            
            # Humidity advice
            if humi_str != "--":
                humi = float(humi_str)
                if humi > 70: advice += "- 湿度较高 ({:.1f}%)，注意通风防潮。\n".format(humi)
                elif humi < 30: advice += "- 湿度较低 ({:.1f}%)，注意保湿。\n".format(humi)
            
            # AQI advice
            if aqi_str != "--":
                aqi = int(aqi_str)
                if aqi > 100: advice += f"- 空气质量指数 (AQI: {aqi}) 略高，敏感人群减少户外活动。\n"
                elif aqi > 50: advice += f"- 空气质量良好 (AQI: {aqi})。\n"
                else: advice += f"- 空气质量优 (AQI: {aqi})。\n"

            # eCO2 advice
            if eco2_str != "--":
                eco2 = int(eco2_str)
                if eco2 > 1000: advice += f"- eCO2浓度 ({eco2} ppm) 偏高，建议通风换气。\n"
            
            if advice == "AI建议:\n": # No specific advice generated
                advice += "- 当前各项环境指标良好。"

        except ValueError:
            advice += "- 部分数据格式错误，无法生成完整建议。"
        except Exception as e:
            advice += f"- 生成建议时出错: {e}"

        self.ai_advice_text_widget.config(state=tk.NORMAL)
        self.ai_advice_text_widget.delete(1.0, tk.END)
        self.ai_advice_text_widget.insert(tk.END, advice)
        self.ai_advice_text_widget.config(state=tk.DISABLED)
        # print("DEBUG: AI advice updated.")

    def on_closing(self):
        print("关闭应用程序...")
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            # self.mqtt_client.disconnect() # disconnect() can sometimes block or cause issues on immediate exit
            print("MQTT客户端已停止。")
        
        # Cancel all .after jobs
        # This requires keeping track of after_ids or iterating through them,
        # which is complex. Tkinter usually handles this on destroy.
        # For a simple approach, just destroy the root window.
        
        self.root.quit() # Stops the Tkinter mainloop
        self.root.destroy() # Destroys the window and cleans up widgets
        print("应用程序已退出。")

# Global update_time function is removed as it's now a method: self.update_time_display

if __name__ == "__main__":
    print("DEBUG: __main__ block started")
    
    # Attempt to set locale for Chinese day names
    # Store original locale to revert if needed, though for app exit it might not matter.
    original_locale_time = locale.getlocale(locale.LC_TIME)
    try:
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
    except locale.Error:
        print("警告: 无法设置中文区域设置 (zh_CN.UTF-8)。尝试其他中文区域设置...")
        try:
            locale.setlocale(locale.LC_TIME, 'Chinese_China.936') # Windows specific
        except locale.Error:
            print("警告: 无法设置 'Chinese_China.936'。星期几可能以默认语言显示。")
            # Revert to original if zh_CN fails, to avoid leaving it in an invalid state
            locale.setlocale(locale.LC_TIME, original_locale_time)


    root = tk.Tk()
    root.geometry("1280x768") # Set a default size
    root.configure(bg=PAGE_BG_COLOR)
    
    app = SmartCampusDashboard(root) # This handles all setup including MQTT
    
    print("DEBUG: Starting Tkinter mainloop...")
    root.mainloop()
    print("DEBUG: Tkinter mainloop finished.")
    
    # Revert locale if it was changed, though after mainloop this is mostly for cleanup
    try:
        locale.setlocale(locale.LC_TIME, original_locale_code=original_locale_time)
    except Exception:
        pass # Ignore errors during final cleanup
