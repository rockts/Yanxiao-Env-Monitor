#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 调试启动脚本
重定向所有输出到文件，帮助诊断启动问题
"""

import os
import sys
import traceback
import datetime
from pathlib import Path

# 设置项目根目录和源代码路径
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

# 创建日志文件
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = PROJECT_ROOT / "debug_logs"
if not log_dir.exists():
    os.makedirs(log_dir)

log_file = log_dir / f"debug_startup_{timestamp}.log"

# 捕获并记录所有输出
with open(log_file, "w") as f:
    # 记录基础信息
    f.write(f"===== 调试启动脚本 =====\n")
    f.write(f"开始时间: {datetime.datetime.now().isoformat()}\n")
    f.write(f"Python版本: {sys.version}\n")
    f.write(f"Python可执行文件: {sys.executable}\n")
    f.write(f"当前工作目录: {os.getcwd()}\n")
    f.write(f"项目根目录: {PROJECT_ROOT}\n")
    f.write(f"源代码路径: {SRC_PATH}\n")
    f.write(f"系统环境变量:\n")
    for key, value in os.environ.items():
        f.write(f"  {key} = {value}\n")
    f.write(f"系统路径:\n")
    for path in sys.path:
        f.write(f"  {path}\n")
    f.write("\n")

    # 确保可以导入src目录下的模块
    sys.path.insert(0, str(SRC_PATH))
    sys.path.insert(0, str(PROJECT_ROOT))
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"
    
    f.write(f"添加到sys.path: {SRC_PATH}, {PROJECT_ROOT}\n")
    f.write(f"设置PYTHONPATH: {os.environ['PYTHONPATH']}\n\n")

    try:
        f.write("===== 开始导入模块 =====\n")
        # 尝试导入所有必要的模块，逐个测试
        
        # 1. 测试tkinter - GUI基础库
        f.write("尝试导入tkinter...\n")
        import tkinter as tk
        f.write(f"tkinter版本: {tk.TkVersion}\n")
        
        # 2. 测试PIL - 图像处理库
        f.write("尝试导入PIL...\n")
        try:
            from PIL import Image, ImageTk
            f.write("PIL导入成功\n")
        except ImportError as e:
            f.write(f"PIL导入失败: {e}\n")
        
        # 3. 测试paho-mqtt - MQTT客户端库
        f.write("尝试导入paho-mqtt...\n")
        try:
            import paho.mqtt.client as mqtt
            f.write(f"paho-mqtt版本: {mqtt.__version__}\n")
        except ImportError as e:
            f.write(f"paho-mqtt导入失败: {e}\n")
        except AttributeError:
            f.write("paho-mqtt导入成功，但无法获取版本号\n")
        
        # 4. 测试项目核心模块
        f.write("尝试导入项目核心模块...\n")
        try:
            from src.core.config_manager import ConfigManager
            f.write("ConfigManager导入成功\n")
        except ImportError as e:
            f.write(f"ConfigManager导入失败: {e}\n")
            
        try:
            from src.core.log_manager import LogManager
            f.write("LogManager导入成功\n")
        except ImportError as e:
            f.write(f"LogManager导入失败: {e}\n")
        
        # 5. 测试UI模块
        f.write("尝试导入UI模块...\n")
        try:
            from src.ui.simple_dashboard import SimpleDashboard
            f.write("SimpleDashboard导入成功\n")
        except ImportError as e:
            f.write(f"SimpleDashboard导入失败: {e}\n")
            
        # 创建一个简单的tkinter窗口测试
        f.write("\n===== 测试tkinter窗口 =====\n")
        try:
            root = tk.Tk()
            root.title("Tkinter测试")
            root.geometry("300x200")
            label = tk.Label(root, text="如果你能看到这个窗口，说明tkinter工作正常")
            label.pack(pady=50)
            f.write("tkinter窗口创建成功\n")
            f.write("注意：窗口将在5秒后关闭\n")
            
            # 5秒后自动关闭窗口
            root.after(5000, root.destroy)
            root.mainloop()
            
            f.write("tkinter窗口测试完成\n")
        except Exception as e:
            f.write(f"tkinter窗口测试失败: {e}\n")
            f.write(traceback.format_exc())
        
        f.write("\n===== 测试ConfigManager =====\n")
        try:
            config_manager = ConfigManager(project_root=PROJECT_ROOT)
            app_config = config_manager.get_all()
            f.write(f"配置加载成功: {json.dumps(app_config, indent=2)}\n")
        except Exception as e:
            f.write(f"配置加载失败: {e}\n")
            f.write(traceback.format_exc())
        
        f.write("\n===== 尝试创建SimpleDashboard =====\n")
        try:
            dashboard = SimpleDashboard(app_config=app_config)
            f.write("SimpleDashboard创建成功\n")
            f.write("注意：窗口将在10秒后关闭\n")
            
            # 10秒后自动关闭窗口
            dashboard.root.after(10000, dashboard.root.destroy)
            dashboard.run()
            
            f.write("SimpleDashboard运行完成\n")
        except Exception as e:
            f.write(f"SimpleDashboard创建或运行失败: {e}\n")
            f.write(traceback.format_exc())
    
    except Exception as e:
        f.write(f"\n===== 发生未预期的错误 =====\n")
        f.write(f"错误: {e}\n")
        f.write(traceback.format_exc())
    
    finally:
        f.write(f"\n===== 调试脚本完成 =====\n")
        f.write(f"结束时间: {datetime.datetime.now().isoformat()}\n")

# 生成一个通知文件，提示日志已创建
with open(PROJECT_ROOT / "debug_complete.txt", "w") as notify_file:
    notify_file.write(f"调试脚本已完成运行。\n")
    notify_file.write(f"日志文件位于: {log_file}\n")
    notify_file.write(f"完成时间: {datetime.datetime.now().isoformat()}\n")

print(f"调试完成。详细日志已保存到: {log_file}")
print(f"同时创建了通知文件: {PROJECT_ROOT / 'debug_complete.txt'}")
