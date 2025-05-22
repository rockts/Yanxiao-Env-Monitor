#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 诊断工具
检查系统配置并测试关键组件是否正常工作
"""

import os
import sys
import platform
import subprocess
import importlib
import socket
import datetime
from pathlib import Path
import time

# 美化输出的颜色定义
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """打印标题"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}{Colors.BLUE}     智慧校园环境监测系统 - 诊断工具     {Colors.ENDC}")
    print("="*60)
    print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print("="*60 + "\n")

def check_python_version():
    """检查Python版本"""
    print(f"{Colors.BOLD}[1] 检查Python版本{Colors.ENDC}")
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"{Colors.GREEN}✓ Python版本正常: {sys.version}{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}✗ Python版本过低: {sys.version}{Colors.ENDC}")
        print(f"{Colors.YELLOW}  推荐使用Python 3.7或更高版本{Colors.ENDC}")
        return False

def check_dependencies():
    """检查依赖库"""
    print(f"\n{Colors.BOLD}[2] 检查依赖库{Colors.ENDC}")
    dependencies = [
        ("tkinter", "GUI界面"),
        ("paho.mqtt.client", "MQTT通信"),
        ("matplotlib", "图表绘制"),
        ("PIL", "图像处理"),
        ("json", "JSON处理"),
        ("requests", "网络请求")
    ]
    
    all_ok = True
    for module, desc in dependencies:
        try:
            if module == "PIL":
                importlib.import_module("PIL.Image")
            else:
                importlib.import_module(module)
            print(f"{Colors.GREEN}✓ {module:<15} 已安装 ({desc}){Colors.ENDC}")
        except ImportError:
            print(f"{Colors.RED}✗ {module:<15} 未安装 ({desc}){Colors.ENDC}")
            if module == "paho.mqtt.client":
                print(f"{Colors.YELLOW}  请运行: pip install paho-mqtt{Colors.ENDC}")
            elif module == "PIL":
                print(f"{Colors.YELLOW}  请运行: pip install Pillow{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}  请运行: pip install {module.split('.')[0]}{Colors.ENDC}")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """检查文件结构"""
    print(f"\n{Colors.BOLD}[3] 检查文件结构{Colors.ENDC}")
    
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    src_path = project_root / "src"
    
    print(f"项目根目录: {project_root}")
    
    # 检查关键文件
    files_to_check = [
        (src_path / "main.py", "主程序"),
        (src_path / "simple_mqtt_broker.py", "MQTT服务器"),
        (src_path / "sensor_data_simulator.py", "数据模拟器") if (src_path / "sensor_data_simulator.py").exists() else 
            (src_path / "simulators" / "sensor_data_simulator.py", "数据模拟器"),
        (project_root / "真完整版启动.py", "启动器"),
        (project_root / "真完整版启动.command", "macOS启动器")
    ]
    
    all_exists = True
    for file_path, desc in files_to_check:
        if file_path.exists():
            print(f"{Colors.GREEN}✓ {file_path.name:<25} 已找到 ({desc}){Colors.ENDC}")
        else:
            print(f"{Colors.RED}✗ {file_path.name:<25} 未找到 ({desc}){Colors.ENDC}")
            all_exists = False
    
    # 检查文件夹
    dirs_to_check = [
        (src_path, "源码目录"),
        (src_path / "ui", "UI目录"),
        (project_root / "logs", "日志目录", True),
        (project_root / "config", "配置目录", True)
    ]
    
    for dir_path, desc, *optional in dirs_to_check:
        is_optional = optional and optional[0]
        if dir_path.exists() and dir_path.is_dir():
            print(f"{Colors.GREEN}✓ {dir_path.name+'/':<25} 已找到 ({desc}){Colors.ENDC}")
        elif is_optional:
            print(f"{Colors.YELLOW}! {dir_path.name+'/':<25} 未找到 ({desc} - 可选){Colors.ENDC}")
        else:
            print(f"{Colors.RED}✗ {dir_path.name+'/':<25} 未找到 ({desc}){Colors.ENDC}")
            all_exists = False
    
    return all_exists

def test_mqtt_server():
    """测试MQTT服务器"""
    print(f"\n{Colors.BOLD}[4] 测试MQTT服务器{Colors.ENDC}")
    
    # 检查端口1883是否已被占用
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1883))
        print(f"{Colors.GREEN}✓ MQTT端口(1883)可连接，服务器可能已在运行{Colors.ENDC}")
        sock.close()
        return True
    except:
        sock.close()
        print(f"{Colors.YELLOW}! MQTT端口(1883)未被占用，尝试启动服务器...{Colors.ENDC}")
    
    # 尝试启动MQTT服务器
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    src_path = project_root / "src"
    mqtt_script = src_path / "simple_mqtt_broker.py"
    
    if not mqtt_script.exists():
        print(f"{Colors.RED}✗ 找不到MQTT服务器脚本: {mqtt_script}{Colors.ENDC}")
        return False
    
    try:
        print(f"{Colors.YELLOW}启动MQTT服务器以测试...{Colors.ENDC}")
        mqtt_process = subprocess.Popen(
            [sys.executable, str(mqtt_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # 等待几秒让服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if mqtt_process.poll() is None:
            print(f"{Colors.GREEN}✓ MQTT服务器启动成功{Colors.ENDC}")
            # 终止进程
            mqtt_process.terminate()
            mqtt_process.wait(timeout=5)
            return True
        else:
            output, _ = mqtt_process.communicate()
            print(f"{Colors.RED}✗ MQTT服务器启动失败:{Colors.ENDC}\n{output}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ 启动MQTT服务器时出错: {e}{Colors.ENDC}")
        return False

def test_config():
    """测试配置文件"""
    print(f"\n{Colors.BOLD}[5] 检查配置文件{Colors.ENDC}")
    
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    config_dir = project_root / "config"
    config_file = config_dir / "config.json"
    
    if not config_dir.exists():
        os.makedirs(config_dir, exist_ok=True)
        print(f"{Colors.YELLOW}! 创建配置目录: {config_dir}{Colors.ENDC}")
    
    if config_file.exists():
        print(f"{Colors.GREEN}✓ 配置文件已存在: {config_file}{Colors.ENDC}")
        # 检查配置文件内容
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 检查关键配置
            if "mqtt" in config and "broker_host" in config["mqtt"]:
                print(f"{Colors.GREEN}✓ MQTT配置正确{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}! MQTT配置不完整{Colors.ENDC}")
            
            if "logging" in config:
                print(f"{Colors.GREEN}✓ 日志配置正确{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}! 日志配置不完整{Colors.ENDC}")
            
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ 读取配置文件时出错: {e}{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.YELLOW}! 配置文件不存在，将创建默认配置{Colors.ENDC}")
        # 创建默认配置
        try:
            import json
            default_config = {
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
                },
                "mqtt_topics": [
                    "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", 
                    "siot/eco2", "siot/紫外线指数", "siot/uv风险等级", "siot/噪音"
                ]
            }
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"{Colors.GREEN}✓ 已创建默认配置文件{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ 创建配置文件时出错: {e}{Colors.ENDC}")
            return False

def print_summary(results):
    """打印诊断摘要"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}诊断摘要{Colors.ENDC}")
    print("="*60)
    
    all_ok = all(results.values())
    
    for test, ok in results.items():
        if ok:
            print(f"{Colors.GREEN}✓ {test:<25} 通过{Colors.ENDC}")
        else:
            print(f"{Colors.RED}✗ {test:<25} 失败{Colors.ENDC}")
    
    print("\n" + "="*60)
    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}所有测试通过! 系统应该可以正常工作。{Colors.ENDC}")
        print(f"\n请使用以下命令启动真·完整版仪表盘:")
        if platform.system() == "Darwin":  # macOS
            print(f"{Colors.BLUE}双击 '真完整版启动.command' 文件{Colors.ENDC}")
        else:
            print(f"{Colors.BLUE}python3 真完整版启动.py{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}存在一些问题需要解决。{Colors.ENDC}")
        print(f"{Colors.YELLOW}请查看上面的错误信息，并解决相应问题后再重新运行诊断。{Colors.ENDC}")
    
    print("="*60 + "\n")

def main():
    """主函数"""
    print_header()
    
    results = {}
    
    # 运行各项测试
    results["Python版本"] = check_python_version()
    results["依赖库"] = check_dependencies()
    results["文件结构"] = check_file_structure()
    results["MQTT服务器"] = test_mqtt_server()
    results["配置文件"] = test_config()
    
    # 打印摘要
    print_summary(results)
    
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()
