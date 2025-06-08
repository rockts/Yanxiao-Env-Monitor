#!/usr/bin/env python3
"""
历史数据分析和图表生成
用于分析环境监测系统的历史数据趋势
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# 设置matplotlib后端和字体
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def analyze_sensor_data():
    """分析传感器历史数据"""
    print("📊 开始分析历史数据...")
    
    csv_file = "logs/sensor_data.csv"
    if not os.path.exists(csv_file):
        print("❌ 历史数据文件不存在，请先运行数据记录")
        return
    
    # 读取CSV数据
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ 成功读取 {len(df)} 条历史记录")
        
        # 转换时间戳
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 基础统计信息
        print("\n📈 数据统计摘要:")
        numeric_columns = ['temperature', 'humidity', 'aqi', 'eco2', 'tvoc', 'noise']
        stats = df[numeric_columns].describe()
        print(stats)
        
        # 生成趋势图表
        generate_trend_charts(df)
        
        # 数据质量分析
        analyze_data_quality(df)
        
        return df
        
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")
        return None

def generate_trend_charts(df):
    """生成趋势图表"""
    print("\n📊 生成趋势图表...")
    
    try:
        # 创建图表目录
        os.makedirs("logs/charts", exist_ok=True)
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 1. 温湿度趋势图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 温度趋势
        ax1.plot(df['datetime'], df['temperature'], color='red', linewidth=2, label='温度')
        ax1.set_title('温度趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('温度 (°C)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 湿度趋势
        ax2.plot(df['datetime'], df['humidity'], color='blue', linewidth=2, label='湿度')
        ax2.set_title('湿度趋势', fontsize=14, fontweight='bold')
        ax2.set_ylabel('湿度 (%)')
        ax2.set_xlabel('时间')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('logs/charts/temperature_humidity_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 空气质量趋势图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # AQI
        ax1.plot(df['datetime'], df['aqi'], color='green', linewidth=2, marker='o', markersize=4)
        ax1.set_title('AQI 趋势')
        ax1.set_ylabel('AQI')
        ax1.grid(True, alpha=0.3)
        
        # eCO2
        ax2.plot(df['datetime'], df['eco2'], color='orange', linewidth=2, marker='s', markersize=4)
        ax2.set_title('eCO2 趋势')
        ax2.set_ylabel('eCO2 (ppm)')
        ax2.grid(True, alpha=0.3)
        
        # TVOC
        ax3.plot(df['datetime'], df['tvoc'], color='purple', linewidth=2, marker='^', markersize=4)
        ax3.set_title('TVOC 趋势')
        ax3.set_ylabel('TVOC (ppb)')
        ax3.set_xlabel('时间')
        ax3.grid(True, alpha=0.3)
        
        # 噪音
        ax4.plot(df['datetime'], df['noise'], color='brown', linewidth=2, marker='d', markersize=4)
        ax4.set_title('噪音趋势')
        ax4.set_ylabel('噪音 (dB)')
        ax4.set_xlabel('时间')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('logs/charts/air_quality_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 数据分布箱型图
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        metrics = ['temperature', 'humidity', 'aqi', 'eco2', 'tvoc', 'noise']
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        units = ['°C', '%', '', 'ppm', 'ppb', 'dB']
        
        for i, (metric, color, unit) in enumerate(zip(metrics, colors, units)):
            if i < len(axes):
                axes[i].boxplot(df[metric], patch_artist=True, boxprops=dict(facecolor=color, alpha=0.7))
                axes[i].set_title(f'{metric.upper()} 分布', fontweight='bold')
                axes[i].set_ylabel(f'{metric} ({unit})')
                axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('logs/charts/data_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ 图表已生成到 logs/charts/ 目录")
        
    except Exception as e:
        print(f"❌ 图表生成失败: {e}")

def analyze_data_quality(df):
    """分析数据质量"""
    print("\n🔍 数据质量分析:")
    
    # 检查缺失值
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print("   ⚠️  发现缺失数据:")
        for col, count in missing_data.items():
            if count > 0:
                print(f"      {col}: {count} 条")
    else:
        print("   ✅ 无缺失数据")
    
    # 检查异常值（使用IQR方法）
    numeric_columns = ['temperature', 'humidity', 'aqi', 'eco2', 'tvoc', 'noise']
    outliers_found = False
    
    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if len(outliers) > 0:
            if not outliers_found:
                print("   ⚠️  发现异常值:")
                outliers_found = True
            print(f"      {col}: {len(outliers)} 条异常值")
    
    if not outliers_found:
        print("   ✅ 无明显异常值")
    
    # 数据时间范围
    time_range = df['datetime'].max() - df['datetime'].min()
    print(f"   📅 数据时间范围: {time_range}")
    print(f"   📊 数据密度: {len(df)} 条记录")

def generate_real_time_dashboard_data():
    """为前端仪表板生成实时数据摘要"""
    print("\n📱 生成仪表板数据摘要...")
    
    csv_file = "logs/sensor_data.csv"
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file)
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 获取最近1小时的数据
        recent_time = datetime.now() - timedelta(hours=1)
        recent_df = df[df['datetime'] >= recent_time]
        
        if len(recent_df) == 0:
            return None
        
        # 生成摘要统计
        summary = {
            'last_update': recent_df['datetime'].max().strftime('%Y-%m-%d %H:%M:%S'),
            'records_count': len(recent_df),
            'averages': {
                'temperature': round(recent_df['temperature'].mean(), 1),
                'humidity': round(recent_df['humidity'].mean(), 1),
                'aqi': round(recent_df['aqi'].mean(), 1),
                'eco2': round(recent_df['eco2'].mean()),
                'tvoc': round(recent_df['tvoc'].mean()),
                'noise': round(recent_df['noise'].mean(), 1)
            },
            'trends': {}
        }
        
        # 计算趋势（比较前半小时和后半小时的平均值）
        if len(recent_df) >= 2:
            mid_point = len(recent_df) // 2
            first_half = recent_df.iloc[:mid_point]
            second_half = recent_df.iloc[mid_point:]
            
            for metric in ['temperature', 'humidity', 'aqi', 'eco2', 'tvoc', 'noise']:
                avg1 = first_half[metric].mean()
                avg2 = second_half[metric].mean()
                trend = "↗️" if avg2 > avg1 else "↘️" if avg2 < avg1 else "➡️"
                summary['trends'][metric] = trend
        
        # 保存到JSON文件
        with open('logs/dashboard_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("✅ 仪表板数据摘要已生成")
        return summary
        
    except Exception as e:
        print(f"❌ 生成仪表板数据失败: {e}")
        return None

if __name__ == "__main__":
    try:
        # 分析历史数据
        df = analyze_sensor_data()
        
        if df is not None:
            # 生成仪表板摘要
            summary = generate_real_time_dashboard_data()
            
            if summary:
                print("\n📋 仪表板摘要:")
                print(f"   最后更新: {summary['last_update']}")
                print(f"   记录数量: {summary['records_count']}")
                print("   平均值:")
                for metric, value in summary['averages'].items():
                    trend = summary['trends'].get(metric, '')
                    print(f"      {metric}: {value} {trend}")
        
        print("\n🎉 历史数据分析完成!")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
