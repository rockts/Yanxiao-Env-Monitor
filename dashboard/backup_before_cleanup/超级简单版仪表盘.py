#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级简单版仪表盘启动器 - 完全独立版本
将所有必要的代码集成在一个文件中，避免导入错误
"""

import os
import sys
import json
import random
import tkinter as tk
from tkinter import messagebox
import time
import threading
from datetime import datetime
from pathlib import Path

# 获取本脚本的绝对路径
SCRIPT_PATH = Path(__file__).resolve()
# 项目根目录
PROJECT_ROOT = SCRIPT_PATH.parent

# 设置UI常量
PAGE_BG_COLOR = "#0A1E36"  # 深科技蓝色背景
PANEL_BG_COLOR = "#102A43" # 稍亮一点的蓝色面板背景
TEXT_COLOR_HEADER = "#E0EFFF"  # 标题文本颜色
TEXT_COLOR_VALUE = "#64FFDA"   # 值文本颜色

# AQI级别常量定义
AQI_LEVELS = {
    (0, 50): {"level": "优", "color": "#00E400", "desc": "空气质量令人满意，基本无空气污染"},
    (51, 100): {"level": "良", "color": "#FFFF00", "desc": "空气质量可接受，但对极少数敏感人群有轻度影响"},
    (101, 150): {"level": "轻度污染", "color": "#FF7E00", "desc": "敏感人群症状有轻度加剧，健康人群可能出现刺激症状"},
    (151, 200): {"level": "中度污染", "color": "#FF0000", "desc": "进一步加剧敏感人群症状，可能对健康人群心脏、呼吸系统有影响"},
    (201, 300): {"level": "重度污染", "color": "#99004C", "desc": "心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状"},
    (301, 500): {"level": "严重污染", "color": "#7E0023", "desc": "健康人群运动耐受力降低，有明显强烈症状，可能导致疾病"}
}

# 模拟数据
SIMULATION_DATA = {
    "环境温度": 25.6,
    "环境湿度": 68.2,
    "aqi": 52,
    "tvoc": 320,
    "eco2": 780,
    "紫外线指数": 2.8,
    "uv风险等级": "低",
    "噪音": 45.5
}

class SimpleStandaloneDashboard:
    """超简单版仪表盘 - 独立版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("烟铺小学智慧校园环境监测系统 - 简易版")
        self.root.geometry("800x600")
        self.root.configure(bg=PAGE_BG_COLOR)
        
        # 初始化变量
        self.use_simulation = True  # 使用模拟数据
        self.sensor_data = {key: "N/A" for key in SIMULATION_DATA.keys()}
        
        # 创建简单布局
        self.create_ui()
        
        # 启动更新循环
        if self.use_simulation:
            self.update_aqi_display()
        
        # 协议处理监听器
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # 创建标题栏
        header_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        header_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(header_frame, text="智慧校园环境监测系统",
                             font=("Helvetica", 24, "bold"), 
                             fg=TEXT_COLOR_HEADER, bg=PAGE_BG_COLOR)
        title_label.pack()
        
        # 添加连接状态
        self.connection_label = tk.Label(header_frame, text="状态: 使用模拟数据",
                                     font=("Helvetica", 10), 
                                     fg="orange", bg=PAGE_BG_COLOR)
        self.connection_label.pack(pady=5)
        
        # 创建AQI面板
        self.aqi_frame = tk.Frame(self.root, bg=PANEL_BG_COLOR, 
                                 padx=20, pady=20,
                                 highlightbackground="#555555", 
                                 highlightthickness=1)
        self.aqi_frame.pack(pady=30)
        
        # AQI标题
        tk.Label(self.aqi_frame, text="空气质量指数 (AQI)", 
               font=("Helvetica", 18, "bold"), 
               fg=TEXT_COLOR_HEADER, bg=PANEL_BG_COLOR).pack(pady=(0,20))
        
        # AQI数值显示
        self.aqi_value_label = tk.Label(self.aqi_frame, text="--", 
                                      font=("Helvetica", 40, "bold"), 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.aqi_value_label.pack()
        
        # AQI等级显示
        self.aqi_level_label = tk.Label(self.aqi_frame, text="--", 
                                      font=("Helvetica", 16), 
                                      fg=TEXT_COLOR_VALUE, bg=PANEL_BG_COLOR)
        self.aqi_level_label.pack(pady=(10, 0))
        
        # AQI描述显示
        self.aqi_desc_label = tk.Label(self.aqi_frame, text="--", 
                                     font=("Helvetica", 12), 
                                     fg=TEXT_COLOR_HEADER, bg=PANEL_BG_COLOR,
                                     wraplength=300)
        self.aqi_desc_label.pack(pady=(5, 0))
        
        # 按钮框架
        buttons_frame = tk.Frame(self.root, bg=PAGE_BG_COLOR)
        buttons_frame.pack(pady=20)
        
        # 添加刷新按钮
        self.refresh_button = tk.Button(buttons_frame, text="刷新数据", 
                                      command=self.update_aqi_display,
                                      font=("Helvetica", 12),
                                      bg="#007BFF", fg="white",
                                      padx=10, pady=5)
        self.refresh_button.pack(side="left", padx=10)
        
        # 添加退出按钮
        self.exit_button = tk.Button(buttons_frame, text="退出", 
                                   command=self.on_closing,
                                   font=("Helvetica", 12),
                                   bg="#DC3545", fg="white",
                                   padx=10, pady=5)
        self.exit_button.pack(side="left", padx=10)
        
        # 添加版本信息标签
        version_label = tk.Label(self.root, text="简化版 v1.0.0 | 更新时间: 2025-05-21",
                               font=("Helvetica", 8),
                               fg="#888888", bg=PAGE_BG_COLOR)
        version_label.pack(side="bottom", pady=10)
    
    def update_aqi_display(self):
        """更新AQI显示 - 使用模拟数据"""
        try:
            if self.use_simulation:
                # 生成一个略有变化的AQI值
                base_aqi = SIMULATION_DATA["aqi"]
                random_change = random.randint(-5, 5)
                aqi_value = base_aqi + random_change
                
                # 确保AQI在合理范围内
                aqi_value = max(10, min(500, aqi_value))
                
                # 打印调试信息
                print(f"使用模拟AQI值: {aqi_value}")
                
                # 更新UI显示
                self.aqi_value_label.config(text=str(aqi_value))
                
                # 确定AQI等级和颜色
                for (low, high), level_info in AQI_LEVELS.items():
                    if low <= aqi_value <= high:
                        level = level_info["level"]
                        color = level_info["color"]
                        desc = level_info["desc"]
                        self.aqi_level_label.config(text=level, fg=color)
                        self.aqi_desc_label.config(text=desc)
                        # 将AQI值的颜色也更改为对应的等级颜色
                        self.aqi_value_label.config(fg=color)
                        break
                
                # 模拟更新其他传感器数据
                for key in self.sensor_data:
                    base_value = SIMULATION_DATA.get(key, 0)
                    if isinstance(base_value, (int, float)):
                        # 数值类型数据添加随机波动
                        random_change = random.uniform(-0.1, 0.1) * base_value
                        self.sensor_data[key] = round(base_value + random_change, 1)
                    else:
                        # 文本类型数据保持不变
                        self.sensor_data[key] = base_value
                
                # 1秒后再次更新
                self.root.after(2000, self.update_aqi_display)
            
        except Exception as e:
            print(f"更新显示时出错: {e}")
            # 出错后仍然继续循环，增强稳定性
            self.root.after(5000, self.update_aqi_display)
    
    def on_closing(self):
        """窗口关闭处理"""
        if messagebox.askokcancel("退出", "确定要退出吗?"):
            print("用户关闭窗口")
            self.root.destroy()

def main():
    """主函数"""
    try:
        # 显示启动信息
        print("=" * 40)
        print("  智慧校园环境监测系统 - 超简版启动")
        print("=" * 40)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"脚本路径: {SCRIPT_PATH}")
        print()
        
        # 创建主窗口
        root = tk.Tk()
        root.title("烟铺小学智慧校园环境监测系统")
        
        # 设置图标（如果有）
        try:
            icon_path = PROJECT_ROOT / "assets" / "app_icon.ico"
            if icon_path.exists():
                root.iconbitmap(icon_path)
        except Exception as e:
            print(f"设置图标时出错: {e}")
        
        # 设置窗口位置在屏幕中央
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 创建仪表盘
        dashboard = SimpleStandaloneDashboard(root)
        
        # 启动主循环
        print("启动主循环...")
        root.mainloop()
        print("程序已退出")
        
        return 0
    
    except Exception as e:
        print(f"发生错误: {e}")
        # 在终端中显示错误
        import traceback
        traceback.print_exc()
        
        # 显示错误窗口
        try:
            error_root = tk.Tk()
            error_root.title("启动错误")
            error_root.geometry("500x300")
            
            error_label = tk.Label(error_root, text=f"发生错误: {e}", wraplength=450)
            error_label.pack(pady=20)
            
            # 错误详情文本框
            error_text = tk.Text(error_root, height=10, width=60)
            error_text.insert("1.0", traceback.format_exc())
            error_text.pack(padx=20, pady=10)
            
            # 关闭按钮
            close_button = tk.Button(error_root, text="关闭", command=error_root.destroy)
            close_button.pack(pady=10)
            
            error_root.mainloop()
        except:
            # 如果Tkinter也出错了，只能在终端显示
            print("无法显示图形错误窗口，请检查上面的错误信息")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
