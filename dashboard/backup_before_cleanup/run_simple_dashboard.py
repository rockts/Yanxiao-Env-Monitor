#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 直接启动脚本
基于调试结果开发的简化启动流程
"""

import os
import sys
import json
import time
from pathlib import Path

# 设置项目根目录和源代码路径
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

# 确保可以导入src目录下的模块
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"

print("导入核心组件...")
from src.core.config_manager import ConfigManager, DEFAULT_CONFIG
from src.core.log_manager import LogManager, logger

def main():
    # 全局变量声明
    global mqtt_process
    
    # 初始化配置
    print("初始化配置...")
    # 创建指向config.json的完整路径
    config_path = PROJECT_ROOT / "config" / "config.json"
    
    # 确保配置目录存在
    if not os.path.exists(config_path.parent):
        os.makedirs(config_path.parent, exist_ok=True)
        print(f"创建配置目录: {config_path.parent}")
    
    # 确保配置文件存在
    if not os.path.exists(config_path):
        # 创建默认配置
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
                "window_size": "800x600"
            },
            "mqtt_broker_host": "localhost",
            "mqtt_broker_port": 1883
        }
        
        with open(str(config_path), 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"创建默认配置文件: {config_path}")
    
    # 初始化配置管理器
    config_manager = ConfigManager(config_path=str(config_path))
    app_config = config_manager.get_all()
    
    # 添加运行时选项到配置
    app_config['simulate_data'] = True  # 使用模拟数据
    app_config['use_local_mqtt'] = True  # 使用本地MQTT
    app_config['simple_mode'] = True     # 简化模式
    app_config['mqtt_broker_host'] = 'localhost'  # 本地MQTT服务器
    
    # 初始化日志
    print("初始化日志...")
    log_manager = LogManager(log_level='INFO')
    
    # 启动本地MQTT服务
    mqtt_process = None
    if app_config.get('use_local_mqtt', True):
        try:
            print("尝试启动本地MQTT服务...")
            mqtt_script = PROJECT_ROOT / "utils" / "local_mqtt_server.py"
            
            # 如果脚本不存在，显示警告
            if not mqtt_script.exists():
                print(f"警告: 找不到本地MQTT服务脚本: {mqtt_script}")
            else:
                # 启动MQTT服务器进程
                import subprocess
                mqtt_process = subprocess.Popen(
                    [sys.executable, str(mqtt_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                print("本地MQTT服务已启动")
                # 等待服务器启动
                time.sleep(2)
        except Exception as e:
            print(f"启动本地MQTT服务失败: {e}")
    
    # 导入简易仪表盘
    print("导入简易仪表盘...")
    from src.ui.dashboard import SimpleDashboard
    
    # 初始化Tkinter
    print("初始化Tkinter...")
    import tkinter as tk
    root = tk.Tk()
    root.title("烟铺小学智慧校园环境监测系统")
    
    # 初始化仪表盘并运行
    print("初始化仪表盘...")
    dashboard = SimpleDashboard(root)  # 只需要传递root参数
    
    print("启动仪表盘...")
    # SimpleDashboard 创建后，使用 Tkinter 的 mainloop() 直接运行
    root.mainloop()
    print("仪表盘已关闭")

if __name__ == "__main__":
    mqtt_process = None
    try:
        print("启动简易仪表盘...")
        main()
    except Exception as e:
        import traceback
        print(f"启动失败: {e}")
        print(traceback.format_exc())
        
        # 创建错误日志文件
        error_file = PROJECT_ROOT / "startup_error.txt"
        with open(error_file, "w") as f:
            f.write(f"启动失败: {e}\n")
            f.write(traceback.format_exc())
        
        print(f"错误详情已保存到: {error_file}")
        sys.exit(1)
    finally:
        # 确保关闭所有子进程
        if 'mqtt_process' in locals() and mqtt_process:
            print("关闭MQTT服务进程...")
            try:
                mqtt_process.terminate()
                mqtt_process.wait(timeout=5)
                print("MQTT服务已关闭")
            except Exception as e:
                print(f"关闭MQTT服务时出错: {e}")
