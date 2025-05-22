#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 正式仪表盘启动脚本
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path
import json

# 获取脚本所在路径
script_path = Path(__file__).resolve()
project_root = script_path.parent

# 创建时间戳
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 打印诊断信息
print(f"==========================================")
print(f"  烟铺小学智慧校园环境监测系统 - 正式仪表盘  ")
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

# 创建有效的配置文件
config_dir = project_root / "config"
config_file = config_dir / "config.json"

config_data = {
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
    }
}

print(f"确保配置文件有效...")
try:
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    print(f"配置文件已更新: {config_file}")
except Exception as e:
    print(f"警告: 无法更新配置文件: {e}")

# 尝试启动本地MQTT服务器
try:
    print("启动本地MQTT服务器...")
    mqtt_script = project_root / "src" / "services" / "simple_mqtt_broker.py"
    if mqtt_script.exists():
        mqtt_process = subprocess.Popen(
            [sys.executable, str(mqtt_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print("本地MQTT服务器已启动")
    else:
        print(f"警告: 找不到MQTT服务器脚本: {mqtt_script}")
except Exception as e:
    print(f"警告: 启动MQTT服务器失败: {e}")

# 执行仪表盘脚本
dashboard_script = project_root / "src" / "ui" / "dashboard.py"
main_dashboard_script = project_root / "src" / "main_dashboard.py"

if not dashboard_script.exists():
    print(f"错误: 找不到正式仪表盘脚本: {dashboard_script}")
    print(f"尝试使用简化版仪表盘...")
    dashboard_script = project_root / "src" / "ui" / "simple_dashboard.py"

print(f"正在启动仪表盘...")
print(f"尝试使用主入口文件: {main_dashboard_script}")
print()

# 创建一个临时启动文件
temp_launcher = project_root / "temp_run_dashboard.py"
with open(temp_launcher, "w") as f:
    f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
临时启动文件 - 用于运行完整的仪表盘
\"\"\"
import os
import sys
import tkinter as tk
from pathlib import Path

# 获取当前目录并设置为项目根目录
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    # 导入相关模块
    print("导入核心组件...")
    from src.core.config_manager import ConfigManager
    from src.core.log_manager import LogManager
    
    print("导入UI组件...")
    from src.ui.dashboard import SimpleDashboard  # 仪表盘组件
    
    def main():
        print("初始化配置管理器...")
        config_manager = ConfigManager(config_path=str(project_root / 'config' / 'config.json'))
        app_config = config_manager.get_all()
        
        print("初始化日志管理器...")
        log_manager = LogManager(project_root=project_root,
                                log_config=app_config.get('logging', {}))
        logger = log_manager.get_logger("DashboardLauncher")
        
        # 启动UI
        print("创建主窗口...")
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统")
        
        try:
            print("启动仪表盘...")
            app = SimpleDashboard(root)  # 只传递root参数
            logger.info("已成功启动仪表盘")
        except Exception as e:
            logger.error(f"启动仪表盘失败: {e}")
            print(f"仪表盘启动失败: {e}")
            return
        
        print("启动主循环...")
        root.mainloop()
        print("主循环结束")
        
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()
""")

print(f"临时启动文件已创建: {temp_launcher}")
os.chmod(temp_launcher, 0o755)  # 确保可执行

try:
    # 1. 确保脚本有执行权限
    if sys.platform != 'win32':  # 如果不是Windows系统
        try:
            os.chmod(temp_launcher, 0o755)  # 赋予执行权限
        except Exception as e:
            print(f"警告: 无法设置执行权限: {e}")
    
    # 2. 启动数据模拟器
    try:
        print("启动数据模拟器...")
        simulator_script = project_root / "src" / "simulators" / "sensor_data_simulator.py"
        if simulator_script.exists():
            simulator_process = subprocess.Popen(
                [sys.executable, str(simulator_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            print("数据模拟器已启动")
        else:
            print(f"警告: 找不到数据模拟器脚本: {simulator_script}")
    except Exception as e:
        print(f"警告: 启动数据模拟器失败: {e}")
    
    # 3. 建立实时输出的子进程
    print("启动仪表盘进程...")
    
    
    # 创建进程并实时显示输出
    process = subprocess.Popen(
        [sys.executable, str(temp_launcher)],
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
    # 确保关闭所有子进程
    try:
        if 'mqtt_process' in locals():
            mqtt_process.terminate()
            print("MQTT服务器已关闭")
        if 'simulator_process' in locals():
            simulator_process.terminate()
            print("数据模拟器已关闭")
    except Exception as e:
        print(f"关闭子进程时出错: {e}")
    
    print("\n==========================================")
    print("  智慧校园环境监测系统 - 会话已结束")
    print("==========================================")

input("\n按回车键退出...")
