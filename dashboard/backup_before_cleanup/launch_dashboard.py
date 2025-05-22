#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 优化的启动脚本
专注于解决 GUI 窗口显示问题
"""

import os
import sys
import tkinter as tk
from pathlib import Path
import subprocess
import traceback
import platform

# 获取脚本所在目录
script_path = Path(__file__).resolve()
project_root = script_path.parent

# 设置Python路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# 对于macOS，确保使用正确的GUI模式
IS_MACOS = platform.system() == 'Darwin'

print(f"==========================================")
print(f"  烟铺小学智慧校园环境监测系统 - 启动器  ")
print(f"==========================================")
print()
print(f"系统环境:")
print(f"- 操作系统: {platform.system()} {platform.release()}")
print(f"- Python版本: {platform.python_version()}")
print(f"- 项目目录: {project_root}")
print()

# 先运行配置修复工具
try:
    print("运行配置修复工具...")
    config_fixer = project_root / "fix_config.py"
    if config_fixer.exists():
        subprocess.run([sys.executable, str(config_fixer)], check=True)
    else:
        print(f"警告: 找不到配置修复工具: {config_fixer}")
except Exception as e:
    print(f"运行配置修复工具时出错: {e}")

# 在macOS上，检查是否需要使用特殊方法
if IS_MACOS:
    print("\n在macOS上运行，检查GUI环境...")
    # 检查macOS是否在正确的环境中运行
    CORRECT_ENV = 'DISPLAY' in os.environ or '_tkinter' in sys.modules or 'Tk' in sys.modules

    # 如果不是在正确的环境中，尝试使用特殊的启动方式
    if not CORRECT_ENV:
        print("检测到可能需要特殊GUI环境，尝试使用AppleScript启动...")
        try:
            # 创建AppleScript命令
            script = f"""tell application "Terminal"
do script "cd '{project_root}' && python3 {project_root}/run_simple_dashboard.py"
end tell"""
            
            # 执行AppleScript
            subprocess.run(['osascript', '-e', script], check=True)
            print("已通过AppleScript启动新终端窗口运行仪表盘")
            sys.exit(0)
        except Exception as e:
            print(f"通过AppleScript启动失败: {e}")
            print("继续尝试直接启动...")

# 导入需要的模块
try:
    print("\n导入模块...")
    
    # 导入UI组件
    print("导入仪表盘组件...")
    from src.ui.dashboard import SimpleDashboard
    
    def main():
        # 显示诊断信息
        print("\n启动仪表盘...")
        
        # 创建主窗口
        print("创建Tkinter窗口...")
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统")
        root.geometry("800x600")
        
        # 放置窗口在屏幕中央
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        root.geometry(f"800x600+{x}+{y}")
        
        try:
            # 初始化仪表盘
            print("初始化SimpleDashboard...")
            app = SimpleDashboard(root)
            
            # 运行主循环
            print("启动主循环...")
            root.mainloop()
            print("程序已退出")
            
        except Exception as e:
            print(f"启动仪表盘时出错: {e}")
            traceback.print_exc()
            
            # 显示错误窗口
            error_window = tk.Toplevel(root)
            error_window.title("启动错误")
            error_window.geometry("500x300")
            
            # 显示错误信息
            tk.Label(error_window, text="启动仪表盘时出错:", font=("Arial", 12, "bold")).pack(pady=10)
            tk.Label(error_window, text=str(e), wraplength=450).pack(pady=5)
            
            # 显示详细错误信息
            error_frame = tk.Frame(error_window)
            error_frame.pack(padx=10, pady=10, fill="both", expand=True)
            
            error_text = tk.Text(error_frame, height=10, width=60)
            error_text.pack(side="left", fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(error_frame, command=error_text.yview)
            scrollbar.pack(side="right", fill="y")
            error_text.config(yscrollcommand=scrollbar.set)
            
            error_text.insert("1.0", traceback.format_exc())
            
            # 启动错误窗口主循环
            root.mainloop()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有必要的Python包。可以运行: ")
    print(f"pip install -r {project_root}/requirements.txt")

except Exception as e:
    print(f"发生未预期的错误: {e}")
    traceback.print_exc()

print("\n按Enter键退出...")
input()
