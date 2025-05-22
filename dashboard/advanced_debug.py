#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智慧校园环境监测系统 - 高级调试脚本
用于详细跟踪完整版仪表盘的启动过程
"""

import os
import sys
import traceback
import inspect

print("启动高级调试脚本...")
print(f"当前工作目录: {os.getcwd()}")

# 包装SmartCampusDashboard类的初始化方法，以便记录每个执行步骤
class DebugWrapper:
    def __init__(self, module_name):
        self.module_name = module_name
        self.original_module = None
        self.original_init = None
        self.dashboard_instance = None
    
    def wrap_init(self):
        print(f"正在监控 {self.module_name}.SmartCampusDashboard.__init__ 方法...")
        try:
            # 导入模块
            exec(f"import {self.module_name} as mod")
            self.original_module = eval("mod")
            
            # 保存原始的init方法
            self.original_init = self.original_module.SmartCampusDashboard.__init__
            
            # 替换为我们的跟踪版本
            def wrapped_init(self_obj, *args, **kwargs):
                print("\n=== 开始初始化 SmartCampusDashboard ===")
                try:
                    # 逐行检查初始化方法的源码并执行
                    source_lines, _ = inspect.getsourcelines(self.original_init)
                    # 跳过方法签名行
                    for i, line in enumerate(source_lines[1:], 1):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        print(f"执行第 {i} 行: {line}")
                        try:
                            if "self." in line:
                                # 对关键操作进行特殊处理
                                if "self.root = root" in line:
                                    self_obj.root = args[0]
                                    print("  root 已设置")
                                elif "self.config" in line and "=" in line:
                                    # 手动加载配置，以便详细报告
                                    print("  加载配置...")
                                    from src.config_loader import ConfigLoader
                                    self_obj.config_loader = ConfigLoader()
                                    self_obj.config = self_obj.config_loader.load_config()
                                    print(f"  配置已加载: {list(self_obj.config.keys())}")
                                elif "self.setup_ui()" in line:
                                    print("  开始设置UI...")
                                    # 这里可能是问题所在，我们仔细检查
                                    # 提取setup_ui方法并逐步执行
                                    setup_ui_source, _ = inspect.getsourcelines(self.original_module.SmartCampusDashboard.setup_ui)
                                    for j, ui_line in enumerate(setup_ui_source[1:], 1):
                                        ui_line = ui_line.strip()
                                        if not ui_line or ui_line.startswith('#'):
                                            continue
                                        print(f"    UI设置第 {j} 行: {ui_line}")
                                        # 这里不实际执行，只是打印
                                else:
                                    # 对其他赋值操作仅打印
                                    print(f"  执行: {line}")
                        except Exception as e:
                            print(f"  行 {i} 执行出错: {e}")
                            traceback.print_exc()
                            break
                    
                    print("\n原始 __init__ 方法:")
                    print("".join(source_lines))
                    
                    print("\n尝试正常执行 __init__ 方法:")
                    self.original_init(self_obj, *args, **kwargs)
                    print("初始化完成！")
                except Exception as e:
                    print(f"初始化过程中出错: {e}")
                    traceback.print_exc()
                
                print("=== 初始化结束 ===")
                
                # 保存引用
                self.dashboard_instance = self_obj
            
            # 替换初始化方法
            self.original_module.SmartCampusDashboard.__init__ = wrapped_init
            print("初始化方法已成功包装")
            return True
        except Exception as e:
            print(f"包装初始化方法时出错: {e}")
            traceback.print_exc()
            return False
    
    def run(self):
        """运行被监控的应用程序"""
        if not self.original_module:
            print("模块尚未正确包装")
            return
        
        try:
            print("\n创建应用程序实例...")
            import tkinter as tk
            root = tk.Tk()
            app = self.original_module.SmartCampusDashboard(root)
            
            print("\n应用程序已创建，但不启动主循环")
            print("调试完成")
        except Exception as e:
            print(f"创建应用程序实例时出错: {e}")
            traceback.print_exc()

try:
    wrapper = DebugWrapper("full_dashboard_new")
    if wrapper.wrap_init():
        wrapper.run()
except Exception as e:
    print(f"调试过程中出错: {e}")
    traceback.print_exc()

print("高级调试脚本结束")
