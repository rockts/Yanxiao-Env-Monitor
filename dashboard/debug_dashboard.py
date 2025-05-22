#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智慧校园环境监测系统 - 调试脚本
用于调试完整版仪表盘问题
"""

import os
import sys
import traceback

print("启动调试脚本...")
print(f"当前工作目录: {os.getcwd()}")

try:
    print("尝试导入仪表盘模块...")
    import full_dashboard_new
    print("成功导入仪表盘模块")
    
    # 尝试查找主类和入口点
    print("查找主类和入口点...")
    import inspect
    classes = inspect.getmembers(full_dashboard_new, inspect.isclass)
    print(f"发现以下类: {[name for name, _ in classes]}")
    
    funcs = inspect.getmembers(full_dashboard_new, inspect.isfunction)
    print(f"发现以下函数: {[name for name, _ in funcs]}")
    
    # 检查配置文件
    print("\n检查配置文件...")
    import os.path
    config_paths = [
        "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/config/config.json",
        "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/config/default_config.json"
    ]
    for path in config_paths:
        if os.path.exists(path):
            print(f"  配置文件存在: {path}")
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"  配置文件格式正确，包含 {len(config)} 个键")
                print(f"  配置键: {list(config.keys())}")
            except Exception as e:
                print(f"  配置文件格式错误: {e}")
        else:
            print(f"  配置文件不存在: {path}")
    
    # 检查日志目录
    print("\n检查日志目录...")
    log_dir = "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/logs"
    if os.path.exists(log_dir) and os.path.isdir(log_dir):
        print(f"  日志目录存在: {log_dir}")
        logs = os.listdir(log_dir)
        print(f"  日志文件数量: {len(logs)}")
    else:
        print(f"  日志目录不存在或不是目录: {log_dir}")
    
    # 分步骤初始化仪表盘，以便定位问题
    print("\n尝试运行仪表盘...")
    if 'SmartCampusDashboard' in [name for name, _ in classes]:
        print("找到 SmartCampusDashboard 类")
        # 检查类的初始化参数
        print("检查类的初始化参数...")
        init_sig = inspect.signature(full_dashboard_new.SmartCampusDashboard.__init__)
        print(f"  初始化方法参数: {init_sig}")
        
        print("1. 创建Tkinter根窗口...")
        import tkinter as tk
        root = tk.Tk()
        print("  根窗口已创建")
        
        print("2. 初始化SmartCampusDashboard类...")
        try:
            app = full_dashboard_new.SmartCampusDashboard(root)
            print("  已创建仪表盘实例")
            print("3. 启动主循环...")
            root.mainloop()
        except Exception as e:
            print(f"  初始化仪表盘时出错: {e}")
            print("  详细错误信息:")
            traceback.print_exc()
    else:
        print("未找到主类，无法启动")
        
except Exception as e:
    print(f"错误: {e}")
    print("详细错误信息:")
    traceback.print_exc()
    
print("调试脚本结束")
