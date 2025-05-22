#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
提供统一的日志记录功能
"""

import os
import logging
from datetime import datetime
from pathlib import Path

class LogManager:
    """日志管理类，负责配置和提供日志记录功能"""
    
    _instance = None
    _logger = None
    
    def __new__(cls, log_level=logging.INFO):
        """单例模式，确保全局只有一个日志管理器实例"""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._setup_logging(log_level)
        return cls._instance
    
    def _setup_logging(self, log_level):
        """配置日志系统"""
        try:
            # 确定日志文件路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(script_dir)
            log_dir = os.path.join(base_dir, "logs")
            
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)
            
            # 创建日志文件名，包含日期和时间
            log_file = os.path.join(log_dir, f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            
            # 配置日志
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s [%(levelname)s] %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
            self._logger = logging.getLogger("smart_campus_dashboard")
            self._logger.info("日志系统已初始化")
            self._logger.info(f"日志文件: {log_file}")
            
        except Exception as e:
            # 如果日志设置失败，确保至少有控制台输出
            logging.basicConfig(
                level=logging.WARNING,
                format='%(asctime)s [%(levelname)s] %(message)s',
                handlers=[logging.StreamHandler()]
            )
            self._logger = logging.getLogger("smart_campus_dashboard")
            self._logger.error(f"设置日志系统时出错: {e}")
    
    def get_logger(self):
        """获取日志记录器"""
        return self._logger or logging.getLogger("smart_campus_dashboard")
    
    def set_level(self, level):
        """设置日志级别"""
        if self._logger:
            self._logger.setLevel(level)
            self._logger.info(f"日志级别已更改为: {logging.getLevelName(level)}")

# 导出单例实例和便捷的日志函数，方便其他模块导入使用
log_manager = LogManager()
logger = log_manager.get_logger()

# 导出便捷的日志函数
def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)

if __name__ == "__main__":
    # 日志测试代码
    info("这是一条信息日志")
    debug("这是一条调试日志")
    warning("这是一条警告日志")
    error("这是一条错误日志")
    critical("这是一条严重错误日志")
