#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 配置文件优化工具
检查、修复和优化配置文件
"""

import os
import sys
import json
import shutil
from pathlib import Path
import datetime

def print_header():
    """打印标题"""
    print("\n" + "="*60)
    print("     智慧校园环境监测系统 - 配置文件优化工具     ")
    print("="*60)
    print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

def get_project_paths():
    """获取项目路径"""
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    config_dir = project_root / "config"
    src_path = project_root / "src"
    
    return {
        "script_path": script_path,
        "project_root": project_root,
        "config_dir": config_dir,
        "src_path": src_path
    }

def check_config_dir(paths):
    """检查并创建配置目录"""
    config_dir = paths["config_dir"]
    if not config_dir.exists():
        print(f"配置目录不存在，创建: {config_dir}")
        config_dir.mkdir(parents=True, exist_ok=True)
        return False
    
    print(f"配置目录存在: {config_dir}")
    return True

def get_default_config():
    """返回默认配置"""
    return {
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
        "mqtt_broker_host": "localhost",
        "mqtt_broker_port": 1883,
        "siot_username": "siot",
        "siot_password": "dfrobot",
        "mqtt_client_id": "smart_campus_dashboard",
        "mqtt_topics": [
            "siot/环境温度", "siot/环境湿度", "siot/aqi", "siot/tvoc", "siot/eco2",
            "siot/紫外线指数", "siot/uv风险等级", "siot/噪音"
        ]
    }

def backup_config_file(config_file):
    """备份配置文件"""
    if not config_file.exists():
        return False
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = config_file.with_name(f"{config_file.stem}_backup_{timestamp}{config_file.suffix}")
    
    try:
        shutil.copy2(config_file, backup_file)
        print(f"已备份配置文件: {backup_file}")
        return True
    except Exception as e:
        print(f"备份配置文件失败: {e}")
        return False

def check_and_fix_config_file(paths):
    """检查并修复配置文件"""
    config_dir = paths["config_dir"]
    config_file = config_dir / "config.json"
    
    # 检查配置文件是否存在
    if not config_file.exists():
        print(f"配置文件不存在，创建默认配置: {config_file}")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)
        print("已创建默认配置")
        return True
    
    # 备份当前配置
    backup_config_file(config_file)
    
    # 读取当前配置
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            current_config = json.load(f)
        print("成功读取当前配置")
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        print("创建新的默认配置")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)
        return True
    
    # 获取默认配置作为参考
    default_config = get_default_config()
    
    # 检查并修复配置
    fixed = False
    
    # 检查顶级键
    for key, value in default_config.items():
        if key not in current_config:
            print(f"添加缺失的配置项: {key}")
            current_config[key] = value
            fixed = True
    
    # 检查mqtt部分
    if "mqtt" in current_config:
        for key, value in default_config["mqtt"].items():
            if key not in current_config["mqtt"]:
                print(f"添加缺失的MQTT配置项: {key}")
                current_config["mqtt"][key] = value
                fixed = True
    
    # 检查logging部分
    if "logging" in current_config:
        for key, value in default_config["logging"].items():
            if key not in current_config["logging"]:
                print(f"添加缺失的日志配置项: {key}")
                current_config["logging"][key] = value
                fixed = True
    
    # 检查ui部分
    if "ui" in current_config:
        for key, value in default_config["ui"].items():
            if key not in current_config["ui"]:
                print(f"添加缺失的UI配置项: {key}")
                current_config["ui"][key] = value
                fixed = True
    
    # 检查simulator部分
    if "simulator" in current_config:
        for key, value in default_config["simulator"].items():
            if key not in current_config["simulator"]:
                print(f"添加缺失的模拟器配置项: {key}")
                current_config["simulator"][key] = value
                fixed = True
    
    # 检查mqtt_topics字段
    if "mqtt_topics" not in current_config or not current_config["mqtt_topics"]:
        print("添加缺失的MQTT主题列表")
        current_config["mqtt_topics"] = default_config["mqtt_topics"]
        fixed = True
    
    # 保存修复后的配置
    if fixed:
        print("修复了配置文件，保存更新")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(current_config, f, ensure_ascii=False, indent=2)
        print("配置文件已更新")
        return True
    else:
        print("配置文件检查完成，未发现问题")
        return False

def check_config_compatibility(paths):
    """检查配置文件兼容性"""
    config_dir = paths["config_dir"]
    
    # 检查可能存在的其他配置文件
    config_files = [
        config_dir / "config.json",
        config_dir / "config_new.json",
        config_dir / "local_config.json"
    ]
    
    found_files = []
    for file in config_files:
        if file.exists():
            found_files.append(file)
    
    if len(found_files) <= 1:
        print("仅发现一个配置文件，无需处理兼容性问题")
        return
    
    print(f"发现多个配置文件: {', '.join(str(f) for f in found_files)}")
    print("检查配置文件兼容性并合并...")
    
    # 以config.json为主，合并其他配置文件的内容
    main_config_file = config_dir / "config.json"
    if not main_config_file.exists():
        print(f"主配置文件不存在，创建: {main_config_file}")
        with open(main_config_file, "w", encoding="utf-8") as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)
    
    try:
        with open(main_config_file, "r", encoding="utf-8") as f:
            main_config = json.load(f)
    except Exception as e:
        print(f"读取主配置文件失败: {e}")
        print("使用默认配置")
        main_config = get_default_config()
    
    # 合并其他配置文件
    merged = False
    for file in found_files:
        if file == main_config_file:
            continue
        
        try:
            with open(file, "r", encoding="utf-8") as f:
                other_config = json.load(f)
            
            print(f"合并配置文件: {file}")
            
            # 合并顶级键
            for key, value in other_config.items():
                if key not in main_config or not main_config[key]:
                    main_config[key] = value
                    merged = True
                    print(f"  合并配置项: {key}")
            
            # 特别处理嵌套对象
            for section in ["mqtt", "logging", "ui", "simulator"]:
                if section in other_config and section in main_config:
                    for key, value in other_config[section].items():
                        if key not in main_config[section] or not main_config[section][key]:
                            main_config[section][key] = value
                            merged = True
                            print(f"  合并嵌套配置项: {section}.{key}")
        
        except Exception as e:
            print(f"处理配置文件 {file} 时出错: {e}")
    
    # 保存合并后的配置
    if merged:
        print("保存合并后的配置")
        with open(main_config_file, "w", encoding="utf-8") as f:
            json.dump(main_config, f, ensure_ascii=False, indent=2)
        print("配置已合并")
    else:
        print("无需合并配置")

def main():
    """主函数"""
    print_header()
    
    paths = get_project_paths()
    print(f"项目根目录: {paths['project_root']}")
    
    # 检查并创建配置目录
    check_config_dir(paths)
    
    # 检查多个配置文件的兼容性
    check_config_compatibility(paths)
    
    # 检查并修复配置文件
    check_and_fix_config_file(paths)
    
    print("\n" + "="*60)
    print("配置文件优化完成!")
    print("="*60 + "\n")
    
    print("按回车键退出...")
    input()

if __name__ == "__main__":
    main()
