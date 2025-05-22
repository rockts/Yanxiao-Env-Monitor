#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件加载工具
用于加载和管理智慧校园环境监测系统配置
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("config_loader")

class ConfigLoader:
    """配置加载器，用于读取和管理配置文件"""
    
    def __init__(self, config_path=None):
        """初始化配置加载器
        
        Args:
            config_path (str, optional): 配置文件路径. 如果为None，使用默认路径
        """
        # 若未指定配置文件，使用默认路径
        if config_path is None:
            # 获取当前脚本目录
            script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
            # 配置文件默认在config子目录中
            config_path = script_dir.parent / "config" / "default_config.json"
        
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """从文件中加载配置"""
        try:
            logger.info(f"正在加载配置文件: {self.config_path}")
            
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                logger.warning(f"配置文件不存在: {self.config_path}")
                self.config = {}
                return
            
            # 打开并解析JSON配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info("配置文件加载成功")
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}")
            # 设置为空配置，避免程序崩溃
            self.config = {}
    
    def get(self, section, key, default=None):
        """获取配置值，如果不存在则返回默认值
        
        Args:
            section (str): 配置节名称
            key (str): 配置项键名
            default: 如果配置不存在，返回的默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    def get_section(self, section, default=None):
        """获取整个配置节
        
        Args:
            section (str): 配置节名称
            default: 如果配置节不存在，返回的默认值
            
        Returns:
            配置节字典或默认值
        """
        try:
            return self.config.get(section, default if default is not None else {})
        except:
            return default if default is not None else {}
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 保存配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            logger.info(f"配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置时出错: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s [%(levelname)s] %(message)s')
    
    # 实例化并加载配置
    config = ConfigLoader()
    
    # 获取MQTT代理主机
    mqtt_host = config.get("mqtt", "broker_host", "localhost")
    print(f"MQTT代理主机: {mqtt_host}")
    
    # 获取整个传感器配置
    sensors = config.get_section("sensors")
    print(f"传感器配置: {sensors}")
