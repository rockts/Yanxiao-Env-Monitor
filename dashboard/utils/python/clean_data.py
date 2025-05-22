#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 数据清理工具
用于清理旧的传感器数据日志和临时文件
"""

import os
import sys
import shutil
import datetime
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_cleaner")

def setup_directories():
    """确保必要的目录结构存在"""
    # 获取当前脚本目录
    script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    base_dir = script_dir.parent
    
    # 创建必要的目录
    dirs = [
        base_dir / "data" / "sensor_logs",
        base_dir / "logs",
        base_dir / "backup",
        base_dir / "archive"
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    return base_dir

def clean_sensor_logs(days=7):
    """清理超过指定天数的传感器数据日志
    
    Args:
        days (int): 保留最近几天的日志
    """
    base_dir = setup_directories()
    sensor_logs_dir = base_dir / "data" / "sensor_logs"
    
    # 如果目录不存在，无需清理
    if not sensor_logs_dir.exists():
        logger.warning(f"传感器日志目录不存在: {sensor_logs_dir}")
        return 0
    
    # 计算截止日期
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # 删除旧文件
    count = 0
    for file_path in sensor_logs_dir.glob("*.csv"):
        try:
            # 获取文件修改时间
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 如果文件早于截止日期，删除文件
            if mtime < cutoff_date:
                os.remove(file_path)
                logger.info(f"已删除旧传感器日志: {file_path.name}")
                count += 1
        except Exception as e:
            logger.error(f"处理文件时出错: {file_path}, {e}")
    
    return count

def clean_app_logs(days=30):
    """清理超过指定天数的应用程序日志
    
    Args:
        days (int): 保留最近几天的日志
    """
    base_dir = setup_directories()
    app_logs_dir = base_dir / "logs"
    
    # 如果目录不存在，无需清理
    if not app_logs_dir.exists():
        logger.warning(f"日志目录不存在: {app_logs_dir}")
        return 0
    
    # 计算截止日期
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # 删除旧文件
    count = 0
    for file_path in app_logs_dir.glob("*.log"):
        try:
            # 获取文件修改时间
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 如果文件早于截止日期，删除文件
            if mtime < cutoff_date:
                os.remove(file_path)
                logger.info(f"已删除旧应用程序日志: {file_path.name}")
                count += 1
        except Exception as e:
            logger.error(f"处理文件时出错: {file_path}, {e}")
    
    return count

def clean_tmp_files():
    """清理临时文件"""
    base_dir = setup_directories()
    
    # 临时文件模式列表
    tmp_patterns = ["*.tmp", "*.bak", "*.pyc", "__pycache__"]
    
    # 删除匹配的临时文件
    count = 0
    for pattern in tmp_patterns:
        for file_path in Path(base_dir).glob(f"**/{pattern}"):
            try:
                if file_path.is_file():
                    os.remove(file_path)
                    logger.info(f"已删除临时文件: {file_path}")
                    count += 1
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    logger.info(f"已删除临时目录: {file_path}")
                    count += 1
            except Exception as e:
                logger.error(f"删除文件/目录时出错: {file_path}, {e}")
    
    return count

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智慧校园环境监测系统 - 数据清理工具')
    parser.add_argument('--sensor-days', type=int, default=7,
                        help='保留最近几天的传感器日志 (默认: 7)')
    parser.add_argument('--app-days', type=int, default=30,
                        help='保留最近几天的应用程序日志 (默认: 30)')
    parser.add_argument('--no-sensor-logs', action='store_true',
                        help='不清理传感器日志')
    parser.add_argument('--no-app-logs', action='store_true',
                        help='不清理应用程序日志')
    parser.add_argument('--no-tmp-files', action='store_true',
                        help='不清理临时文件')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  智慧校园环境监测系统 - 数据清理工具")
    print("=" * 60)
    
    # 统计清理的文件数量
    total_count = 0
    
    if not args.no_sensor_logs:
        count = clean_sensor_logs(args.sensor_days)
        print(f"已清理 {count} 个传感器日志文件 (保留最近 {args.sensor_days} 天)")
        total_count += count
    
    if not args.no_app_logs:
        count = clean_app_logs(args.app_days)
        print(f"已清理 {count} 个应用程序日志文件 (保留最近 {args.app_days} 天)")
        total_count += count
    
    if not args.no_tmp_files:
        count = clean_tmp_files()
        print(f"已清理 {count} 个临时文件")
        total_count += count
    
    print("=" * 60)
    print(f"总共清理了 {total_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
