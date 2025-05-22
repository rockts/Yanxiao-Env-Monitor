#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - VS Code 终端桥接脚本
自动检测VS Code终端环境并在必要时启动外部终端
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# 设置项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent

def is_vscode_terminal():
    """检测是否在VS Code终端中运行"""
    env_vars = ['VSCODE_GIT_IPC_HANDLE', 'VSCODE_IPC_HOOK', 'TERM_PROGRAM']
    return any(var in os.environ and ('vscode' in os.environ[var].lower() if var in os.environ else False) for var in env_vars)

def get_dashboard_script_path():
    """获取仪表盘主脚本路径"""
    return PROJECT_ROOT / "run_simple_dashboard.py"

def create_temp_script():
    """创建临时启动脚本"""
    script_path = PROJECT_ROOT / "temp_launch.command"
    dashboard_path = get_dashboard_script_path()
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"cd \"{PROJECT_ROOT}\"\n")
        f.write("echo \"=====================================\"\n")
        f.write("echo \"智慧校园环境监测系统启动中...\"\n")
        f.write("echo \"=====================================\"\n")
        f.write(f"python3 \"{dashboard_path}\"\n")
        f.write("\necho \"程序已退出，按回车键关闭此窗口...\"\n")
        f.write("read\n")
    
    # 设置可执行权限
    os.chmod(script_path, 0o755)
    return script_path

def main():
    print("智慧校园环境监测系统 - 启动器")
    
    # 检测是否在VS Code终端中运行
    if is_vscode_terminal():
        print("检测到VS Code终端环境...")
        
        if platform.system() == "Darwin":  # macOS
            print("在外部Terminal中启动仪表盘...")
            temp_script = create_temp_script()
            
            # 使用macOS的open命令在Terminal中运行脚本
            try:
                subprocess.run(["open", "-a", "Terminal", str(temp_script)])
                print("已在系统Terminal中启动仪表盘，请查看新打开的窗口。")
            except Exception as e:
                print(f"启动外部终端失败: {e}")
                print("请尝试直接在系统Terminal中运行:")
                print(f"cd {PROJECT_ROOT} && python3 run_simple_dashboard.py")
        
        elif platform.system() == "Windows":  # Windows
            print("在Windows命令提示符中启动仪表盘...")
            dashboard_path = get_dashboard_script_path()
            
            try:
                cmd = f'start cmd /k "cd /d {PROJECT_ROOT} && python {dashboard_path} && pause"'
                subprocess.run(cmd, shell=True)
                print("已在系统命令提示符中启动仪表盘，请查看新打开的窗口。")
            except Exception as e:
                print(f"启动外部终端失败: {e}")
                print("请尝试直接在系统命令提示符中运行:")
                print(f"cd {PROJECT_ROOT} && python run_simple_dashboard.py")
        
        else:  # Linux等其他系统
            print("尝试在外部终端中启动仪表盘...")
            dashboard_path = get_dashboard_script_path()
            
            try:
                for terminal in ["gnome-terminal", "xterm", "konsole"]:
                    try:
                        if terminal == "gnome-terminal":
                            subprocess.run([terminal, "--", "bash", "-c", 
                                           f"cd {PROJECT_ROOT} && python3 {dashboard_path}; echo '程序已退出，按回车键关闭窗口...'; read"])
                        else:
                            subprocess.run([terminal, "-e", 
                                           f"bash -c 'cd {PROJECT_ROOT} && python3 {dashboard_path}; echo \"程序已退出，按回车键关闭窗口...\"; read'"])
                        print(f"已在{terminal}中启动仪表盘，请查看新打开的窗口。")
                        break
                    except FileNotFoundError:
                        continue
                else:
                    raise Exception("未找到可用的终端模拟器")
            except Exception as e:
                print(f"启动外部终端失败: {e}")
                print("请尝试直接在系统终端中运行:")
                print(f"cd {PROJECT_ROOT} && python3 run_simple_dashboard.py")
    
    else:
        print("在标准终端环境中运行仪表盘...")
        # 直接导入并运行仪表盘
        sys.path.insert(0, str(PROJECT_ROOT))
        
        try:
            from run_simple_dashboard import main as run_dashboard
            run_dashboard()
        except Exception as e:
            print(f"启动仪表盘失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
