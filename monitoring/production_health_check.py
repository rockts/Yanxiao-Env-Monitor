#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟小环境监测系统 - 生产环境健康检查工具
Production Health Check Tool for Environment Monitoring System

功能：
- 远程检查生产服务器状态
- 验证MQTT连接
- 监控数据流
- 生成状态报告
"""

import requests
import json
import time
import sys
from datetime import datetime
import subprocess
import socket

class ProductionHealthChecker:
    def __init__(self):
        self.server_ip = "192.168.1.115"
        self.server_port = 5052
        self.api_base = f"http://{self.server_ip}:{self.server_port}"
        self.ssh_user = "rockts"
        
    def check_network_connectivity(self):
        """检查网络连接"""
        print("🌐 检查网络连接...")
        try:
            # 检查ping连通性
            result = subprocess.run(['ping', '-c', '3', self.server_ip], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ 网络连接正常 - {self.server_ip}")
                return True
            else:
                print(f"   ❌ 网络连接失败 - {self.server_ip}")
                return False
        except Exception as e:
            print(f"   ⚠️  网络检查异常: {e}")
            return False
    
    def check_port_status(self):
        """检查端口状态"""
        print(f"🔌 检查服务端口 {self.server_port}...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, self.server_port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ 端口 {self.server_port} 开放")
                return True
            else:
                print(f"   ❌ 端口 {self.server_port} 不可达")
                return False
        except Exception as e:
            print(f"   ⚠️  端口检查异常: {e}")
            return False
    
    def check_api_status(self):
        """检查API状态"""
        print("📡 检查API服务...")
        try:
            response = requests.get(f"{self.api_base}/api/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API响应正常")
                print(f"   📊 MQTT连接: {'已连接' if data.get('mqtt_connected') else '未连接'}")
                print(f"   🏷️  服务模式: {data.get('server_mode', 'unknown')}")
                print(f"   🌐 MQTT服务器: {data.get('mqtt_broker', 'unknown')}")
                return True, data
            else:
                print(f"   ❌ API响应异常: {response.status_code}")
                return False, None
        except Exception as e:
            print(f"   ⚠️  API检查异常: {e}")
            return False, None
    
    def check_data_flow(self):
        """检查数据流"""
        print("📊 检查数据流...")
        try:
            response = requests.get(f"{self.api_base}/data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 数据获取正常")
                
                # 检查主要传感器数据
                sensors = ['temperature', 'humidity', 'aqi', 'eco2', 'tvoc', 'noise']
                for sensor in sensors:
                    value = data.get(sensor, 'N/A')
                    print(f"   📈 {sensor}: {value}")
                
                # 检查摄像头数据
                camera = data.get('camera', '')
                if camera and len(camera) > 100:
                    print(f"   📷 摄像头: 有数据 ({len(camera)} 字符)")
                else:
                    print(f"   📷 摄像头: 无数据")
                    
                return True, data
            else:
                print(f"   ❌ 数据获取失败: {response.status_code}")
                return False, None
        except Exception as e:
            print(f"   ⚠️  数据检查异常: {e}")
            return False, None
    
    def check_health_endpoint(self):
        """检查健康检查端点"""
        print("🏥 检查健康端点...")
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 健康检查正常")
                print(f"   📅 时间戳: {data.get('timestamp', 'unknown')}")
                return True, data
            else:
                print(f"   ❌ 健康检查失败: {response.status_code}")
                return False, None
        except Exception as e:
            print(f"   ⚠️  健康检查异常: {e}")
            return False, None
    
    def check_ssh_service(self):
        """检查SSH服务状态（可选）"""
        print("🔐 检查SSH服务...")
        try:
            result = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', 
                                   f'{self.ssh_user}@{self.server_ip}', 
                                   'echo "SSH connection test"'], 
                                   capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"   ✅ SSH连接正常")
                return True
            else:
                print(f"   ❌ SSH连接失败")
                return False
        except Exception as e:
            print(f"   ⚠️  SSH检查异常: {e}")
            return False
    
    def get_remote_logs(self, lines=20):
        """获取远程日志"""
        print(f"📄 获取最新日志 (最近{lines}行)...")
        try:
            cmd = f'tail -{lines} /home/rockts/env-monitor/logs/production.log'
            result = subprocess.run(['ssh', f'{self.ssh_user}@{self.server_ip}', cmd], 
                                   capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print("   ✅ 日志获取成功")
                logs = result.stdout.strip()
                if logs:
                    print("   📝 最新日志:")
                    for line in logs.split('\n')[-10:]:  # 显示最后10行
                        print(f"      {line}")
                else:
                    print("   ⚠️  日志文件为空")
                return True, logs
            else:
                print(f"   ❌ 日志获取失败: {result.stderr}")
                return False, None
        except Exception as e:
            print(f"   ⚠️  日志获取异常: {e}")
            return False, None
    
    def run_comprehensive_check(self):
        """运行综合检查"""
        print("=" * 60)
        print("🏥 烟小环境监测系统 - 生产环境健康检查")
        print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 目标服务器: {self.server_ip}:{self.server_port}")
        print("=" * 60)
        
        results = {}
        
        # 1. 网络连接检查
        results['network'] = self.check_network_connectivity()
        
        # 2. 端口状态检查
        results['port'] = self.check_port_status()
        
        # 3. API状态检查
        results['api'], api_data = self.check_api_status()
        
        # 4. 数据流检查
        results['data'], sensor_data = self.check_data_flow()
        
        # 5. 健康端点检查
        results['health'], health_data = self.check_health_endpoint()
        
        # 6. SSH服务检查
        results['ssh'] = self.check_ssh_service()
        
        # 7. 获取远程日志
        results['logs'], log_data = self.get_remote_logs()
        
        # 生成总结报告
        self.generate_summary_report(results, api_data, sensor_data, health_data)
    
    def generate_summary_report(self, results, api_data, sensor_data, health_data):
        """生成总结报告"""
        print("\n" + "=" * 60)
        print("📋 健康检查报告")
        print("=" * 60)
        
        # 计算总体状态
        total_checks = len(results)
        passed_checks = sum(1 for v in results.values() if v)
        health_score = (passed_checks / total_checks) * 100
        
        print(f"🎯 总体健康评分: {health_score:.1f}% ({passed_checks}/{total_checks})")
        
        # 详细状态
        status_icons = {True: "✅", False: "❌"}
        print(f"\n📊 详细状态:")
        for check, status in results.items():
            icon = status_icons[status]
            check_name = {
                'network': '网络连接',
                'port': '端口状态', 
                'api': 'API服务',
                'data': '数据流',
                'health': '健康端点',
                'ssh': 'SSH服务',
                'logs': '日志获取'
            }.get(check, check)
            print(f"   {icon} {check_name}")
        
        # 系统信息
        if api_data:
            print(f"\n🔧 系统信息:")
            print(f"   📡 MQTT状态: {'已连接' if api_data.get('mqtt_connected') else '未连接'}")
            print(f"   🌐 MQTT服务器: {api_data.get('mqtt_broker', 'unknown')}")
            print(f"   🏷️  运行模式: {api_data.get('server_mode', 'unknown')}")
        
        # 传感器数据摘要
        if sensor_data:
            print(f"\n📈 传感器数据摘要:")
            key_sensors = {
                'temperature': '温度',
                'humidity': '湿度', 
                'aqi': '空气质量',
                'noise': '噪音'
            }
            for key, name in key_sensors.items():
                value = sensor_data.get(key, 'N/A')
                print(f"   🌡️  {name}: {value}")
        
        # 建议和警告
        print(f"\n💡 建议:")
        if health_score == 100:
            print("   🎉 系统运行状态良好，无需额外操作")
        else:
            if not results.get('network'):
                print("   🔧 检查网络连接，确保服务器可达")
            if not results.get('port'):
                print("   🔧 检查服务是否正常运行，端口是否被占用")
            if not results.get('api'):
                print("   🔧 检查Flask服务状态，查看错误日志")
            if api_data and not api_data.get('mqtt_connected'):
                print("   🔧 检查MQTT连接，确保lot.lekee.cc可达")
        
        print("\n📞 如需进一步诊断，请运行:")
        print(f"   ssh {self.ssh_user}@{self.server_ip}")
        print(f"   tail -f /home/rockts/env-monitor/logs/production.log")
        print("=" * 60)

def main():
    """主函数"""
    checker = ProductionHealthChecker()
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'quick':
            # 快速检查
            print("🚀 快速健康检查...")
            network_ok = checker.check_network_connectivity()
            if network_ok:
                api_ok, _ = checker.check_api_status()
                if api_ok:
                    print("✅ 快速检查通过 - 系统运行正常")
                else:
                    print("❌ 快速检查失败 - API服务异常")
            else:
                print("❌ 快速检查失败 - 网络连接问题")
        elif command == 'logs':
            # 仅获取日志
            checker.get_remote_logs(50)
        elif command == 'data':
            # 仅检查数据
            checker.check_data_flow()
        elif command == 'help':
            print("使用方法:")
            print("  python3 production_health_check.py          # 完整检查")
            print("  python3 production_health_check.py quick    # 快速检查")
            print("  python3 production_health_check.py logs     # 获取日志")
            print("  python3 production_health_check.py data     # 检查数据")
        else:
            print(f"未知命令: {command}")
            print("使用 'help' 查看可用命令")
    else:
        # 完整检查
        checker.run_comprehensive_check()

if __name__ == "__main__":
    main()
