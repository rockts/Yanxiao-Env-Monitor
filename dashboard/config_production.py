# -*- coding: utf-8 -*-
"""
生产环境配置文件
Production Configuration
"""

# 生产环境MQTT配置
MQTT_BROKER = "lot.lekee.cc"
MQTT_PORT = 1883
MQTT_USERNAME = "siot"
MQTT_PASSWORD = "dfrobot"

# API配置
DASHSCOPE_API_KEY = "sk-1515ee3c6dc74eaf9e2ba3e2c86aa87e"
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 服务器配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5052
DEBUG_MODE = False

# MQTT主题映射
TOPIC_MAP = {
    "siot/环境温度": "temperature",
    "siot/环境湿度": "humidity", 
    "siot/aqi": "aqi",
    "siot/eco2": "eco2",
    "siot/tvoc": "tvoc",
    "siot/紫外线指数": "uv_raw",
    "siot/uv风险等级": "uv_index",
    "siot/噪音": "noise",
    "siot/摄像头": "camera"
}
