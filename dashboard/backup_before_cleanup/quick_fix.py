#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 快速修复版
这个文件创建了一个简单、独立的启动器，直接运行仪表盘程序并添加了缺失的方法
"""

import os
import sys
import platform
import datetime
import traceback
from pathlib import Path
import logging
import tkinter as tk
import random
import paho.mqtt.client as mqtt
import importlib.util

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

# 准备目录和基础设置
print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 快速修复版     ")
print("=" * 60)
print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"Python版本: {platform.python_version()}")
print(f"项目根目录: {PROJECT_ROOT}")
print()

# 确保src目录在Python路径中
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 创建日志目录
log_dir = PROJECT_ROOT / "logs"
if not log_dir.exists():
    os.makedirs(log_dir, exist_ok=True)
    print(f"创建日志目录: {log_dir}")

log_file = log_dir / f"quick_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# 创建配置目录
config_dir = PROJECT_ROOT / "config"
if not config_dir.exists():
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

# 常量定义
TEXT_COLOR_STATUS_OK = "#33FF99"
TEXT_COLOR_STATUS_FAIL = "#FF6666"
TEXT_COLOR_STATUS_SIM = "#FFD700"

# 模拟数据
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

# 修复缺失的方法
class DashboardFixer:
    """负责修复仪表盘类的辅助类"""
    
    @staticmethod
    def update_connection_status_display(self, connected, status_text=None):
        """更新MQTT连接状态显示"""
        try:
            self._mqtt_connected = connected
            
            if connected:
                status_msg = "状态: 已连接到MQTT服务器"
                status_color = TEXT_COLOR_STATUS_OK
                self.connection_status_var.set(status_msg)
                logging.info(status_msg)
            else:
                if status_text:
                    status_msg = f"状态: {status_text}"
                else:
                    status_msg = "状态: 未连接"
                status_color = TEXT_COLOR_STATUS_FAIL
                self.connection_status_var.set(status_msg)
                logging.warning(status_msg)
            
            # 如果标签控件已创建，更新其外观
            if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                self.connection_status_label_widget.config(text=status_msg, fg=status_color)
        except Exception as e:
            logging.error(f"更新连接状态显示时出错: {e}")
            print(f"ERROR: 更新连接状态显示时出错: {e}")
    
    @staticmethod
    def on_message(self, client, userdata, msg):
        """处理MQTT消息"""
        try:
            topic_str = msg.topic
            
            # 尝试解码消息
            try:
                payload_str = msg.payload.decode('utf-8')
            except UnicodeDecodeError:
                logging.error(f"解码消息失败: {msg.topic}")
                return
                
            print(f"收到MQTT消息: {topic_str} = {payload_str}")
            
            # 这部分根据仪表盘实际设计来处理消息
            # 这里是简化版的处理，实际应该根据仪表盘类的实现来调整
            if hasattr(self, 'panel_configs'):
                for key, config in self.panel_configs.items():
                    if "base_topic_name" in config:
                        expected_topic = "siot/" + config["base_topic_name"]
                        if topic_str == expected_topic:
                            if hasattr(self, 'data_vars') and key in self.data_vars:
                                self.data_vars[key].set(payload_str)
                                print(f"更新数据: {key} = {payload_str}")
                                
                                # 如果有历史数据记录，也进行更新
                                if hasattr(self, 'sensor_data_history') and key in self.sensor_data_history:
                                    try:
                                        value = float(payload_str)
                                        timestamp = datetime.datetime.now()
                                        self.sensor_data_history[key].append((timestamp, value))
                                    except ValueError:
                                        pass
                            break
            
        except Exception as e:
            logging.error(f"处理消息时出错: {str(e)}")
            print(f"处理消息错误: {str(e)}")
            traceback.print_exc()
    
    @staticmethod
    def toggle_simulation(self):
        """切换是否使用模拟数据"""
        print("DEBUG: toggle_simulation 方法被调用")
        
        # 确保实例有use_simulation属性
        if not hasattr(self, 'use_simulation'):
            self.use_simulation = True
        
        # 切换模拟状态
        self.use_simulation = not self.use_simulation
        
        if self.use_simulation:
            print("DEBUG: 启用模拟数据模式")
            self.sim_button_text_var.set("关闭模拟数据")
            # 更新状态显示
            logging.info("已启用模拟数据模式")
            if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                self.connection_status_label_widget.config(text="状态: 使用模拟数据", fg=TEXT_COLOR_STATUS_SIM)
            
            # 更新所有传感器数据
            for topic_key, value in simulation_data.items():
                print(f"DEBUG: 正在模拟数据 - {topic_key}: {value}")
                full_topic = f"siot/{topic_key}"
                # 模拟消息格式
                message = mqtt.MQTTMessage()
                message.topic = full_topic.encode('utf-8')
                message.payload = value.encode('utf-8')
                # 直接调用消息处理函数
                self.on_message(None, None, message)
                
            # 定期刷新模拟数据
            self.root.after(5000, self.refresh_simulation_data)
        else:
            print("DEBUG: 关闭模拟数据模式")
            self.sim_button_text_var.set("启用模拟数据")
            logging.info("已关闭模拟数据模式")
            # 尝试重新连接MQTT
            self.connect_mqtt()
    
    @staticmethod
    def refresh_simulation_data(self):
        """定期刷新模拟数据"""
        if not hasattr(self, 'use_simulation') or not self.use_simulation:
            return
        
        # 随机变化模拟数据，在原基础上加减一些随机值
        for key in simulation_data:
            try:
                current_value = float(simulation_data[key])
                # 添加一些随机变化，最大为当前值的10%
                change = current_value * (random.random() * 0.1 - 0.05)  # -5% 到 +5% 的变化
                new_value = current_value + change
                
                # 确保值在合理范围内
                if key == "环境温度":
                    new_value = max(10, min(40, new_value))  # 确保温度在10-40度之间
                elif key == "环境湿度":
                    new_value = max(20, min(95, new_value))  # 确保湿度在20-95%之间
                elif key == "aqi":
                    new_value = max(20, min(300, new_value))  # AQI范围
                
                # 更新模拟数据
                simulation_data[key] = f"{new_value:.1f}"
                
                # 发送模拟消息
                full_topic = f"siot/{key}"
                message = mqtt.MQTTMessage()
                message.topic = full_topic.encode('utf-8')
                message.payload = simulation_data[key].encode('utf-8')
                self.on_message(None, None, message)
                
            except (ValueError, TypeError):
                # 非数值的不做变化
                pass
        
        # 继续定期刷新
        self.root.after(5000, self.refresh_simulation_data)
        
    @staticmethod
    def on_closing(self):
        """当窗口关闭时的处理程序"""
        logging.info("应用程序正在关闭")
        try:
            # 停止MQTT客户端循环
            if hasattr(self, 'mqtt_client') and self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logging.info("MQTT客户端已断开连接")
        except Exception as e:
            logging.error(f"关闭MQTT连接时出错: {e}")
        finally:
            # 确保窗口被销毁
            self.root.destroy()
            logging.info("应用程序已关闭")
    
    @staticmethod
    def fix_dashboard_class(dashboard_class):
        """为仪表盘类添加缺失的方法"""
        
        # 添加update_connection_status_display方法
        if not hasattr(dashboard_class, 'update_connection_status_display'):
            dashboard_class.update_connection_status_display = DashboardFixer.update_connection_status_display
            print("添加了update_connection_status_display方法")
        
        # 添加on_message方法
        if not hasattr(dashboard_class, 'on_message'):
            dashboard_class.on_message = DashboardFixer.on_message
            print("添加了on_message方法")
        
        # 添加toggle_simulation方法
        if not hasattr(dashboard_class, 'toggle_simulation'):
            dashboard_class.toggle_simulation = DashboardFixer.toggle_simulation
            print("添加了toggle_simulation方法")
        
        # 添加refresh_simulation_data方法
        if not hasattr(dashboard_class, 'refresh_simulation_data'):
            dashboard_class.refresh_simulation_data = DashboardFixer.refresh_simulation_data
            print("添加了refresh_simulation_data方法")
        
        # 添加on_closing方法
        if not hasattr(dashboard_class, 'on_closing'):
            dashboard_class.on_closing = DashboardFixer.on_closing
            print("添加了on_closing方法")
        
        return dashboard_class

def main():
    """主函数，修复并运行仪表盘"""
    try:
        # 导入主模块
        main_module_path = SRC_PATH / "main.py"
        print(f"导入主模块: {main_module_path}")
        
        spec = importlib.util.spec_from_file_location("main", main_module_path)
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # 修复SmartCampusDashboard类
        print("修复SmartCampusDashboard类...")
        SmartCampusDashboard = getattr(main_module, 'SmartCampusDashboard')
        fixed_class = DashboardFixer.fix_dashboard_class(SmartCampusDashboard)
        
        # 创建根窗口
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统 - 修复版")
        
        # 创建仪表盘实例
        print("创建仪表盘实例...")
        app = fixed_class(root)
        
        # 设置窗口关闭处理
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # 启动主循环
        print("启动主循环...")
        root.mainloop()
        
    except Exception as e:
        print(f"启动仪表盘时出错: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        
        print("\n按回车键退出...")
        input()

if __name__ == "__main__":
    main()
