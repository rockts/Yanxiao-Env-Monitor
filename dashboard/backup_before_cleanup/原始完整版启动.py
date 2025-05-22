#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 原始完整版启动脚本
"""

import os
import sys
import importlib
import traceback
from pathlib import Path
import subprocess
import datetime

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 50)
print("烟铺小学智慧校园环境监测系统 - 原始完整版")
print("=" * 50)
print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"项目根目录: {PROJECT_ROOT}")
print()

# 确保src目录在Python路径中
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"
print(f"设置PYTHONPATH: {os.environ['PYTHONPATH']}")

# 创建日志目录
logs_dir = PROJECT_ROOT / "logs"
if not logs_dir.exists():
    os.makedirs(logs_dir, exist_ok=True)
    print(f"创建日志目录: {logs_dir}")

# 创建配置目录
config_dir = PROJECT_ROOT / "config"
if not config_dir.exists():
    os.makedirs(config_dir, exist_ok=True)
    print(f"创建配置目录: {config_dir}")

# 定义MQTT服务器启动函数
def start_mqtt():
    """启动本地MQTT服务器"""
    mqtt_script = SRC_PATH / "simple_mqtt_broker.py"
    
    if not mqtt_script.exists():
        print(f"警告: 找不到MQTT服务器脚本 {mqtt_script}")
        return None
    
    try:
        print("启动本地MQTT服务器...")
        mqtt_process = subprocess.Popen(
            [sys.executable, str(mqtt_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("MQTT服务器已启动")
        return mqtt_process
    except Exception as e:
        print(f"启动MQTT服务器时出错: {e}")
        return None

# 定义数据模拟器启动函数
def start_simulator():
    """启动传感器数据模拟器"""
    simulator_script = SRC_PATH / "simulators" / "sensor_data_simulator.py"
    if not simulator_script.exists():
        simulator_script = SRC_PATH / "sensor_data_simulator.py"
        if not simulator_script.exists():
            print(f"警告: 找不到传感器数据模拟器脚本")
            return None
    
    try:
        print("启动传感器数据模拟器...")
        simulator_process = subprocess.Popen(
            [sys.executable, str(simulator_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("传感器数据模拟器已启动")
        return simulator_process
    except Exception as e:
        print(f"启动传感器数据模拟器时出错: {e}")
        return None

# 尝试启动MQTT服务器
mqtt_process = start_mqtt()

# 尝试启动数据模拟器
simulator_process = start_simulator()

try:
    # 尝试直接导入完整版仪表盘类并运行
    print("\n正在启动完整版仪表盘...")
    
    # 导入tkinter
    import tkinter as tk
    
    # 直接导入原始仪表盘类 (dashboard.py中的SimpleDashboard类)
    print("导入原始仪表盘类...")
    from src.ui.dashboard import SimpleDashboard
    
    # 创建窗口实例
    print("创建窗口...")
    root = tk.Tk()
    root.title("烟铺小学智慧校园环境监测系统")
    
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
    # 关闭子进程
    if 'mqtt_process' in locals() and mqtt_process:
        mqtt_process.terminate()
        print("MQTT服务器已关闭")
    
    if 'simulator_process' in locals() and simulator_process:
        simulator_process.terminate()
        print("传感器数据模拟器已关闭")

print("\n程序已退出，按回车键关闭窗口...")
input()
