#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 简易启动器
直接启动完整版仪表盘，无需额外配置
"""

import os
import sys
import traceback
from pathlib import Path
import platform
import datetime

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 启动中...     ")
print("=" * 60)
print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"Python版本: {platform.python_version()}")
print(f"项目根目录: {PROJECT_ROOT}")
print()

# 添加src目录到路径
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}"
print(f"设置PYTHONPATH: {os.environ['PYTHONPATH']}")

# 创建日志目录
logs_dir = PROJECT_ROOT / "logs"
if not logs_dir.exists():
    os.makedirs(logs_dir, exist_ok=True)
    print(f"创建日志目录: {logs_dir}")

try:
    # 找到main.py文件
    main_py_path = SRC_PATH / "main.py"
    if not main_py_path.exists():
        raise FileNotFoundError(f"找不到主模块文件: {main_py_path}")
    
    print(f"正在启动仪表盘...")
    
    # 导入tkinter
    import tkinter as tk
    
    # 创建根窗口
    root = tk.Tk()
    
    # 直接从main.py导入所需内容
    print(f"导入主模块...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", main_py_path)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    
    # 创建应用实例
    print(f"创建应用实例...")
    app = main.SmartCampusDashboard(root)
    
    # 添加错误处理和窗口关闭处理
    def on_error(*args):
        print("发生未处理的异常:")
        traceback.print_exception(*args)
    
    # 设置未捕获异常处理器
    sys.excepthook = on_error
    
    # 添加窗口关闭处理
    print(f"设置窗口关闭处理...")
    if hasattr(app, 'on_closing'):
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
    else:
        def default_on_closing():
            if hasattr(app, 'mqtt_client'):
                try:
                    app.mqtt_client.loop_stop()
                    app.mqtt_client.disconnect()
                except:
                    pass
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", default_on_closing)
    
    # 启动主循环
    print(f"启动主循环...")
    root.mainloop()
    
except Exception as e:
    print(f"启动仪表盘时出错: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
    print("\n请按回车键退出...")
    input()
