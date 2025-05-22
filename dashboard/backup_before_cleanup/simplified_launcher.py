#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 直接启动脚本
简化的启动方式，只启动仪表盘窗口，不包含MQTT服务器和数据模拟器
"""

import os
import sys
import traceback
import tkinter as tk
from pathlib import Path
import logging

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

# 配置日志
log_dir = PROJECT_ROOT / "logs"
if not log_dir.exists():
    os.makedirs(log_dir, exist_ok=True)

# 添加模块路径
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """主函数"""
    print("=" * 60)
    print("     烟铺小学智慧校园环境监测系统 - 简单启动器     ")
    print("=" * 60)
    
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统")
        root.geometry("1200x800")
        
        # 设置窗口图标（如果有）
        icon_path = PROJECT_ROOT / "assets" / "icon.png"
        if icon_path.exists():
            try:
                from PIL import Image, ImageTk
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                root.iconphoto(True, icon)
            except ImportError:
                pass
        
        # 导入主模块
        try:
            # 加载方式1：直接导入模块
            try:
                print("尝试导入主模块...")
                from main import SmartCampusDashboard
                print("成功导入主模块")
                app = SmartCampusDashboard(root)
            except ImportError:
                print("无法直接导入模块，尝试通过文件路径加载")
                # 加载方式2：通过文件路径导入
                main_py_path = SRC_PATH / "main.py"
                if not main_py_path.exists():
                    raise FileNotFoundError(f"找不到主模块文件: {main_py_path}")
                
                print(f"从文件导入: {main_py_path}")
                import importlib.util
                spec = importlib.util.spec_from_file_location("main", main_py_path)
                main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main)
                app = main.SmartCampusDashboard(root)
            
            # 设置关闭处理
            if hasattr(app, 'on_closing'):
                root.protocol("WM_DELETE_WINDOW", app.on_closing)
            else:
                def on_closing():
                    try:
                        if hasattr(app, 'mqtt_client'):
                            app.mqtt_client.loop_stop()
                            app.mqtt_client.disconnect()
                    except:
                        pass
                    root.destroy()
                root.protocol("WM_DELETE_WINDOW", on_closing)
            
            print("启动主循环")
            root.mainloop()
            
        except Exception as e:
            print(f"ERROR: 创建应用实例时出错: {e}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"ERROR: 启动过程中出现错误: {e}")
        traceback.print_exc()
    
    print("程序已退出")

if __name__ == "__main__":
    main()
