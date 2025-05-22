#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
传感器数据记录工具
用于记录和管理智慧校园环境监测系统传感器数据
"""

import os
import csv
import json
import time
import datetime
import logging
from pathlib import Path

logger = logging.getLogger("data_logger")

class SensorDataLogger:
    """传感器数据记录器，用于记录和管理传感器数据"""
    
    def __init__(self, log_dir=None, max_days=7):
        """初始化数据记录器
        
        Args:
            log_dir (str, optional): 日志目录路径. 如果为None，使用默认路径
            max_days (int): 保留日志文件的最大天数
        """
        # 若未指定日志目录，使用默认路径
        if log_dir is None:
            # 获取当前脚本目录
            script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
            # 日志默认在data/sensor_logs子目录中
            log_dir = script_dir.parent / "data" / "sensor_logs"
        
        self.log_dir = Path(log_dir)
        self.max_days = max_days
        
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"数据记录器初始化，日志目录: {self.log_dir}")
        
        # 清理旧日志文件
        self.cleanup_old_logs()
    
    def log_sensor_data(self, sensor_data):
        """记录传感器数据到CSV文件
        
        Args:
            sensor_data (dict): 传感器数据，格式为 {传感器名: 数值}
        """
        try:
            # 获取当前日期作为文件名
            today = datetime.date.today().strftime("%Y-%m-%d")
            log_file = self.log_dir / f"sensor_data_{today}.csv"
            
            # 获取当前时间
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 检查文件是否已存在
            file_exists = log_file.exists()
            
            # 打开文件并写入数据
            with open(log_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp'] + list(sensor_data.keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 如果是新文件，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 准备数据行
                row_data = {'timestamp': current_time}
                row_data.update(sensor_data)
                
                # 写入数据
                writer.writerow(row_data)
            
            logger.debug(f"传感器数据已记录到: {log_file}")
            return True
        except Exception as e:
            logger.error(f"记录传感器数据时出错: {e}")
            return False
    
    def cleanup_old_logs(self):
        """清理超过最大保留天数的旧日志文件"""
        try:
            # 获取所有日志文件
            log_files = list(self.log_dir.glob("sensor_data_*.csv"))
            
            # 计算截止日期
            cutoff_date = datetime.date.today() - datetime.timedelta(days=self.max_days)
            
            # 遍历并删除旧文件
            for log_file in log_files:
                try:
                    # 从文件名中提取日期
                    file_date_str = log_file.name.replace("sensor_data_", "").replace(".csv", "")
                    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    
                    # 如果文件日期早于截止日期，删除文件
                    if file_date < cutoff_date:
                        os.remove(log_file)
                        logger.info(f"已删除旧日志文件: {log_file}")
                except Exception as e:
                    logger.warning(f"处理日志文件时出错: {log_file}, {e}")
        except Exception as e:
            logger.error(f"清理旧日志文件时出错: {e}")
    
    def get_sensor_history(self, sensor_name, days=1):
        """获取指定传感器的历史数据
        
        Args:
            sensor_name (str): 传感器名称
            days (int): 获取多少天的历史数据
            
        Returns:
            list: 数据点列表，每个元素为 [timestamp, value]
        """
        try:
            history_data = []
            
            # 计算开始日期
            start_date = datetime.date.today() - datetime.timedelta(days=days-1)
            
            # 遍历日期范围内的所有日志文件
            for day_offset in range(days):
                date = start_date + datetime.timedelta(days=day_offset)
                date_str = date.strftime("%Y-%m-%d")
                log_file = self.log_dir / f"sensor_data_{date_str}.csv"
                
                # 如果文件存在，读取数据
                if log_file.exists():
                    with open(log_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if sensor_name in row:
                                # 添加数据点 [timestamp, value]
                                history_data.append([
                                    row['timestamp'],
                                    row.get(sensor_name, "")
                                ])
            
            return history_data
        except Exception as e:
            logger.error(f"获取传感器历史数据时出错: {e}")
            return []

# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s [%(levelname)s] %(message)s')
    
    # 实例化数据记录器
    data_logger = SensorDataLogger()
    
    # 记录样本数据
    sample_data = {
        "环境温度": "25.3",
        "环境湿度": "65.7",
        "aqi": "48",
        "噪音": "42.1"
    }
    
    data_logger.log_sensor_data(sample_data)
    
    # 获取温度历史数据
    temp_history = data_logger.get_sensor_history("环境温度", days=3)
    print(f"温度历史数据: {temp_history}")
