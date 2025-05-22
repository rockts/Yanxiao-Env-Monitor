#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 启动测试脚本
用于测试MQTT连接修复
"""

import os
import sys
import traceback
from pathlib import Path
import subprocess
import datetime
import time
import platform

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 测试脚本     ")
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

try:
    # 导入main模块
    print("\n正在启动测试...")
    print("导入主模块...")
    
    # 检查main.py是否存在
    main_py_path = SRC_PATH / "main.py"
    if not main_py_path.exists():
        raise FileNotFoundError(f"找不到主模块文件: {main_py_path}")
    
    print(f"正在执行主模块文件: {main_py_path}")
    
    # 直接运行main.py文件
    try:
        exec(open(main_py_path).read())
    except Exception as e:
        if "update_connection_status_display" in str(e):
            print("\n错误: 'SmartCampusDashboard' 对象没有 'update_connection_status_display' 属性")
            print("修复未能解决问题。请检查main.py文件中是否正确添加了该方法。")
        else:
            print(f"\n启动仪表盘时出错: {e}")
            print("\n详细错误信息:")
            traceback.print_exc()
    else:
        print("测试成功完成，未发现 'update_connection_status_display' 相关错误！")
    
except Exception as e:
    print(f"测试过程中出错: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()

print("\n=" * 30)
print("  智慧校园环境监测系统 - 测试已结束")
print("=" * 30)
print("按回车键退出...")
input()
