#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置快速修复工具 - 确保配置文件正确并能被仪表盘读取
"""

import os
import sys
import json
import shutil
from pathlib import Path

# 获取项目根目录
script_path = Path(__file__).resolve()
project_root = script_path.parent

# 确保配置目录存在
config_dir = project_root / "config"
if not config_dir.exists():
    print(f"创建配置目录: {config_dir}")
    os.makedirs(config_dir, exist_ok=True)

# 配置文件路径
config_file = config_dir / "config.json"
local_config_file = config_dir / "local_config.json"

# 默认配置
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
        "window_size": "800x600",
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

# 本地测试配置
local_config = {
    "mqtt_broker_host": "localhost", 
    "mqtt_broker_port": 1883,
    "siot_username": "siot",
    "siot_password": "dfrobot",
    "mqtt_client_id": "smart_campus_dashboard_test"
}

# 创建或更新配置文件
if config_file.exists():
    print(f"配置文件已存在: {config_file}")
    # 读取当前配置，确保不丢失用户设置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            existing_config = json.load(f)
        
        # 备份现有配置
        backup_file = config_dir / f"config_backup_{Path(__file__).stem}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        print(f"已备份现有配置到: {backup_file}")
        
        # 更新缺失的配置项
        for key, value in default_config.items():
            if key not in existing_config:
                existing_config[key] = value
                print(f"添加了缺失的配置项: {key}")
        
        # 写回更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        print(f"已更新配置文件: {config_file}")
    except Exception as e:
        print(f"读取或更新配置文件时出错: {e}")
        print(f"创建新的配置文件...")
        # 如果出错，创建新配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
else:
    print(f"创建新的配置文件: {config_file}")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

# 创建本地配置文件（用于本地测试）
if not local_config_file.exists():
    print(f"创建本地测试配置文件: {local_config_file}")
    with open(local_config_file, 'w', encoding='utf-8') as f:
        json.dump(local_config, f, ensure_ascii=False, indent=2)
else:
    print(f"本地测试配置文件已存在: {local_config_file}")

print("\n配置文件检查完成！")
print(f"标准配置文件: {config_file}")
print(f"本地测试配置: {local_config_file}")
print("\n现在可以尝试启动仪表盘了！")
