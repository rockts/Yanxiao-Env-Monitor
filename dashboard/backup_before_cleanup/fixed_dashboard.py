#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 修复版启动器
该脚本包含了修复版的SmartCampusDashboard，解决了原有的错误
"""

import os
import sys
import platform
import datetime
import traceback
from pathlib import Path
import logging
import tkinter as tk
from tkinter import ttk
import random
import paho.mqtt.client as mqtt
import json
import importlib.util
import threading
import time

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 修复版     ")
print("=" * 60)
print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"Python版本: {platform.python_version()}")
print(f"项目根目录: {PROJECT_ROOT}")
print()

# 确保src目录在Python路径中
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}"

# 设置日志
log_dir = PROJECT_ROOT / "logs"
if not log_dir.exists():
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)
    print(f"创建配置目录: {config_dir}")

# 确保配置文件存在
config_file = config_dir / "config.json"
if not config_file.exists():
    import json
    default_config = {
        "mqtt": {
            "broker_host": "localhost",
            "broker_port": 1883,
            "client_id": "smart_campus_dashboard",
            "username": "siot",
            "password": "dfrobot"
        },
        "logging": {
            "level": "INFO",
            "log_dir": "logs",
            "log_file_prefix": "dashboard"
        },
        "ui": {
            "window_title": "烟铺小学智慧校园环境监测系统",
            "window_size": "1280x720",
            "use_fullscreen": False,
            "update_interval": 1000
        },
        "simulator": {
            "enabled": True,
            "update_interval": 3000
        },
        "siot_server_http": "http://localhost:8080",
        "siot_username": "siot",
        "siot_password": "dfrobot",
        "mqtt_broker_host": "localhost",
        "mqtt_broker_port": 1883,
        "mqtt_client_id": "smart_campus_dashboard",
        "mqtt_topics": [
            "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
            "siot/紫外线指数", "siot/uv风险等级", "siot/噪音"
        ]
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    print(f"创建默认配置文件: {config_file}")

# 定义静态修复方法
def add_dashboard_methods():
    """向SmartCampusDashboard类添加缺失的方法"""
    from types import MethodType
    
    try:
        # 导入tkinter和日志模块
        import tkinter as tk
        
        # 从主模块导入SmartCampusDashboard类和相关常量
        main_module_path = SRC_PATH / "main.py"
        
        # 执行主模块代码，但先修改模块级别的__name__变量，防止执行主模块的if __name__ == "__main__"块
        namespace = {"__name__": "main_module", "__file__": str(main_module_path)}
        
        # 读取主模块内容
        with open(main_module_path, "r", encoding="utf-8") as f:
            main_code = f.read()
        
        # 1. 首先获取所有常量和类定义，但不执行main函数
        # 将__name__ == "__main__"块替换为pass
        main_code_modified = main_code.replace(
            'if __name__ == "__main__":', 
            'if False:  # 禁用自动执行'
        )
        
        # 执行修改后的代码
        exec(main_code_modified, namespace)
        
        # 2. 获取SmartCampusDashboard类
        SmartCampusDashboard = namespace.get("SmartCampusDashboard")
        if not SmartCampusDashboard:
            print("错误: 找不到SmartCampusDashboard类")
            return False
        
        # 获取颜色常量
        TEXT_COLOR_STATUS_OK = namespace.get("TEXT_COLOR_STATUS_OK", "#33FF99")
        TEXT_COLOR_STATUS_FAIL = namespace.get("TEXT_COLOR_STATUS_FAIL", "#FF6666")
        
        # 3. 定义缺失的方法
        def update_connection_status_display(self, connected, status_text=None):
            """更新MQTT连接状态显示"""
            try:
                if hasattr(self, 'connection_status_var'):
                    status_msg = f"状态: {'已连接' if connected else status_text if status_text else '未连接'}"
                    self.connection_status_var.set(status_msg)
                    if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                        color = TEXT_COLOR_STATUS_OK if connected else TEXT_COLOR_STATUS_FAIL
                        self.connection_status_label_widget.config(text=status_msg, fg=color)
            except Exception as e:
                print(f"更新连接状态时出错: {e}")
                if logging:
                    logging.error(f"更新连接状态显示时出错: {e}")
        
        def on_closing(self):
            """窗口关闭时的处理函数"""
            if logging:
                logging.info("应用程序正在关闭")
            try:
                if hasattr(self, 'mqtt_client') and self.mqtt_client:
                    self.mqtt_client.loop_stop()
                    self.mqtt_client.disconnect()
                    if logging:
                        logging.info("MQTT客户端已断开连接")
            except Exception as e:
                print(f"关闭MQTT连接时出错: {e}")
                if logging:
                    logging.error(f"关闭MQTT连接时出错: {e}")
            finally:
                self.root.destroy()
                if logging:
                    logging.info("应用程序已关闭")
        
        # 4. 添加方法到类
        if not hasattr(SmartCampusDashboard, 'update_connection_status_display'):
            SmartCampusDashboard.update_connection_status_display = update_connection_status_display
            print("已添加update_connection_status_display方法")
        
        if not hasattr(SmartCampusDashboard, 'on_closing'):
            SmartCampusDashboard.on_closing = on_closing
            print("已添加on_closing方法")
            
        return True
    except Exception as e:
        print(f"添加方法时出错: {e}")
        traceback.print_exc()
        return False

# 添加方法到Dashboard类
add_dashboard_methods()

# 运行仪表盘
main_module_path = SRC_PATH / "main.py"
print(f"开始运行仪表盘: {main_module_path}")

try:
    # 读取主模块内容
    with open(main_module_path, "r", encoding="utf-8") as f:
        main_code = f.read()
    
    # 执行主模块代码
    exec(main_code)
except Exception as e:
    print(f"运行仪表盘时出错: {e}")
    traceback.print_exc()
