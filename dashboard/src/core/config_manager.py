#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和提供应用程序配置
"""

import os
import json
import logging
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "siot_server_http": "http://192.168.1.129:8080",
    "siot_username": "siot",
    "siot_password": "dfrobot",
    "mqtt_broker_host": "127.0.0.1",
    "mqtt_broker_port": 1883,
    "mqtt_client_id": "smart_campus_dashboard_client_001",
    "mqtt_camera_topic": "sc/camera/stream",
    "mqtt_weather_topic": "sc/weather/data",
    "update_interval": 15,
    "chart_history_maxlen": 20,
    "weather_fetch_interval": 1800,
    "mqtt_topics": [
        "siot/环境温度", 
        "siot/环境湿度", 
        "siot/aqi", 
        "siot/tvoc", 
        "siot/eco2",
        "siot/紫外线指数", 
        "siot/uv风险等级", 
        "siot/噪音"
    ],
    "video_dimensions": {
        "width": 450,
        "height": 340
    },
    "panel_configs": {
        "temp": {"base_topic_name": "环境温度", "display_title": "环境温度", "unit": "°C", "icon": "🌡️"},
        "weather_desc": {"base_topic_name": "weather_api_desc", "display_title": "天气状况", "unit": "", "icon": "☁️"},
        "wind_speed": {"base_topic_name": "weather_api_wind", "display_title": "风速", "unit": "m/s", "icon": "🌬️"},
        "humi": {"base_topic_name": "环境湿度", "display_title": "环境湿度", "unit": "%RH", "icon": "💧"},
        "aqi": {"base_topic_name": "aqi", "display_title": "AQI", "unit": "", "icon": "💨"},
        "eco2": {"base_topic_name": "eco2", "display_title": "eCO2", "unit": "ppm", "icon": "🌿"},
        "tvoc": {"base_topic_name": "tvoc", "display_title": "TVOC", "unit": "ppb", "icon": "🧪"},
        "uv": {"base_topic_name": "紫外线指数", "display_title": "紫外线指数", "unit": "", "icon": "☀️"},
        "noise": {"base_topic_name": "噪音", "display_title": "噪音", "unit": "dB", "icon": "🔊"}
    }
}

class ConfigManager:
    """配置管理类，负责加载、提供和验证配置"""
    
    _instance = None
    _config = None
    _custom_config_path = None # Allow overriding the config path

    def __new__(cls, config_path: str | None = None): # Allow passing config_path during first instantiation
        """单例模式，确保全局只有一个配置管理器实例"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            if config_path: # Store custom path if provided on first call
                cls._custom_config_path = Path(config_path)
            cls._instance._load_config()
        elif config_path and Path(config_path) != cls._custom_config_path:
            # If a different config_path is provided on subsequent calls, log a warning or decide behavior
            logging.warning(f"ConfigManager already initialized. Ignoring new path '{config_path}'.")
        return cls._instance
    
    def _load_config(self):
        """从配置文件加载配置，如果失败则使用默认配置"""
        try:
            if self._custom_config_path and self._custom_config_path.exists():
                config_file_to_load = self._custom_config_path
                logging.info(f"Attempting to load custom config from: {config_file_to_load}")
            else:
                # 确定配置文件路径
                project_root = Path(__file__).resolve().parent.parent.parent # dashboard/src/core -> dashboard/src -> dashboard
                config_file_to_load = project_root / "config" / "config.json"
                logging.info(f"Attempting to load default config from: {config_file_to_load}")

            if os.path.exists(config_file_to_load):
                with open(config_file_to_load, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logging.info(f"成功加载配置文件: {config_file_to_load}")
                
                # 合并默认配置中可能缺失的配置项
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self._config:
                        self._config[key] = value
                        logging.warning(f"配置文件中缺少'{key}'，使用默认值")
            else:
                logging.warning(f"配置文件不存在: {config_file_to_load}，使用默认配置")
                self._config = DEFAULT_CONFIG.copy()
        except Exception as e:
            logging.error(f"加载配置文件时出错: {e}，使用默认配置")
            self._config = DEFAULT_CONFIG.copy()
    
    def load_from_file(self, file_path: str):
        """允许从指定文件路径加载或重新加载配置"""
        self._custom_config_path = Path(file_path)
        self._load_config() # Reload configuration
        logging.info(f"Configuration reloaded from: {file_path}")

    def get(self, key, default=None):
        """获取配置项，如果不存在则返回默认值"""
        return self._config.get(key, default)
    
    def get_mqtt_topics(self):
        """获取MQTT主题列表，确保包含摄像头和天气主题"""
        topics = self._config.get("mqtt_topics", [])
        camera_topic = self._config.get("mqtt_camera_topic")
        weather_topic = self._config.get("mqtt_weather_topic")
        
        # 确保包含摄像头和天气主题
        if camera_topic and camera_topic not in topics:
            topics.append(camera_topic)
        if weather_topic and weather_topic not in topics:
            topics.append(weather_topic)
            
        return topics
    
    def get_panel_configs(self):
        """获取面板配置"""
        return self._config.get("panel_configs", {})
    
    def get_video_dimensions(self):
        """获取视频尺寸配置"""
        dims = self._config.get("video_dimensions", {})
        return dims.get("width", 450), dims.get("height", 340)
    
    def get_all(self):
        """获取所有配置项"""
        return self._config.copy() if self._config else DEFAULT_CONFIG.copy() # Ensure return a copy
    
    def save_config(self):
        """保存当前配置到配置文件"""
        try:
            # Determine save path: custom path if used, else default path
            if self._custom_config_path:
                save_file_path = self._custom_config_path
                # Ensure directory exists for custom path
                os.makedirs(self._custom_config_path.parent, exist_ok=True)
            else:
                project_root = Path(__file__).resolve().parent.parent.parent # dashboard
                config_dir = project_root / "config"
                os.makedirs(config_dir, exist_ok=True)
                save_file_path = config_dir / "config.json"
            
            with open(save_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
            logging.info(f"配置已保存到: {save_file_path}")
            return True
        except Exception as e:
            logging.error(f"保存配置时出错: {e}")
            return False

# 导出单例实例，方便其他模块导入使用
# The instantiation of 'config' here will use the default path logic
# as no argument is passed.
config = ConfigManager()

if __name__ == "__main__":
    # 配置测试代码
    print("配置管理器测试")
    print(f"MQTT服务器: {config.get('mqtt_broker_host')}:{config.get('mqtt_broker_port')}")
    print(f"MQTT主题: {config.get_mqtt_topics()}")
    print(f"面板配置: {config.get_panel_configs()}")
