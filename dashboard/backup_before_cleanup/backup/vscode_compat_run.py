#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - VS Code兼容启动脚本
解决VS Code终端无法显示Tkinter窗口的问题
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 设置项目根目录和源代码路径
PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = PROJECT_ROOT / "run_simple_dashboard.py"

def is_running_in_vscode():
    """检测是否在VS Code终端中运行"""
    return 'VSCODE_GIT_IPC_HANDLE' in os.environ or 'TERM_PROGRAM' in os.environ and os.environ['TERM_PROGRAM'] == 'vscode'

def main():
    print("检测运行环境...")
    
    # 如果在VS Code中运行，使用外部终端
    if is_running_in_vscode():
        print("检测到VS Code终端环境，将使用系统终端启动图形界面...")
        
        # 获取Python可执行文件路径
        python_exec = sys.executable
        
        # 准备命令
        cmd = [python_exec, str(SCRIPT_PATH)]
        
        # 在macOS上使用open命令
        if platform.system() == 'Darwin':
            print("使用macOS的open命令启动Terminal...")
            
            # 生成shell脚本
            temp_script = PROJECT_ROOT / "temp_launch.sh"
            with open(temp_script, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"cd {PROJECT_ROOT}\n")
                f.write(f"{python_exec} {SCRIPT_PATH}\n")
                f.write('echo "程序已退出，按任意键关闭窗口..."\n')
                f.write("read -n 1\n")
            
            # 添加执行权限
            os.chmod(temp_script, 0o755)
            
            # 使用open命令启动终端并执行脚本
            subprocess.run(["open", "-a", "Terminal", str(temp_script)])
            
            print(f"已在外部Terminal中启动仪表盘。")
            print(f"如果窗口没有出现，请手动执行: python3 {SCRIPT_PATH}")
            
        # 在Windows上使用start命令
        elif platform.system() == 'Windows':
            cmd_str = f'python "{SCRIPT_PATH}"'
            subprocess.run(["start", "cmd", "/k", cmd_str], shell=True)
            
        # 在Linux上尝试使用xterm或gnome-terminal
        elif platform.system() == 'Linux':
            try:
                subprocess.run(["xterm", "-e", f"python3 {SCRIPT_PATH}; read -n 1"])
            except FileNotFoundError:
                try:
                    subprocess.run(["gnome-terminal", "--", "bash", "-c", f"python3 {SCRIPT_PATH}; read -n 1"])
                except FileNotFoundError:
                    print("无法找到合适的终端模拟器，请手动在系统终端中运行脚本:")
                    print(f"python3 {SCRIPT_PATH}")
        
    # 在普通终端中直接运行
    else:
        print("在普通终端环境中，直接启动仪表盘...")
        # 导入主脚本并执行
        sys.path.insert(0, str(PROJECT_ROOT))
        from run_simple_dashboard import main as dashboard_main
        dashboard_main()

if __name__ == "__main__":
    main()
