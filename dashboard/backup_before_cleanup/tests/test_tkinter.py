#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简化的Tkinter测试程序，验证窗口显示功能
"""

import tkinter as tk
import os
import sys
import logging
from datetime import datetime

# 设置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def main():
    """创建并显示一个简单的Tkinter窗口"""
    logging.info("开始测试Tkinter窗口")
    print("创建Tkinter窗口...")
    
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("Tkinter窗口测试")
        root.geometry("400x300")
        
        # 添加标签
        label = tk.Label(root, text="如果你能看到这个窗口，说明Tkinter正常工作", font=("Helvetica", 14))
        label.pack(pady=20)
        
        # 添加退出按钮
        button = tk.Button(root, text="退出", command=root.destroy)
        button.pack(pady=10)
        
        print("启动Tkinter主循环...")
        logging.info("启动Tkinter主循环")
        root.mainloop()
        logging.info("Tkinter主循环结束")
        print("窗口已关闭")
        
    except Exception as e:
        logging.error(f"Tkinter窗口测试出错: {e}", exc_info=True)
        print(f"错误: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    print(f"Python版本: {sys.version}")
    print(f"脚本路径: {__file__}")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        sys.exit(main())
    except Exception as e:
        logging.critical(f"未处理的异常: {e}", exc_info=True)
        print(f"致命错误: {e}")
        sys.exit(1)
