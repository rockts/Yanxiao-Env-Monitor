#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 真·完整版启动器
直接启动包含多种传感器数据显示的完整仪表盘
"""

import os
import sys
import traceback
from pathlib import Path
import subprocess
import datetime
import platform

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 真·完整版     ")
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
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"
print(f"设置PYTHONPATH: {os.environ['PYTHONPATH']}")

# 创建日志目录
logs_dir = PROJECT_ROOT / "logs"
if not logs_dir.exists():
    os.makedirs(logs_dir, exist_ok=True)
    print(f"创建日志目录: {logs_dir}")

# 确保配置目录存在
config_dir = PROJECT_ROOT / "config"
if not config_dir.exists():
    os.makedirs(config_dir, exist_ok=True)
    print(f"创建配置目录: {config_dir}")

# 创建基本配置文件(如果不存在)
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
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    print(f"创建默认配置文件: {config_file}")

# 定义启动MQTT服务器的函数
def start_mqtt():
    """启动本地MQTT服务器"""
    mqtt_script = SRC_PATH / "simple_mqtt_broker.py"
    
    if not mqtt_script.exists():
        print(f"警告: 找不到MQTT服务器脚本 {mqtt_script}")
        return None
    
    try:
        print(f"使用MQTT服务器脚本: {mqtt_script}")
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

# 定义启动数据模拟器的函数
def start_simulator():
    """启动传感器数据模拟器"""
    # 首先检查simulators目录下的模拟器
    simulator_script = SRC_PATH / "simulators" / "sensor_data_simulator.py"
    if not simulator_script.exists():
        # 然后检查根目录下的模拟器
        simulator_script = SRC_PATH / "sensor_data_simulator.py"
        if not simulator_script.exists():
            print(f"警告: 找不到传感器数据模拟器脚本")
            return None
    
    print(f"使用模拟器脚本: {simulator_script}")
    
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

# 启动附加组件
mqtt_process = start_mqtt()
simulator_process = start_simulator()

try:
    # 导入并启动主要仪表盘文件 (main.py 是完整版)
    print("\n正在启动真·完整版仪表盘...")
    print("导入主模块...")
    
    # 检查main.py是否存在
    main_py_path = SRC_PATH / "main.py"
    if not main_py_path.exists():
        raise FileNotFoundError(f"找不到主模块文件: {main_py_path}")
    
    print(f"正在执行主模块文件: {main_py_path}")
    
    # 添加详细的错误捕获
    try:
        # 启用详细错误信息
        import traceback
        
        # 确保配置文件目录正确
        config_dir = PROJECT_ROOT / "config"
        if not config_dir.exists():
            print(f"创建配置目录: {config_dir}")
            os.makedirs(config_dir, exist_ok=True)
            
        # 确保配置文件存在
        config_file = config_dir / "config.json"
        if not config_file.exists():
            print(f"创建默认配置文件: {config_file}")
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
        
        # 修复 SmartCampusDashboard 类
        print("添加必要的方法到SmartCampusDashboard类...")
        
        # 定义修复函数
        fix_code = """
# 添加缺失的方法到 SmartCampusDashboard 类
def patch_smart_campus_dashboard():
    import types
    import sys
    import logging
    
    # 动态导入模块中的类
    print("正在准备获取SmartCampusDashboard类...")
    
    # 执行前先修复
    def update_connection_status_display(self, connected, status_text=None):
        '''更新MQTT连接状态显示'''
        print(f"MQTT连接状态: {'已连接' if connected else '未连接'} - {status_text if status_text else ''}")
        try:
            # 如果有connection_status_var属性
            if hasattr(self, 'connection_status_var'):
                status_msg = f"状态: {'已连接' if connected else status_text if status_text else '未连接'}"
                self.connection_status_var.set(status_msg)
                
                # 如果有connection_status_label_widget属性
                if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                    color = "#33FF99" if connected else "#FF6666"  # 绿色或红色
                    self.connection_status_label_widget.config(text=status_msg, fg=color)
        except Exception as e:
            print(f"更新连接状态时出错: {e}")
    
    def on_closing(self):
        '''窗口关闭时的处理函数'''
        print("应用程序正在关闭...")
        try:
            if hasattr(self, 'mqtt_client') and self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
        except Exception as e:
            print(f"关闭MQTT连接时出错: {e}")
        finally:
            if hasattr(self, 'root'):
                self.root.destroy()
    
    # 在全局命名空间中找到SmartCampusDashboard类
    import inspect
    import sys
    
    # 直接执行前先添加方法
    print("准备修复SmartCampusDashboard类...")
    
    # 先运行脚本的一部分，直到定义了SmartCampusDashboard类
    with open(main_py_path, 'r', encoding='utf-8') as f:
        main_script = f.read()
    
    # 找到SmartCampusDashboard类的定义位置
    class_pos = main_script.find("class SmartCampusDashboard")
    if class_pos == -1:
        print("错误: 找不到SmartCampusDashboard类定义")
        return False
    
    # 找到类定义之后的第一个方法
    first_method_pos = main_script.find("    def ", class_pos)
    if first_method_pos == -1:
        print("错误: 找不到SmartCampusDashboard类的方法")
        return False
    
    # 在第一个方法之前插入我们的新方法
    patched_script = (
        main_script[:first_method_pos] + 
        "\n    def update_connection_status_display(self, connected, status_text=None):\n" +
        "        '''更新MQTT连接状态显示'''\n" +
        "        try:\n" +
        "            if hasattr(self, 'connection_status_var'):\n" +
        "                status_msg = f\"状态: {'已连接' if connected else status_text if status_text else '未连接'}\"\n" +
        "                self.connection_status_var.set(status_msg)\n" +
        "                if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:\n" +
        "                    color = TEXT_COLOR_STATUS_OK if connected else TEXT_COLOR_STATUS_FAIL\n" +
        "                    self.connection_status_label_widget.config(text=status_msg, fg=color)\n" +
        "        except Exception as e:\n" +
        "            logging.error(f\"更新连接状态显示时出错: {e}\")\n" +
        "            print(f\"ERROR: 更新连接状态显示时出错: {e}\")\n\n" +
        "    def on_closing(self):\n" +
        "        '''当窗口关闭时的处理程序'''\n" +
        "        logging.info(\"应用程序正在关闭\")\n" +
        "        try:\n" +
        "            if hasattr(self, 'mqtt_client') and self.mqtt_client:\n" +
        "                self.mqtt_client.loop_stop()\n" +
        "                self.mqtt_client.disconnect()\n" +
        "                logging.info(\"MQTT客户端已断开连接\")\n" +
        "        except Exception as e:\n" +
        "            logging.error(f\"关闭MQTT连接时出错: {e}\")\n" +
        "        finally:\n" +
        "            self.root.destroy()\n" +
        "            logging.info(\"应用程序已关闭\")\n\n" +
        main_script[first_method_pos:]
    )
    
    # 写入临时文件
    temp_file = main_py_path.parent / "main_patched.py"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(patched_script)
    
    print(f"已创建修补后的文件: {temp_file}")
    return str(temp_file)

# 执行补丁
patched_file = patch_smart_campus_dashboard()

# 执行修复代码
exec(fix_code)
        
        # 获取patched_file变量
        patched_file = locals().get('patched_file')
        
        if patched_file and os.path.exists(patched_file):
            print(f"使用修补后的文件: {patched_file}")
            # 执行修补后的文件
            with open(patched_file, 'r', encoding='utf-8') as f:
                patched_content = f.read()
            exec(patched_content)
        else:
            # 如果补丁失败，尝试直接运行并捕获具体错误
            try:
                with open(main_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                exec(content)
            except Exception as e:
                print(f"\n执行时错误: {type(e).__name__}: {e}")
                print("\n详细错误信息:")
                traceback.print_exc()
    
    except AttributeError as ae:
        print(f"\n错误: 可能是方法缺失 - {ae}")
        print("\n详细错误信息:")
        traceback.print_exc()
    
except Exception as e:
    print(f"启动仪表盘时出错: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
finally:
    # 关闭子进程
    if 'mqtt_process' in locals() and mqtt_process:
        mqtt_process.terminate()
        print("MQTT服务器已关闭")
    
    if 'simulator_process' in locals() and simulator_process:
        simulator_process.terminate()
        print("传感器数据模拟器已关闭")

print("\n=" * 30)
print("  智慧校园环境监测系统 - 会话已结束")
print("=" * 30)
print("按回车键退出...")
input()
