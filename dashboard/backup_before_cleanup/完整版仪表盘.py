#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 完整版启动脚本
直接启动完整版仪表盘，无需简化
"""

import os
import sys
import tkinter as tk
import traceback
import platform
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 设置项目路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

# 添加src目录到Python路径
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"

def ensure_config_exists():
    """确保配置文件存在"""
    config_dir = PROJECT_ROOT / "config"
    config_file = config_dir / "config.json"
    
    if not config_dir.exists():
        os.makedirs(config_dir, exist_ok=True)
        print(f"创建配置目录: {config_dir}")
    
    if not config_file.exists():
        # 创建基本配置
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
            "mqtt_broker_host": "localhost",
            "mqtt_broker_port": 1883,
            "siot_username": "siot",
            "siot_password": "dfrobot",
            "mqtt_client_id": "smart_campus_dashboard",
            "mqtt_topics": [
                "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
                "siot/紫外线指数", "siot/uv风险等级", "siot/噪音"
            ]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"创建默认配置文件: {config_file}")
    
    return config_file

def start_mqtt_broker():
    """启动MQTT服务器"""
    try:
        # 检查是否有paho-mqtt库
        import paho.mqtt.client
        print("MQTT库已安装")
        
        mqtt_script = SRC_PATH / "simple_mqtt_broker.py"
        if not mqtt_script.exists():
            print(f"警告: 找不到MQTT服务器脚本: {mqtt_script}")
            return None
        
        print("正在启动本地MQTT服务器...")
        mqtt_process = subprocess.Popen(
            [sys.executable, str(mqtt_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print("MQTT服务器已启动")
        return mqtt_process
    except ImportError:
        print("警告: 未安装MQTT库，无法启动MQTT服务器")
        return None
    except Exception as e:
        print(f"启动MQTT服务器时出错: {e}")
        return None

def start_data_simulator():
    """启动数据模拟器"""
    try:
        simulator_script = SRC_PATH / "simulators" / "sensor_data_simulator.py"
        if not simulator_script.exists():
            simulator_script = SRC_PATH / "sensor_data_simulator.py"
            if not simulator_script.exists():
                print(f"警告: 找不到数据模拟器脚本")
                return None
        
        print("正在启动数据模拟器...")
        simulator_process = subprocess.Popen(
            [sys.executable, str(simulator_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print("数据模拟器已启动")
        return simulator_process
    except Exception as e:
        print(f"启动数据模拟器时出错: {e}")
        return None

def main():
    """主函数"""
    print(f"==========================================")
    print(f"  烟铺小学智慧校园环境监测系统 - 完整版  ")
    print(f"==========================================")
    print()
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"系统环境: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print(f"项目根目录: {PROJECT_ROOT}")
    print()
    
    # 确保配置文件存在
    config_file = ensure_config_exists()
    print(f"配置文件: {config_file}")
    
    # 启动MQTT服务器
    mqtt_process = start_mqtt_broker()
    
    # 启动数据模拟器
    simulator_process = start_data_simulator()
    
    try:
        print("\n准备启动仪表盘...")
        
        # 导入仪表盘类
        from src.ui.dashboard import SimpleDashboard
        
        # 创建主窗口
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统")
        root.geometry("1280x720")
        
        # 窗口居中
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 720) // 2
        root.geometry(f"1280x720+{x}+{y}")
        
        # 创建仪表盘实例
        print("初始化仪表盘...")
        dashboard = SimpleDashboard(root)
        
        # 启动主循环
        print("启动主循环...")
        root.mainloop()
        print("主循环结束")
        
    except Exception as e:
        print(f"启动仪表盘时出错: {e}")
        traceback.print_exc()
    
    finally:
        # 关闭所有子进程
        if 'mqtt_process' in locals() and mqtt_process:
            mqtt_process.terminate()
            print("MQTT服务器已关闭")
        
        if 'simulator_process' in locals() and simulator_process:
            simulator_process.terminate()
            print("数据模拟器已关闭")
    
    print("\n==========================================")
    print("  智慧校园环境监测系统 - 会话已结束")
    print("==========================================")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
