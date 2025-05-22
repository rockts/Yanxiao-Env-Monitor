#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟铺小学智慧校园环境监测系统 - 直接启动脚本
绕过启动器直接运行主程序，专为解决启动问题而设计
"""

import os
import sys
import argparse
import datetime
from pathlib import Path

# 设置项目根目录和源代码路径
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

# 创建指示文件以验证脚本执行
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
indicator_file = PROJECT_ROOT / f"direct_run_indicator_{timestamp}.txt"

with open(indicator_file, "w") as f:
    f.write(f"直接启动脚本执行于 {datetime.datetime.now().isoformat()}\n")
    f.write(f"Python可执行文件: {sys.executable}\n")
    f.write(f"当前工作目录: {os.getcwd()}\n")
    f.write(f"项目根目录: {PROJECT_ROOT}\n")
    f.write(f"源代码路径: {SRC_PATH}\n")

print(f"创建了指示文件: {indicator_file}")

# 确保可以导入src目录下的模块
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}:{os.environ.get('PYTHONPATH', '')}"
print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="烟铺小学智慧校园环境监测系统 - 直接启动")
    parser.add_argument("--simple", action="store_true", help="运行简易仪表盘")
    parser.add_argument("--full", action="store_true", help="运行完整仪表盘")
    parser.add_argument("--simulate", action="store_true", help="使用模拟数据")
    parser.add_argument("--local-mqtt", action="store_true", help="使用本地MQTT代理")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 默认使用简易模式
    if not args.simple and not args.full:
        print("未指定仪表盘模式，默认使用简易模式")
        args.simple = True
    
    print(f"命令行参数: {args}")
    
    try:
        # 使用源代码中的core模块
        print("导入核心组件...")
        from src.core.config_manager import ConfigManager
        from src.core.log_manager import LogManager
        
        # 初始化配置和日志
        print("初始化配置管理器...")
        config_manager = ConfigManager(project_root=PROJECT_ROOT)
        app_config = config_manager.get_all()
        
        # 设置程序参数到配置中
        app_config['runtime_args'] = vars(args)
        
        # 添加特定的配置项
        app_config['mqtt_broker_host'] = 'localhost' if args.local_mqtt else app_config.get('mqtt_broker_host', 'localhost')
        app_config['simulate_data'] = args.simulate
        
        print("初始化日志管理器...")
        log_manager = LogManager(project_root=PROJECT_ROOT, log_config=app_config.get("logging", {}))
        logger = log_manager.get_logger("DirectRun")
        
        logger.info("使用直接启动脚本启动应用程序")
        logger.info(f"命令行参数: {args}")
        
        if args.simple:
            # 直接运行简易仪表盘模式
            print("导入简易仪表盘...")
            from src.ui.simple_dashboard import SimpleDashboard
            
            print("初始化简易仪表盘...")
            # 使用新的初始化方法，传递app_config
            dashboard = SimpleDashboard(app_config=app_config)
            
            print("启动简易仪表盘...")
            dashboard.run()
        else:
            print("全功能仪表盘尚未实现")
            
    except Exception as e:
        error_file = PROJECT_ROOT / f"direct_run_error_{timestamp}.txt"
        with open(error_file, "w") as f:
            f.write(f"错误发生于 {datetime.datetime.now().isoformat()}\n")
            f.write(f"错误: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        print(f"发生错误! 详情已写入: {error_file}")
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
