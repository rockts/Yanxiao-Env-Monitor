#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
警报管理工具
用于管理智慧校园环境监测系统警报和阈值
"""

import logging

logger = logging.getLogger("alert_manager")

class AlertManager:
    """警报管理器，用于监控和管理传感器阈值警报"""
    
    def __init__(self, sensor_config=None):
        """初始化警报管理器
        
        Args:
            sensor_config (dict, optional): 传感器配置，包含警告和临界阈值
        """
        self.sensor_config = sensor_config or {}
        self.current_alerts = {}  # 当前活动的警报
        
        logger.info("警报管理器初始化完成")
    
    def update_config(self, sensor_config):
        """更新传感器配置
        
        Args:
            sensor_config (dict): 传感器配置
        """
        self.sensor_config = sensor_config
        logger.info("警报管理器配置已更新")
    
    def check_threshold(self, sensor_name, value):
        """检查传感器值是否超过阈值
        
        Args:
            sensor_name (str): 传感器名称
            value (str): 传感器值
            
        Returns:
            tuple: (状态, 警报级别) 
                  状态: "正常", "警告", "危险"
                  警报级别: 0=正常, 1=警告, 2=危险
        """
        # 如果没有配置，返回正常
        if sensor_name not in self.sensor_config:
            return "正常", 0
        
        # 获取传感器配置
        config = self.sensor_config.get(sensor_name, {})
        warning_threshold = config.get("warning_threshold", None)
        critical_threshold = config.get("critical_threshold", None)
        
        # 如果没有设置阈值，返回正常
        if warning_threshold is None and critical_threshold is None:
            return "正常", 0
        
        try:
            # 尝试转换为浮点数进行比较
            value_float = float(value)
            
            # 检查临界阈值
            if critical_threshold is not None and value_float >= critical_threshold:
                self.current_alerts[sensor_name] = ("危险", 2)
                return "危险", 2
            
            # 检查警告阈值
            if warning_threshold is not None and value_float >= warning_threshold:
                self.current_alerts[sensor_name] = ("警告", 1)
                return "警告", 1
            
            # 值正常，清除警报
            if sensor_name in self.current_alerts:
                del self.current_alerts[sensor_name]
            
            return "正常", 0
        except (ValueError, TypeError):
            # 无法转换为浮点数，返回正常
            logger.warning(f"无法解析传感器值: {sensor_name}={value}")
            return "正常", 0
    
    def get_alert_color(self, sensor_name, value):
        """根据传感器值获取警报颜色
        
        Args:
            sensor_name (str): 传感器名称
            value (str): 传感器值
            
        Returns:
            str: 颜色代码
        """
        status, level = self.check_threshold(sensor_name, value)
        
        if level == 2:  # 危险
            return "#FF0000"  # 红色
        elif level == 1:  # 警告
            return "#FFA500"  # 橙色
        else:  # 正常
            return "#4CAF50"  # 绿色
    
    def get_active_alerts(self):
        """获取当前活动的警报
        
        Returns:
            dict: {传感器名称: (状态, 级别)}
        """
        return self.current_alerts
    
    def get_alert_message(self, sensor_name, value):
        """获取警报消息
        
        Args:
            sensor_name (str): 传感器名称
            value (str): 传感器值
            
        Returns:
            str: 警报消息
        """
        status, level = self.check_threshold(sensor_name, value)
        
        if sensor_name not in self.sensor_config:
            return ""
        
        config = self.sensor_config.get(sensor_name, {})
        display_name = config.get("display", sensor_name)
        unit = config.get("unit", "")
        
        if level == 2:  # 危险
            return f"{display_name}值过高 ({value}{unit})，超过危险阈值!"
        elif level == 1:  # 警告
            return f"{display_name}值偏高 ({value}{unit})，请注意监控"
        else:
            return ""

# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s [%(levelname)s] %(message)s')
    
    # 示例传感器配置
    sample_config = {
        "环境温度": {"display": "温度", "unit": "°C", "warning_threshold": 28, "critical_threshold": 32},
        "环境湿度": {"display": "湿度", "unit": "%RH", "warning_threshold": 75, "critical_threshold": 85}
    }
    
    # 实例化警报管理器
    alert_mgr = AlertManager(sample_config)
    
    # 测试不同的值
    print(alert_mgr.check_threshold("环境温度", "26.5"))  # 正常
    print(alert_mgr.check_threshold("环境温度", "29.2"))  # 警告
    print(alert_mgr.check_threshold("环境温度", "33.5"))  # 危险
    
    print(alert_mgr.get_alert_color("环境温度", "26.5"))  # 绿色
    print(alert_mgr.get_alert_message("环境温度", "33.5"))  # 危险消息
