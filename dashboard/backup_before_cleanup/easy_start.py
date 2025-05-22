#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 简单启动脚本
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# 获取脚本所在路径
script_path = Path(__file__).resolve()
project_root = script_path.parent

# 创建时间戳
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 打印诊断信息
print(f"==========================================")
print(f"  烟铺小学智慧校园环境监测系统 - 简易启动器  ")
print(f"==========================================")
print()
print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"启动诊断信息:")
print(f"- 脚本路径: {script_path}")
print(f"- 项目根目录: {project_root}")
print(f"- 当前工作目录: {os.getcwd()}")
print(f"- Python 可执行文件: {sys.executable}")
print(f"- Python 版本: {sys.version.split()[0]}")
print()

# 设置环境变量
os.environ['PYTHONPATH'] = f"{project_root}/src:{project_root}:{os.environ.get('PYTHONPATH', '')}"
print(f"设置PYTHONPATH: {os.environ['PYTHONPATH']}")
print()

# 执行仪表盘脚本
run_script = project_root / "run_simple_dashboard.py"
print(f"正在启动仪表盘...")
print(f"启动脚本: {run_script}")
print()

try:
    # 1. 确保脚本有执行权限
    if sys.platform != 'win32':  # 如果不是Windows系统
        try:
            os.chmod(run_script, 0o755)  # 赋予执行权限
        except Exception as e:
            print(f"警告: 无法设置执行权限: {e}")
    
    # 2. 建立实时输出的子进程
    print("启动仪表盘进程...")
    
    # 创建进程并实时显示输出
    process = subprocess.Popen(
        [sys.executable, str(run_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # 行缓冲
        universal_newlines=True
    )
    
    # 实时显示输出
    print("\n--- 仪表盘输出开始 ---\n")
    for line in process.stdout:
        print(line, end='')  # 实时打印输出
    
    # 等待进程结束
    return_code = process.wait()
    print("\n--- 仪表盘输出结束 ---\n")
    
    if return_code != 0:
        print(f"警告: 仪表盘进程返回非零退出码: {return_code}")
    else:
        print(f"仪表盘进程正常结束，退出码: {return_code}")
        
except subprocess.CalledProcessError as e:
    print(f"执行失败，返回码: {e.returncode}")
    if hasattr(e, 'stdout') and e.stdout:
        print(f"标准输出: {e.stdout}")
    if hasattr(e, 'stderr') and e.stderr:
        print(f"标准错误: {e.stderr}")
except Exception as e:
    print(f"出现错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n==========================================")
    print("  智慧校园环境监测系统 - 会话已结束")
    print("==========================================")

input("\n按回车键退出...")
