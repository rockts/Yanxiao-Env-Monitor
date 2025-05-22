#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 数据清理工具
用于清理旧的日志文件和数据记录
"""

import os
import datetime
import logging
import argparse
import shutil
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

def cleanup_old_logs(log_dir, max_days=7, create_backup=True):
    """清理超过最大保留天数的旧日志文件
    
    Args:
        log_dir (str): 日志目录路径
        max_days (int): 保留日志文件的最大天数
        create_backup (bool): 是否创建备份而不是删除
    
    Returns:
        int: 处理的文件数量
    """
    try:
        # 确保目录存在
        log_dir = Path(log_dir)
        if not log_dir.exists():
            logger.warning(f"目录不存在: {log_dir}")
            return 0
        
        # 计算截止日期
        cutoff_date = datetime.date.today() - datetime.timedelta(days=max_days)
        logger.info(f"清理 {max_days} 天之前的日志 (早于 {cutoff_date})")
        
        # 准备备份目录
        backup_dir = None
        if create_backup:
            backup_dir = log_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            logger.info(f"备份目录: {backup_dir}")
        
        # 统计
        processed_count = 0
        
        # 处理传感器数据日志
        sensor_log_pattern = "sensor_data_*.csv"
        for log_file in log_dir.glob(sensor_log_pattern):
            try:
                # 从文件名中提取日期
                file_date_str = log_file.name.replace("sensor_data_", "").replace(".csv", "")
                file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                
                # 如果文件日期早于截止日期，处理文件
                if file_date < cutoff_date:
                    if create_backup:
                        # 复制到备份目录
                        shutil.copy2(log_file, backup_dir / log_file.name)
                        logger.info(f"已备份: {log_file.name}")
                    
                    # 删除原文件
                    os.remove(log_file)
                    logger.info(f"已删除: {log_file.name}")
                    processed_count += 1
            except Exception as e:
                logger.warning(f"处理文件出错 {log_file}: {e}")
        
        # 处理应用日志
        app_log_pattern = "dashboard_*.log"
        for log_file in log_dir.glob(app_log_pattern):
            try:
                # 从文件名中提取日期
                file_date_str = log_file.name.replace("dashboard_", "").split("_")[0]
                file_date = datetime.datetime.strptime(file_date_str, "%Y%m%d").date()
                
                # 如果文件日期早于截止日期，处理文件
                if file_date < cutoff_date:
                    if create_backup:
                        # 复制到备份目录
                        shutil.copy2(log_file, backup_dir / log_file.name)
                        logger.info(f"已备份: {log_file.name}")
                    
                    # 删除原文件
                    os.remove(log_file)
                    logger.info(f"已删除: {log_file.name}")
                    processed_count += 1
            except Exception as e:
                logger.warning(f"处理文件出错 {log_file}: {e}")
        
        logger.info(f"总共处理了 {processed_count} 个文件")
        return processed_count
    
    except Exception as e:
        logger.error(f"清理日志文件时出错: {e}")
        return 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智慧校园环境监测系统 - 数据清理工具')
    parser.add_argument('--days', type=int, default=7, help='保留的天数')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份')
    parser.add_argument('--logs-dir', type=str, help='日志目录路径')
    parser.add_argument('--data-dir', type=str, help='数据目录路径')
    args = parser.parse_args()
    
    # 确定日志目录
    if args.logs_dir:
        logs_dir = Path(args.logs_dir)
    else:
        # 获取脚本所在目录
        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        project_root = script_dir.parent
        logs_dir = project_root / "logs"
    
    # 确定数据目录
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        # 获取脚本所在目录
        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        project_root = script_dir.parent
        data_dir = project_root / "data" / "sensor_logs"
    
    logger.info(f"日志目录: {logs_dir}")
    logger.info(f"数据目录: {data_dir}")
    
    # 清理日志
    logger.info("开始清理日志...")
    count1 = cleanup_old_logs(logs_dir, args.days, not args.no_backup)
    
    # 清理传感器数据
    logger.info("开始清理传感器数据...")
    count2 = cleanup_old_logs(data_dir, args.days, not args.no_backup)
    
    logger.info(f"清理完成，总共处理了 {count1 + count2} 个文件")

if __name__ == "__main__":
    main()
