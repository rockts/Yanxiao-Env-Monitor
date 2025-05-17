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
from tkinter import ttk, font
import paho.mqtt.client as mqtt
import requests
import json
import time
import socket # For MQTT connection error handling and general networking
import base64 # 新增：用于Basic Authentication
import urllib.parse # 新增：用于URL编码Topic
import cv2
import threading
import os
from datetime import datetime
from collections import deque # 用于存储历史数据
import io # Required for image data handling
import locale # Added for Chinese day of the week
from matplotlib.figure import Figure

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
last_weather_fetch_time = 0 # 新增：初始化上次天气获取时间

# --- UI Update Intervals ---
GUI_UPDATE_INTERVAL_MS = 1000 # 界面刷新间隔（毫秒），原为5000，改为1000以更快地看到调试输出

# --- MQTT Configuration ---
SIOT_SERVER_HTTP = "http://192.168.1.129:8080" # 保留HTTP服务器地址用于可能的其他功能
SIOT_USERNAME = "siot"
SIOT_PASSWORD = "dfrobot"

# MQTT 配置
MQTT_BROKER_HOST = "192.168.1.129"
MQTT_BROKER_PORT = 1883
MQTT_CAMERA_TOPIC = "siot/摄像头" # New topic for camera
MQTT_TOPICS = [
    "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
    "siot/紫外线指数", "siot/uv风险等级", "siot/噪音", MQTT_CAMERA_TOPIC # Added camera topic
] # 添加 "siot/" 前缀
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

# --- Global UI References & StringVars ---
root = None
time_var = None
# temp_var, humi_var, etc. are no longer initialized as StringVars here at module level directly if managed by data_vars
# They can be declared as None if needed for other non-StringVar global uses, or removed if exclusively via data_vars
temp_var = None 
humi_var = None
aqi_var = None
tvoc_var = None
eco2_var = None
uv_index_var = None
uv_risk_var = None
noise_var = None

connection_status_var = None
connection_status_label_widget = None # To change fg color
sim_button_widget = None # To change bg color
sim_button_text_var = None
ai_advice_var = None # Will be removed
data_vars = {} # Stores StringVars for sensor values: data_vars["temp"], data_vars["humi"] etc.
video_image_label = None # Label to display video/image
video_photo_image = None # To keep a reference to the PhotoImage
_debug_video_update_counter = 0 # 新增：调试计数器
ai_advice_text_widget = None # Added for direct Text widget update
app = None # 全局应用实例

# Weather StringVars - These will be deprecated in favor of data_vars entries
# weather_desc_var = None
# wind_speed_var = None

# --- Chart Specific Globals ---
TEMP_HISTORY_MAXLEN = 50
HUMI_HISTORY_MAXLEN = 50
NOISE_HISTORY_MAXLEN = 50 # Renamed from AQI_HISTORY_MAXLEN

temp_history = deque(maxlen=TEMP_HISTORY_MAXLEN)
humi_history = deque(maxlen=HUMI_HISTORY_MAXLEN) # New history for humidity
noise_history = deque(maxlen=NOISE_HISTORY_MAXLEN)   # Renamed from aqi_history

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
    "weather_desc": {"base_topic_name": "weather_api_desc", "display_title": "天气状况", "unit": "", "icon": "☁️"}, # Moved
    "wind_speed": {"base_topic_name": "weather_api_wind", "display_title": "风速", "unit": "m/s", "icon": "🌬️"},  # Moved
    "humi": {"base_topic_name": "环境湿度", "display_title": "环境湿度", "unit": "%RH", "icon": "💧"},
    "aqi": {"base_topic_name": "aqi", "display_title": "AQI", "unit": "", "icon": "💨"},
    "eco2": {"base_topic_name": "eco2", "display_title": "eCO2", "unit": "ppm", "icon": "🌿"},
    "tvoc": {"base_topic_name": "tvoc", "display_title": "TVOC", "unit": "ppb", "icon": "🧪"},
    "uv": {"base_topic_name": "紫外线指数", "display_title": "紫外线指数", "unit": "", "icon": "☀️"},
    "noise": {"base_topic_name": "噪音", "display_title": "噪音", "unit": "dB", "icon": "🔊"},
    "uvl": {"base_topic_name": "uv风险等级", "display_title": "UV风险等级", "unit": "", "icon": "🛡️"}
}
# Order of panels in the grid - this might become dynamic or less relevant if left panel shows all
# panel_order = ["eco2", "tvoc", "uv", "noise", "uvl"] # Original for reference

# --- UI Creation Functions ---
def create_header_section(parent_frame):
    # Per attachment, this is empty. If completion was intended, it's not reflected.
    # Keeping as is from attachment.
    pass

def create_main_layout(parent_frame):
    global main_regions_frame, data_vars, panel_configs, sim_button_text_var, connection_status_label_widget, APP_VERSION
    # Assuming UI constants like PAGE_BG_COLOR, PANEL_BG_COLOR, etc., are defined at the module level.

    print("DEBUG: create_main_layout called - restoring left panel and applying grid weights")

    main_regions_frame = tk.Frame(parent_frame, bg="yellow", bd=2, relief="solid") # Diagnostic
    main_regions_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    main_regions_frame.grid_columnconfigure(0, weight=3) # Left panel wider
    main_regions_frame.grid_columnconfigure(1, weight=2) # Middle panel
    main_regions_frame.grid_columnconfigure(2, weight=2) # Right panel
    main_regions_frame.grid_rowconfigure(0, weight=1)    # All regions in one row

    # --- Left Region (Data Panels) ---
    # Using a less obtrusive diagnostic color or actual intended color
    left_region_frame = tk.Frame(main_regions_frame, bg="lightgrey", padx=5, pady=5) 
    left_region_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
    
    # Make left_region_frame itself responsive if it contains elements that should expand
    # For now, data_panels_container is packed with expand=False, fill='x'
    # bottom_info_frame is packed with fill='x'
    # So left_region_frame's height will be determined by its content, width by grid.

    data_panels_container = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR) 
    data_panels_container.pack(expand=False, fill='x', anchor='n')
    
    left_panel_keys = list(panel_configs.keys())
    
    for key in left_panel_keys:
        if key not in panel_configs:
            print(f"警告: left_panel_keys 中的键 '{key}' 在 panel_configs 中未找到。")
            continue
        
        config = panel_configs[key]
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
    
        if key in data_vars and data_vars[key] is not None:
            value_label = tk.Label(value_unit_frame, textvariable=data_vars[key], font=FONT_PANEL_VALUE, fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
            value_label.pack(side="left", anchor="s")
        else:
            tk.Label(value_unit_frame, text="--", font=FONT_PANEL_VALUE, fg="red", bg=PANEL_BG_COLOR).pack(side="left", anchor="s")
            print(f"DEBUG: data_vars missing or None for key: {key} in create_main_layout")
    
        if unit:
            unit_label = tk.Label(value_unit_frame, text=unit, font=FONT_PANEL_UNIT, fg=TEXT_COLOR_UNIT, bg=PANEL_BG_COLOR)
            unit_label.pack(side="left", anchor="s", padx=(3,0), pady=(0,3))
            
    # --- Version, Simulation Button, and Connection Status (Bottom of Left Region) ---
    bottom_info_frame = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR) 
    bottom_info_frame.pack(side=tk.BOTTOM, fill="x", pady=(10,0), padx=5)
    
    version_label = tk.Label(bottom_info_frame, text=f"版本: {APP_VERSION}", font=FONT_STATUS, fg=TEXT_COLOR_VERSION, bg=PAGE_BG_COLOR, bd=0)
    version_label.pack(side="left", padx=(10, 5))
    
    sim_button_widget = tk.Button(bottom_info_frame, textvariable=sim_button_text_var, font=FONT_STATUS, fg=TEXT_COLOR_STATUS_SIM, bg=PANEL_BG_COLOR,
                                  activebackground=PANEL_BG_COLOR, bd=0, highlightthickness=0, command=toggle_simulation)
    sim_button_widget.pack(side="left", padx=5)
    
    if connection_status_label_widget is None:
        connection_status_label_widget = tk.Label(bottom_info_frame, text="连接状态: 初始化...", font=FONT_STATUS, fg=TEXT_COLOR_STATUS_FAIL, bg=PAGE_BG_COLOR)
    else: 
        connection_status_label_widget.pack_forget()
        connection_status_label_widget.master = bottom_info_frame
        # Ensure all relevant properties are set, especially if it was configured for a different parent/style before
        connection_status_label_widget.config(text=connection_status_var.get(), font=FONT_STATUS, bg=PAGE_BG_COLOR)
        # Foreground color will be set by update_connection_status
    connection_status_label_widget.pack(side="right", padx=(0, 10))
    # update_connection_status(mqtt_client.is_connected() if mqtt_client else False) # Initial update based on current status if possible
            
    # # --- Middle Region (Video Top, AI Bottom) ---
    # middle_region_frame = tk.Frame(main_regions_frame, bg="green", padx=5, pady=5, highlightbackground="green", highlightthickness=2) # DIAGNOSTIC
    # middle_region_frame.grid(row=0, column=1, sticky="nsew", padx=5)
    # middle_region_frame.grid_rowconfigure(0, weight=4)
    # middle_region_frame.grid_rowconfigure(1, weight=1)
    # middle_region_frame.grid_columnconfigure(0, weight=1)
    #
    # video_outer_frame = tk.Frame(middle_region_frame, bg=VIDEO_BG_COLOR,
    #                              highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # video_outer_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
    # tk.Label(video_outer_frame, text="实时监控视频", font=FONT_PANEL_TITLE, fg=TEXT_COLOR_PANEL_TITLE, bg=VIDEO_BG_COLOR).pack(anchor="nw", padx=10, pady=5)
    # 
    # if video_image_label is None:
    #     video_image_label = tk.Label(video_outer_frame, bg=VIDEO_BG_COLOR)
    # for widget in video_outer_frame.winfo_children():
    #     if isinstance(widget, tk.Label) and widget.cget("text") == "无可用视频源":
    #         widget.destroy()
    #
    # video_image_label.pack(expand=True, fill="both")
    #
    # ai_advice_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR, pady=5, padx=10,
    #                            highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # ai_advice_frame.grid(row=1, column=0, sticky="nsew", pady=(5,0))
    #
    # tk.Label(ai_advice_frame, text="AI建议", font=FONT_AI_SECTION_TITLE, fg=TEXT_COLOR_AI_TITLE, bg=PANEL_BG_COLOR).pack(anchor="nw", padx=10, pady=5)
    #
    # ai_advice_text_widget = tk.Text(ai_advice_frame, height=5, wrap=tk.WORD, bg=PANEL_BG_COLOR, fg=TEXT_COLOR_AI_ADVICE,
    #                          font=FONT_AI_ADVICE, bd=0, highlightthickness=0)
    # ai_advice_text_widget.pack(expand=True, fill="both", padx=10, pady=(0,5))
    # ai_advice_text_widget.insert(tk.END, "欢迎使用智慧校园环境监测系统")
    #
    # # --- Right Region (Status, Controls) ---
    # right_region_frame = tk.Frame(main_regions_frame, bg="blue", padx=5, pady=5, highlightbackground="blue", highlightthickness=2) # DIAGNOSTIC
    # right_region_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0)) 
    #
    # charts_frame = tk.Frame(right_region_frame, bg=PAGE_BG_COLOR) 
    # charts_frame.pack(expand=True, fill="both", pady=10, padx=5)
    #
    # charts_frame.grid_rowconfigure(0, weight=1)
    # charts_frame.grid_rowconfigure(1, weight=1)
    # charts_frame.grid_rowconfigure(2, weight=1)
    # charts_frame.grid_columnconfigure(0, weight=1)
    #
    # # Temperature Chart Panel
    # temp_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # temp_chart_panel.grid(row=0, column=0, sticky="nsew", pady=(0,5))
    # # ... (chart setup) ...
    # chart_canvas_widget_temp.draw()
    #
    # # Humidity Chart Panel
    # humi_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # humi_chart_panel.grid(row=1, column=0, sticky="nsew", pady=5)
    # # ... (chart setup) ...
    # chart_canvas_widget_humi.draw()
    #
    # # Noise Chart Panel
    # noise_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # noise_chart_panel.grid(row=2, column=0, sticky="nsew", pady=5)
    # # ... (chart setup) ...
    # chart_canvas_widget_noise.draw()
    #
    # # --- Bottom Spacer ---
    # bottom_spacer = tk.Frame(parent_frame, bg=PAGE_BG_COLOR, height=10) 
    # bottom_spacer.pack(fill="x") 

    # --- Bindings ---
    # parent_frame.bind("<Configure>", lambda e: on_resize(e, main_regions_frame))

    print("DEBUG: create_main_layout finished - left panel restored, middle/right still commented")
    return main_regions_frame

def on_resize(event, main_regions_frame):
    # This function will be called whenever the parent frame is resized
    print("DEBUG: on_resize called - event:", event)
    try:
        # If an image is set, the label's size is dictated by the image.
        # The pack(expand=True, fill="both") should handle centering.
        # Explicitly setting width/height here in text units or conflicting pixels might not be ideal.
        if video_image_label and video_photo_image:
            # print(f"DEBUG: (on_resize) video_image_label has an image. Current image size: {video_photo_image.width()}x{video_photo_image.height()}")
            pass # Image size is fixed by handle_camera_stream_update for now
        elif video_image_label:
            # print("DEBUG: (on_resize) video_image_label has no image, it's a colored background.")
            pass
    except Exception as e:
        print(f"ERROR in on_resize: {type(e).__name__} - {e}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"DEBUG: MQTT on_connect called with rc: {rc}, flags: {flags}, properties: {properties}")
    if rc == 0:
        print("MQTT连接成功，状态码：", rc)
        update_connection_status(True)
        print("DEBUG: Attempting to subscribe to topics...")
        subscribe_to_topics()
        # Reset simulation data usage flag
        global use_simulation, data_vars, panel_configs

        was_simulation_active = use_simulation 
        use_simulation = False 

        if was_simulation_active:
            print("DEBUG: MQTT connected, was in simulation mode. Clearing sensor data for real values.")
            for p_key, config in panel_configs.items():
                # Only clear data that comes from MQTT, not weather API specific keys if any are distinct
                if config.get("base_topic_name") and not config.get("base_topic_name").startswith("weather_api_"):
                    if p_key in data_vars: # Check if the key exists in data_vars
                        data_vars[p_key].set("--") # Reset to default
        
        # Update UI to reflect real data mode
        update_ui()
    else:
        print(f"MQTT连接失败，状态码：{rc}")
        update_connection_status(False)


def on_disconnect(client, userdata, rc, properties=None): # Added properties for consistency
    print(f"MQTT连接断开，状态码：{rc}, properties: {properties}")
    update_connection_status(False)

def on_message(client, userdata, msg):
    # print(f"DEBUG: MQTT on_message received. Topic: {msg.topic}, Payload: '{msg.payload.decode('utf-8')[:100]}...'")
    # Assuming 'app' is the global instance of SmartCampusDashboard
    if app is None:
        print("ERROR: 'app' instance is None in on_message. Cannot update UI.")
        return

    payload_str = ""
    try:
        payload_str = msg.payload.decode('utf-8')
        payload_preview = payload_str[:100]
        print(f"DEBUG: MQTT on_message. Topic: {msg.topic}, Payload: '{payload_preview}...'")

        topic_str = msg.topic

        if topic_str == MQTT_CAMERA_TOPIC:
            try:
                image_data_b64 = None
                # 首先尝试直接使用payload_str
                if payload_str.startswith("data:image"):
                    if ',' in payload_str:
                        image_data_b64 = payload_str.split(',', 1)[1]
                    else:
                        image_data_b64 = payload_str
                else:
                    # 尝试解析JSON
                    try:
                        # 先尝试标准JSON解析
                        json_data = json.loads(payload_str)
                        if isinstance(json_data, dict) and "image" in json_data:
                            image_data_b64 = json_data["image"]
                        else:
                            # 处理可能的格式问题
                            payload_str = payload_str.strip()
                            if payload_str.startswith('{') and payload_str.endswith('}'):
                                # 清理可能的无效JSON字符
                                cleaned_payload = payload_str.replace('\n', '').replace('\r', '')
                                try:
                                    json_data = json.loads(cleaned_payload)
                                    if isinstance(json_data, dict) and "image" in json_data:
                                        image_data_b64 = json_data["image"]
                                    else:
                                        print(f"JSON格式正确但缺少'image'键: {cleaned_payload[:100]}")
                                except:
                                    print(f"清理后仍无法解析JSON: {cleaned_payload[:100]}")
                            else:
                                print(f"不是有效的JSON格式: {payload_str[:100]}")
                    except json.JSONDecodeError as json_err:
                        print(f"JSON解析错误: {json_err}. 尝试直接使用payload作为图像数据")
                        # 如果JSON解析失败，尝试将整个payload作为base64图像数据
                        if len(payload_str) > 100:  # 简单检查是否可能是base64数据
                            image_data_b64 = payload_str

                if image_data_b64:
                    # Schedule the UI update on the main thread
                    app.root.after(0, app.update_camera_stream, {"image": image_data_b64})
                else:
                    print(f"无法从payload中提取base64图像数据, 主题: {topic_str}. Payload: {payload_str[:100]}")

            except Exception as e:
                print(f"处理摄像头数据时出错, 主题 {topic_str}: {type(e).__name__} - {e}. Payload: {payload_str[:100]}")
            return

        # For other sensor topics:
        try:
            data = json.loads(payload_str)
            # Schedule the UI update on the main thread
            app.root.after(0, app.update_sensor_data, topic_str, data)
        except json.JSONDecodeError:
            print(f"主题 {topic_str} payload不是有效的JSON. Payload: {payload_str}. 将作为原始字符串转发.")
            app.root.after(0, app.update_sensor_data, topic_str, payload_str)
        except Exception as e:
            print(f"处理数据时出错, 主题 {topic_str}: {type(e).__name__} - {e}. Payload: {payload_str}")

    except UnicodeDecodeError as e:
        print(f"MQTT payload解码错误, 主题 {msg.topic}: {e}. 原始payload: {msg.payload[:100]}...")
    except Exception as e:
        print(f"在on_message中出现意外错误, 主题 {msg.topic}: {type(e).__name__} - {e}. Payload (如已解码): '{payload_str[:100]}...'")

def update_connection_status(connected):
    global connection_status_var, connection_status_label_widget
    if connection_status_var: # Check if connection_status_var itself is initialized
        if connected:
            connection_status_var.set("已连接")
            if connection_status_label_widget: # ADD THIS CHECK
                connection_status_label_widget.config(fg=TEXT_COLOR_STATUS_OK)
        else:
            connection_status_var.set("未连接")
            if connection_status_label_widget: # ADD THIS CHECK
                connection_status_label_widget.config(fg=TEXT_COLOR_STATUS_FAIL)
    # else:
    #     print("DEBUG: connection_status_var is None in update_connection_status") # Should not happen

def subscribe_to_topics():
    try:
        for topic in MQTT_TOPICS:
            mqtt_client.subscribe(topic)
            print(f"DEBUG: Subscribed to topic: {topic}")
        print("DEBUG: All topics subscribed.")
    except Exception as e:
        print("订阅主题时发生错误:", e)

def update_sensor_data(data): # data is from json.loads(payload) or constructed in on_message
    global mqtt_data_cache, data_vars, panel_configs, use_simulation
    # print(f"DEBUG: update_sensor_data called. Simulation mode: {use_simulation}. Received data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

    if use_simulation: 
        print("DEBUG: In simulation mode, MQTT sensor data update skipped.")
        return

    # 这部分仅在 use_simulation 为 False 时运行
    print(f"DEBUG: update_sensor_data (real data mode). Received data: {data}")

    if not isinstance(data, dict):
        print(f"ERROR: update_sensor_data expects a dictionary, but received {type(data)}: {data}")
        return

    for p_key, config in panel_configs.items():
        base_topic_name = config.get("base_topic_name")
        # Check if this base_topic_name (e.g., "环境温度") is a key in the received MQTT data
        if base_topic_name and base_topic_name in data:
            value = str(data[base_topic_name]) # Ensure value is a string for StringVar
            
            full_mqtt_topic_key = f"siot/{base_topic_name}" 
            
            if full_mqtt_topic_key in mqtt_data_cache: # Check if it's a topic we generally track
                 mqtt_data_cache[full_mqtt_topic_key] = value
            
            if p_key in data_vars:
                data_vars[p_key].set(value)
                print(f"DEBUG: Updated data_vars['{p_key}'] to '{value}' from MQTT key '{base_topic_name}'")
            # else:
            #     print(f"DEBUG: p_key '{p_key}' not in data_vars, though base_topic_name '{base_topic_name}' was in MQTT data.")

def fetch_weather_data():
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status() # Raise an error for bad responses
        weather_data = response.json()

        # Extract relevant fields - update keys based on actual API response structure
        description = weather_data.get("weather", [{}])[0].get("description", "")
        temperature = weather_data.get("main", {}).get("temp", "")
        humidity = weather_data.get("main", {}).get("humidity", "")
        wind_speed = weather_data.get("wind", {}).get("speed", "")

        # Update the UI directly with the fetched values
        if "weather_desc" in data_vars:
            data_vars["weather_desc"].set(description)
        # if "temp" in data_vars: # Removed to avoid conflict with MQTT sensor temp
        #     data_vars["temp"].set(temperature)
        # if "humi" in data_vars: # Removed to avoid conflict with MQTT sensor humi
        #     data_vars["humi"].set(humidity)
        if "wind_speed" in data_vars:
            data_vars["wind_speed"].set(wind_speed)

        print("天气数据更新成功")
    except requests.exceptions.RequestException as e:
        print("天气数据请求错误:", e)
    except Exception as e:
        print("处理天气数据时发生错误:", e)

def start_weather_fetch_loop():
    def loop():
        while True:
            try:
                # Calculate time since last fetch
                time_since_last_fetch = time.time() - last_weather_fetch_time
                # If it's time to fetch new data
                if time_since_last_fetch >= WEATHER_FETCH_INTERVAL:
                    print("定时获取天气数据...")
                    fetch_weather_data()
                else:
                    print(f"天气数据更新中，距离下次更新还有 {WEATHER_FETCH_INTERVAL - time_since_last_fetch} 秒")
            except Exception as e:
                print("天气数据循环获取时发生错误:", e)
            # Sleep for a while before next check
            time.sleep(60) # Check every minute

    # Start the loop in a new thread
    threading.Thread(target=loop, daemon=True).start()

def toggle_simulation():
    global use_simulation, sim_button_text_var, data_vars, panel_configs, simulation_data
    use_simulation = not use_simulation
    if use_simulation:
        sim_button_text_var.set("禁用模拟数据")
        for p_key, config in panel_configs.items():
            base_topic_name = config.get("base_topic_name")
            if p_key in data_vars:
                if base_topic_name and base_topic_name in simulation_data:
                    data_vars[p_key].set(str(simulation_data[base_topic_name]))
                else: # For panel_config keys not in simulation_data (e.g., weather)
                    data_vars[p_key].set("--")
        print("模拟数据已启用")
    else:
        sim_button_text_var.set("启用模拟数据")
        for p_key in data_vars.keys(): # Reset all to "--"
            data_vars[p_key].set("--")
        print("模拟数据已禁用")
        # Optionally, trigger real data fetching
        fetch_weather_data() # Fetch weather when disabling simulation
        # MQTT data will flow naturally if connected.

def update_ui():
    # This function updates parts of the UI not directly tied to StringVars auto-update
    print("DEBUG: update_ui called")
    global ai_advice_text_widget, use_simulation # Added ai_advice_text_widget
    try:
        # Update AI advice section
        if ai_advice_text_widget:
            ai_advice_text_widget.delete('1.0', tk.END) # Clear existing text
            if use_simulation:
                ai_advice_text_widget.insert(tk.END, "当前为模拟数据，实际数据可能有所不同。")
            else:
                # Basic AI advice, can be expanded based on data_vars values
                ai_advice_text_widget.insert(tk.END, "环境参数监测中...")
        
        # TODO: Add calls to update chart data and redraw them
        # e.g., update_temperature_chart(), update_humidity_chart(), update_noise_chart()
        # These functions would read from data_vars, append to history deques, and call canvas.draw()

        print("UI更新成功 (AI advice and potentially charts in future)")
    except Exception as e:
        print("更新UI时发生错误:", e)

def handle_camera_stream_update(data):
    global video_photo_image, _debug_video_update_counter

    _debug_video_update_counter += 1 # Increment for every call attempt

    if not PIL_AVAILABLE:
        if _debug_video_update_counter % 50 == 1: # Print less frequently if PIL is not there
             print("DEBUG: Pillow (PIL) not available, cannot process video stream.")
        return

    try:
        if _debug_video_update_counter % 5 == 1:
            print(f"DEBUG: handle_camera_stream_update called (call #{_debug_video_update_counter}). Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

        if "image" in data:
            image_data_b64 = data["image"]
            
            if not image_data_b64:
                if _debug_video_update_counter % 10 == 1:
                    print("DEBUG: 'image' key present but data is empty.")
                return

            if _debug_video_update_counter % 5 == 1:
                print(f"DEBUG: image_data_b64 (first 64 chars): {image_data_b64[:64]}")
            
            image_bytes = base64.b64decode(image_data_b64)
            if _debug_video_update_counter % 5 == 1:
                print(f"DEBUG: Decoded image_bytes length: {len(image_bytes)}")
            
            img_io = io.BytesIO(image_bytes)
            image = Image.open(img_io)
            if _debug_video_update_counter % 5 == 1:
                print(f"DEBUG: Image opened: mode={image.mode}, size={image.size}, format={image.format}")
            
            target_width = 400 # Reduced width
            target_height = 300 # Reduced height (maintaining 4:3 ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            if _debug_video_update_counter % 5 == 1:
                print(f"DEBUG: Image resized to: {image.size}")

            video_photo_image = ImageTk.PhotoImage(image)
            if _debug_video_update_counter % 5 == 1:
                print("DEBUG: ImageTk.PhotoImage created successfully.")

            if video_image_label:
                video_image_label.config(image=video_photo_image, width=target_width, height=target_height)
                video_image_label.image = video_photo_image 
                if _debug_video_update_counter % 10 == 1: # Less frequent success message
                    print("DEBUG: video_image_label updated with new image.")
            else:
                if _debug_video_update_counter % 5 == 1:
                    print("DEBUG: video_image_label is None, cannot update.")
        else:
            if _debug_video_update_counter % 10 == 1: # Print less frequently if key is missing
                print("DEBUG: No 'image' key found in camera stream data.")
    except UnidentifiedImageError as uie:
        print(f"ERROR: Pillow UnidentifiedImageError - Cannot identify image file. Is the base64 data a valid image? Details: {uie}")
    except base64.binascii.Error as b64_error:
        print(f"ERROR: Base64 decoding error: {b64_error}. Is the image data correctly base64 encoded?")
    except OSError as ose:
        # This can catch issues like "decoder ... not available"
        print(f"ERROR: Pillow OSError in handle_camera_stream_update: {ose}")
        if "decoder" in str(ose) and "not available" in str(ose):
            print("ERROR DETAIL: Pillow decoder issue. This often means Pillow or its dependencies (like libjpeg for JPEG images) are not correctly installed or found.")
    except Exception as e:
        print(f"ERROR in handle_camera_stream_update: {type(e).__name__} - {e}")

def update_time(): # ADDED FUNCTION
    global time_var, root
    if time_var and root: # Ensure time_var and root are initialized
        now = datetime.now().strftime("%Y-%m-%d %A %H:%M:%S") # A for full day name
        time_var.set(now)
        root.after(1000, update_time) # Schedule next update

class SmartCampusDashboard:
    def __init__(self, root):
        self.root = root
        self.camera_image_label = None # Initialize in __init__
        self.setup_left_panel() # Call setup_left_panel which will create the label

        # Ensure MQTT client is stopped when the window is closed
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_sensor_data(self, topic, data):
        """处理从MQTT接收到的传感器数据"""
        global data_vars, panel_configs, use_simulation
        print(f"DEBUG: SmartCampusDashboard.update_sensor_data called. Topic: {topic}, Data type: {type(data)}")

        if use_simulation:
            print("DEBUG: 在模拟模式下，忽略MQTT传感器数据更新。")
            return

        try:
            # 如果是字符串，尝试将其转换为数字或其他值
            if isinstance(data, str):
                try:
                    # 尝试转换为数字
                    if data.replace('.', '', 1).isdigit():
                        parsed_data = float(data) if '.' in data else int(data)
                        data = parsed_data
                    # 检查json格式的字符串
                    elif (data.startswith('{') and data.endswith('}')) or (data.startswith('[') and data.endswith(']')):
                        try:
                            parsed_data = json.loads(data)
                            data = parsed_data
                        except json.JSONDecodeError:
                            pass  # 保持为字符串
                except ValueError:
                    pass  # 保持为字符串

            # 准备一个用于更新的数据字典
            update_data = {}
            
            # 如果是字典，处理多个值
            if isinstance(data, dict):
                update_data = data
            else:
                # 如果是单个值，从topic提取键
                topic_name = topic.split('/')[-1] if '/' in topic else topic
                update_data = {topic_name: data}
            
            # 遍历所有配置的面板
            for p_key, config in panel_configs.items():
                base_topic_name = config.get("base_topic_name", "")
                
                # 检查这个base_topic_name是否在接收到的数据中
                if base_topic_name and base_topic_name in update_data:
                    value = str(update_data[base_topic_name])  # 确保值是字符串，用于StringVar
                    
                    # 更新MQTT数据缓存
                    full_mqtt_topic_key = f"siot/{base_topic_name}"
                    if full_mqtt_topic_key in mqtt_data_cache:
                        mqtt_data_cache[full_mqtt_topic_key] = value
                    
                    # 更新对应的StringVar
                    if p_key in data_vars:
                        data_vars[p_key].set(value)
                        print(f"DEBUG: 更新data_vars['{p_key}']为'{value}'，来自MQTT键'{base_topic_name}'")

            # 触发UI更新
            update_ui()
        except Exception as e:
            print(f"在update_sensor_data处理过程中出错: {type(e).__name__} - {e}")
            
    def setup_left_panel(self):
        global main_regions_frame, data_vars, panel_configs, sim_button_text_var, connection_status_label_widget, APP_VERSION

        print("DEBUG: create_main_layout called - restoring left panel and applying grid weights")

        main_regions_frame = tk.Frame(self.root, bg="yellow", bd=2, relief="solid") # Diagnostic
        main_regions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_regions_frame.grid_columnconfigure(0, weight=3) # Left panel wider
        main_regions_frame.grid_columnconfigure(1, weight=2) # Middle panel
        main_regions_frame.grid_columnconfigure(2, weight=2) # Right panel
        main_regions_frame.grid_rowconfigure(0, weight=1)    # All regions in one row

        # --- Left Region (Data Panels) ---
        # Using a less obtrusive diagnostic color or actual intended color
        left_region_frame = tk.Frame(main_regions_frame, bg="lightgrey", padx=5, pady=5) 
        left_region_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        # Make left_region_frame itself responsive if it contains elements that should expand
        # For now, data_panels_container is packed with expand=False, fill='x'
        # bottom_info_frame is packed with fill='x'
        # So left_region_frame's height will be determined by its content, width by grid.

        data_panels_container = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR) 
        data_panels_container.pack(expand=False, fill='x', anchor='n')
        
        left_panel_keys = list(panel_configs.keys())
        
        for key in left_panel_keys:
            if key not in panel_configs:
                print(f"警告: left_panel_keys 中的键 '{key}' 在 panel_configs 中未找到。")
                continue
            
            config = panel_configs[key]
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
        
            if key in data_vars and data_vars[key] is not None:
                value_label = tk.Label(value_unit_frame, textvariable=data_vars[key], font=FONT_PANEL_VALUE, fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
                value_label.pack(side="left", anchor="s")
            else:
                tk.Label(value_unit_frame, text="--", font=FONT_PANEL_VALUE, fg="red", bg=PANEL_BG_COLOR).pack(side="left", anchor="s")
                print(f"DEBUG: data_vars missing or None for key: {key} in create_main_layout")
        
            if unit:
                unit_label = tk.Label(value_unit_frame, text=unit, font=FONT_PANEL_UNIT, fg=TEXT_COLOR_UNIT, bg=PANEL_BG_COLOR)
                unit_label.pack(side="left", anchor="s", padx=(3,0), pady=(0,3))
                
        # --- Version, Simulation Button, and Connection Status (Bottom of Left Region) ---
        bottom_info_frame = tk.Frame(left_region_frame, bg=PAGE_BG_COLOR) 
        bottom_info_frame.pack(side=tk.BOTTOM, fill="x", pady=(10,0), padx=5)
        
        version_label = tk.Label(bottom_info_frame, text=f"版本: {APP_VERSION}", font=FONT_STATUS, fg=TEXT_COLOR_VERSION, bg=PAGE_BG_COLOR, bd=0)
        version_label.pack(side="left", padx=(10, 5))
        
        sim_button_widget = tk.Button(bottom_info_frame, textvariable=sim_button_text_var, font=FONT_STATUS, fg=TEXT_COLOR_STATUS_SIM, bg=PANEL_BG_COLOR,
                                      activebackground=PANEL_BG_COLOR, bd=0, highlightthickness=0, command=toggle_simulation)
        sim_button_widget.pack(side="left", padx=5)
        
        if connection_status_label_widget is None:
            connection_status_label_widget = tk.Label(bottom_info_frame, text="连接状态: 初始化...", font=FONT_STATUS, fg=TEXT_COLOR_STATUS_FAIL, bg=PAGE_BG_COLOR)
        else: 
            connection_status_label_widget.pack_forget()
            connection_status_label_widget.master = bottom_info_frame
            # Ensure all relevant properties are set, especially if it was configured for a different parent/style before
            connection_status_label_widget.config(text=connection_status_var.get(), font=FONT_STATUS, bg=PAGE_BG_COLOR)
            # Foreground color will be set by update_connection_status
        connection_status_label_widget.pack(side="right", padx=(0, 10))
        # update_connection_status(mqtt_client.is_connected() if mqtt_client else False) # Initial update based on current status if possible
                
        # # --- Middle Region (Video Top, AI Bottom) ---
        # middle_region_frame = tk.Frame(main_regions_frame, bg="green", padx=5, pady=5, highlightbackground="green", highlightthickness=2) # DIAGNOSTIC
        # middle_region_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        # middle_region_frame.grid_rowconfigure(0, weight=4)
        # middle_region_frame.grid_rowconfigure(1, weight=1)
        # middle_region_frame.grid_columnconfigure(0, weight=1)
        #
        # video_outer_frame = tk.Frame(middle_region_frame, bg=VIDEO_BG_COLOR,
        #                              highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
        # video_outer_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        # tk.Label(video_outer_frame, text="实时监控视频", font=FONT_PANEL_TITLE, fg=TEXT_COLOR_PANEL_TITLE, bg=VIDEO_BG_COLOR).pack(anchor="nw", padx=10, pady=5)
        # 
        # if video_image_label is None:
        #     video_image_label = tk.Label(video_outer_frame, bg=VIDEO_BG_COLOR)
        # for widget in video_outer_frame.winfo_children():
        #     if isinstance(widget, tk.Label) and widget.cget("text") == "无可用视频源":
        #         widget.destroy()
    #
    # video_image_label.pack(expand=True, fill="both")
    #
    # ai_advice_frame = tk.Frame(middle_region_frame, bg=PANEL_BG_COLOR, pady=5, padx=10,
    #                            highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # ai_advice_frame.grid(row=1, column=0, sticky="nsew", pady=(5,0))
    #
    # tk.Label(ai_advice_frame, text="AI建议", font=FONT_AI_SECTION_TITLE, fg=TEXT_COLOR_AI_TITLE, bg=PANEL_BG_COLOR).pack(anchor="nw", padx=10, pady=5)
    #
    # ai_advice_text_widget = tk.Text(ai_advice_frame, height=5, wrap=tk.WORD, bg=PANEL_BG_COLOR, fg=TEXT_COLOR_AI_ADVICE,
    #                          font=FONT_AI_ADVICE, bd=0, highlightthickness=0)
    # ai_advice_text_widget.pack(expand=True, fill="both", padx=10, pady=(0,5))
    # ai_advice_text_widget.insert(tk.END, "欢迎使用智慧校园环境监测系统")
    #
    # # --- Right Region (Status, Controls) ---
    # right_region_frame = tk.Frame(main_regions_frame, bg="blue", padx=5, pady=5, highlightbackground="blue", highlightthickness=2) # DIAGNOSTIC
    # right_region_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0)) 
    #
    # charts_frame = tk.Frame(right_region_frame, bg=PAGE_BG_COLOR) 
    # charts_frame.pack(expand=True, fill="both", pady=10, padx=5)
    #
    # charts_frame.grid_rowconfigure(0, weight=1)
    # charts_frame.grid_rowconfigure(1, weight=1)
    # charts_frame.grid_rowconfigure(2, weight=1)
    # charts_frame.grid_columnconfigure(0, weight=1)
    #
    # # Temperature Chart Panel
    # temp_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # temp_chart_panel.grid(row=0, column=0, sticky="nsew", pady=(0,5))
    # # ... (chart setup) ...
    # chart_canvas_widget_temp.draw()
    #
    # # Humidity Chart Panel
    # humi_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # humi_chart_panel.grid(row=1, column=0, sticky="nsew", pady=5)
    # # ... (chart setup) ...
    # chart_canvas_widget_humi.draw()
    #
    # # Noise Chart Panel
    # noise_chart_panel = tk.Frame(charts_frame, bg=PANEL_BG_COLOR, highlightbackground=BORDER_LINE_COLOR, highlightthickness=1)
    # noise_chart_panel.grid(row=2, column=0, sticky="nsew", pady=5)
    # # ... (chart setup) ...
    # chart_canvas_widget_noise.draw()
    #
    # # --- Bottom Spacer ---
    # bottom_spacer = tk.Frame(parent_frame, bg=PAGE_BG_COLOR, height=10) 
    # bottom_spacer.pack(fill="x") 

        # --- Bindings ---
        # parent_frame.bind("<Configure>", lambda e: on_resize(e, main_regions_frame))

        print("DEBUG: create_main_layout finished - left panel restored, middle/right still commented")
        return main_regions_frame

    def update_camera_stream(self, data):
        print("DEBUG: update_camera_stream called")
        if not self.camera_image_label:
            print("DEBUG: camera_image_label is None in update_camera_stream")
            return
        try:
            image_data_b64 = data.get("image")
            if image_data_b64:
                # print(f"DEBUG: Received image data (first 100 chars): {image_data_b64[:100]}")
                image_bytes = base64.b64decode(image_data_b64)
                image = Image.open(io.BytesIO(image_bytes))
                # Resize image if necessary, e.g., to fit in the panel
                # image = image.resize((320, 240), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                self.camera_image_label.config(image=photo)
                self.camera_image_label.image = photo # Keep a reference!
                # print("DEBUG: Camera image updated on label")
            else:
                print("DEBUG: No 'image' key in data for update_camera_stream")
        except base64.binascii.Error as b64_error:
            print(f"Error decoding base64 string for camera: {b64_error}. Data (first 100 chars): {str(image_data_b64)[:100]}")
        except UnidentifiedImageError as img_error:
            print(f"Error identifying image from bytes (PIL/Pillow): {img_error}")
        except Exception as e:
            print(f"Error updating camera stream: {type(e).__name__} - {e}")

    def on_closing(self):
        print("INFO: 应用程序正在关闭。断开MQTT客户端连接。")
        try:
            global mqtt_client
            # 首先尝试停止消息循环
            if mqtt_client:
                try:
                    mqtt_client.loop_stop()
                    print("INFO: MQTT客户端消息循环已停止")
                except Exception as e:
                    print(f"停止MQTT循环时出错: {e}")
                
                # 然后尝试断开连接
                try:
                    if hasattr(mqtt_client, 'is_connected') and mqtt_client.is_connected():
                        mqtt_client.disconnect()
                        print("INFO: MQTT客户端已断开连接")
                except Exception as e:
                    print(f"断开MQTT连接时出错: {e}")
            
            # 最后销毁Tkinter窗口
            self.root.destroy()
            print("INFO: Tkinter窗口已销毁")
        except Exception as e:
            print(f"关闭应用程序时发生错误: {type(e).__name__} - {e}")
            # 如果出现错误，强制退出应用
            try:
                self.root.quit()
                print("INFO: 应用程序已通过quit()退出")
            except:
                print("警告: 无法通过常规方式退出应用程序，尝试强制销毁")
                self.root.destroy()

# Global MQTT client instance (ensure it's defined)
# client = mqtt.Client() # Or however it's initialized

# At the end of the script, ensure `app` is assigned before `root.mainloop()`
def main():
    global root, app, data_vars, sim_button_text_var, connection_status_var, time_var, mqtt_client
    
    print("DEBUG: 进入main()函数") 
    
    try:
        # 创建主窗口实例（必须在初始化 StringVar 之前）
        root = tk.Tk()
        root.title("智慧校园环境监测系统")
        
        # 初始化时间变量
        time_var = tk.StringVar(value="")
        
        # 确保 sim_button_text_var 已初始化
        sim_button_text_var = tk.StringVar(value="启用模拟数据")
        print("DEBUG: 初始化 sim_button_text_var")
        
        # 确保 connection_status_var 已初始化
        connection_status_var = tk.StringVar(value="未连接")
        print("DEBUG: 初始化 connection_status_var")
        
        # 初始化 data_vars 字典，确保所有键都存在
        for key in panel_configs.keys():
            data_vars[key] = tk.StringVar(value="--")
            print(f"DEBUG: 初始化 data_vars[{key}] = '--'")
        
        # 创建应用实例
        app = SmartCampusDashboard(root) 
        
        print("DEBUG: 执行初始天气数据获取并启动天气循环")
        update_time() # 启动时间更新
        fetch_weather_data() # 获取天气数据
        start_weather_fetch_loop() # 启动天气数据循环获取
        
        # --- MQTT 客户端设置 ---
        mqtt_client.on_connect = on_connect 
        mqtt_client.on_disconnect = on_disconnect 
        mqtt_client.on_message = on_message # 必须在app创建后分配on_message
        
        try:
            mqtt_client.username_pw_set(SIOT_USERNAME, SIOT_PASSWORD)
            print(f"DEBUG: 尝试MQTT连接到 {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
            mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            print("DEBUG: MQTT connect()已调用")
            mqtt_client.loop_start()
            print("DEBUG: MQTT loop_start()已调用")
        except Exception as e:
            print(f"连接MQTT代理或启动循环时发生错误: {e}")
            # 如果连接失败，自动启用模拟模式
            global use_simulation
            use_simulation = True
            sim_button_text_var.set("禁用模拟数据")
            print("已自动启用模拟数据模式")
        
        # --- 启动GUI ---
        print("DEBUG: 进入root.mainloop()")
        root.mainloop()
        
    except Exception as e:
        print(f"在main()函数中出现意外错误: {type(e).__name__} - {e}")
    finally:
        # 确保在任何情况下都尝试停止MQTT客户端循环
        print("DEBUG: 程序结束，清理资源")
        try:
            if mqtt_client:
                mqtt_client.loop_stop()
                print("DEBUG: MQTT循环已停止")
        except Exception as cleanup_err:
            print(f"清理MQTT客户端时出错: {cleanup_err}")

if __name__ == "__main__":
    print("DEBUG: 进入__main__块，准备调用main()")
    main()
