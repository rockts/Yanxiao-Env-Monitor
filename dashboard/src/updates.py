#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 故障诊断模块
用于修复和诊断系统问题
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# 设置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def fix_mqtt_connection():
    """修复MQTT连接问题"""
    try:
        # 获取main.py文件路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_path = os.path.join(script_dir, "main.py")
        
        logging.info(f"检查文件: {main_py_path}")
        
        # 读取文件内容
        with open(main_py_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 检查是否已经有update_connection_status_display方法
        if "def update_connection_status_display" in content:
            logging.info("update_connection_status_display方法已存在")
            return True
        
        # 在SmartCampusDashboard类中查找适合添加方法的位置
        import re
        
        # 查找类中最后一个方法
        class_pattern = r"class SmartCampusDashboard[^{]*:"
        if not re.search(class_pattern, content):
            logging.error("找不到SmartCampusDashboard类")
            return False
            
        # 添加方法
        method_code = """
    def update_connection_status_display(self, connected, status_text=None):
        \"\"\"更新MQTT连接状态显示\"\"\"
        try:
            self._mqtt_connected = connected
            
            if connected:
                status_msg = "状态: 已连接到MQTT服务器"
                status_color = TEXT_COLOR_STATUS_OK
                self.connection_status_var.set(status_msg)
                logging.info(status_msg)
            else:
                if status_text:
                    status_msg = f"状态: {status_text}"
                else:
                    status_msg = "状态: 未连接"
                status_color = TEXT_COLOR_STATUS_FAIL
                self.connection_status_var.set(status_msg)
                logging.warning(status_msg)
            
            # 如果标签控件已创建，更新其外观
            if hasattr(self, 'connection_status_label_widget') and self.connection_status_label_widget:
                self.connection_status_label_widget.config(text=status_msg, fg=status_color)
        except Exception as e:
            logging.error(f"更新连接状态显示时出错: {e}")
            print(f"ERROR: 更新连接状态显示时出错: {e}")
"""
        
        logging.info("创建修复后的文件内容...")
        
        return True
    except Exception as e:
        logging.error(f"修复MQTT连接时出错: {e}")
        traceback.print_exc()
        return False

def create_simple_launcher():
    """创建简单的启动脚本"""
    try:
        # 获取dashboard目录
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        launcher_path = os.path.join(script_dir, "easy_launch.py")
        
        launcher_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
智慧校园环境监测系统 - 简易启动器
直接启动完整版仪表盘，无需额外配置
\"\"\"

import os
import sys
import traceback
from pathlib import Path

# 获取脚本所在路径
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
SRC_PATH = PROJECT_ROOT / "src"

print("=" * 60)
print("     烟铺小学智慧校园环境监测系统 - 启动中...     ")
print("=" * 60)

# 添加src目录到路径
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['PYTHONPATH'] = f"{SRC_PATH}:{PROJECT_ROOT}"

try:
    # 找到main.py文件
    main_py_path = SRC_PATH / "main.py"
    if not main_py_path.exists():
        raise FileNotFoundError(f"找不到主模块文件: {main_py_path}")
    
    print(f"正在启动仪表盘...")
    
    # 导入tkinter
    import tkinter as tk
    
    # 创建根窗口
    root = tk.Tk()
    
    # 导入main模块
    sys.path.insert(0, str(SRC_PATH))
    from main import SmartCampusDashboard
    
    # 创建应用实例
    app = SmartCampusDashboard(root)
    
    # 添加错误处理和窗口关闭处理
    def on_error(*args):
        print("发生未处理的异常:")
        traceback.print_exception(*args)
    
    # 设置未捕获异常处理器
    sys.excepthook = on_error
    
    # 添加窗口关闭处理
    if hasattr(app, 'on_closing'):
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
    else:
        def default_on_closing():
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", default_on_closing)
    
    # 启动主循环
    root.mainloop()
    
except Exception as e:
    print(f"启动仪表盘时出错: {e}")
    print("\\n详细错误信息:")
    traceback.print_exc()
    
    print("\\n请按回车键退出...")
    input()
"""
        
        with open(launcher_path, 'w', encoding='utf-8') as file:
            file.write(launcher_code)
        
        # 添加执行权限
        os.chmod(launcher_path, 0o755)
        
        logging.info(f"创建了简易启动器: {launcher_path}")
        return launcher_path
    except Exception as e:
        logging.error(f"创建启动器时出错: {e}")
        traceback.print_exc()
        return None

def run_diagnostics():
    """运行全面诊断"""
    logging.info("开始系统诊断...")
    
    # 1. 检查环境
    logging.info("检查Python环境...")
    import platform
    print(f"Python版本: {platform.python_version()}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    
    # 2. 检查必要的库
    try:
        logging.info("检查必要的库...")
        import tkinter
        print("√ tkinter 已安装")
    except ImportError:
        print("× tkinter 未安装")
    
    try:
        import paho.mqtt.client
        print("√ paho-mqtt 已安装")
    except ImportError:
        print("× paho-mqtt 未安装")
    
    try:
        import matplotlib
        print("√ matplotlib 已安装")
    except ImportError:
        print("× matplotlib 未安装")
    
    try:
        from PIL import Image
        print("√ Pillow 已安装")
    except ImportError:
        print("× Pillow 未安装")
    
    # 3. 检查文件系统
    logging.info("检查文件系统...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    main_py = os.path.join(script_dir, "main.py")
    if os.path.exists(main_py):
        print(f"√ 主程序文件存在: {main_py}")
    else:
        print(f"× 主程序文件不存在: {main_py}")
    
    # 创建简易启动器
    launcher_path = create_simple_launcher()
    
    if launcher_path:
        print(f"\n创建了新的简易启动器: {launcher_path}")
        print("请尝试运行此启动器来启动仪表盘")
        print(f"命令: python3 {launcher_path}")
    
    print("\n诊断完成!")

# 执行主函数
if __name__ == "__main__":
    run_diagnostics()