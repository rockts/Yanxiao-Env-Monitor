#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时启动文件 - 用于运行完整的仪表盘
"""
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
