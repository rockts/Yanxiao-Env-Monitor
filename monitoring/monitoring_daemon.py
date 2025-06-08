#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烟小环境监测系统 - 自动监控守护进程
Automated Monitoring Daemon for Environment Monitoring System

功能：
- 定期检查生产服务器状态
- 自动发送告警
- 记录监控日志
- 生成监控报告
"""

import time
import json
import logging
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
from production_health_check import ProductionHealthChecker

class MonitoringDaemon:
    def __init__(self, check_interval=300):  # 默认5分钟检查一次
        self.check_interval = check_interval  # 检查间隔（秒）
        self.checker = ProductionHealthChecker()
        
        # 配置日志
        self.setup_logging()
        
        # 监控历史记录
        self.monitoring_history = []
        self.alert_history = []
        
        # 告警阈值配置
        self.alert_config = {
            'consecutive_failures': 3,  # 连续失败次数触发告警
            'health_score_threshold': 60,  # 健康评分阈值
            'data_freshness_minutes': 10,  # 数据新鲜度阈值（分钟）
        }
        
        # 状态跟踪
        self.consecutive_failures = 0
        self.last_alert_time = None
        self.alert_cooldown_minutes = 30  # 告警冷却时间
        
    def setup_logging(self):
        """设置日志配置"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建监控专用日志
        self.logger = logging.getLogger('production_monitor')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_dir / 'production_monitor.log')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def run_health_check(self):
        """运行健康检查并返回结果"""
        try:
            self.logger.info("开始健康检查...")
            
            # 执行各项检查
            results = {}
            
            # 网络检查
            results['network'] = self.checker.check_network_connectivity()
            
            # API检查
            results['api'], api_data = self.checker.check_api_status()
            
            # 数据流检查
            results['data'], sensor_data = self.checker.check_data_flow()
            
            # 健康端点检查
            results['health'], health_data = self.checker.check_health_endpoint()
            
            # 计算健康评分
            total_checks = len(results)
            passed_checks = sum(1 for v in results.values() if v)
            health_score = (passed_checks / total_checks) * 100
            
            # 构建检查结果
            check_result = {
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'results': results,
                'api_data': api_data,
                'sensor_data': sensor_data,
                'health_data': health_data
            }
            
            self.logger.info(f"健康检查完成 - 评分: {health_score:.1f}%")
            return check_result
            
        except Exception as e:
            self.logger.error(f"健康检查异常: {e}")
            return None
    
    def evaluate_alerts(self, check_result):
        """评估是否需要发送告警"""
        if not check_result:
            self.consecutive_failures += 1
            return self.should_send_alert("health_check_failed", "健康检查执行失败")
        
        health_score = check_result['health_score']
        results = check_result['results']
        
        # 重置连续失败计数器（如果检查成功）
        if health_score > self.alert_config['health_score_threshold']:
            self.consecutive_failures = 0
        
        # 检查各种告警条件
        alerts = []
        
        # 1. 健康评分过低
        if health_score < self.alert_config['health_score_threshold']:
            self.consecutive_failures += 1
            alerts.append({
                'type': 'low_health_score',
                'message': f"系统健康评分过低: {health_score:.1f}%",
                'severity': 'warning' if health_score > 30 else 'critical'
            })
        
        # 2. 网络连接失败
        if not results.get('network'):
            alerts.append({
                'type': 'network_failure', 
                'message': "网络连接失败",
                'severity': 'critical'
            })
        
        # 3. API服务异常
        if not results.get('api'):
            alerts.append({
                'type': 'api_failure',
                'message': "API服务异常", 
                'severity': 'critical'
            })
        
        # 4. MQTT连接断开
        api_data = check_result.get('api_data', {})
        if api_data and not api_data.get('mqtt_connected'):
            alerts.append({
                'type': 'mqtt_disconnected',
                'message': "MQTT连接断开",
                'severity': 'warning'
            })
        
        # 5. 数据流异常
        if not results.get('data'):
            alerts.append({
                'type': 'data_flow_failure',
                'message': "数据流获取失败",
                'severity': 'warning'
            })
        
        # 6. 连续失败次数过多
        if self.consecutive_failures >= self.alert_config['consecutive_failures']:
            alerts.append({
                'type': 'consecutive_failures',
                'message': f"连续{self.consecutive_failures}次检查失败",
                'severity': 'critical'
            })
        
        return alerts
    
    def should_send_alert(self, alert_type, message):
        """判断是否应该发送告警（考虑冷却时间）"""
        now = datetime.now()
        
        # 检查冷却时间
        if self.last_alert_time:
            time_since_last = now - self.last_alert_time
            if time_since_last.total_seconds() < (self.alert_cooldown_minutes * 60):
                return False
        
        return True
    
    def send_alert(self, alerts):
        """发送告警（这里可以扩展为邮件、短信、钉钉等）"""
        if not alerts:
            return
        
        now = datetime.now()
        
        # 检查是否在冷却期
        if not self.should_send_alert("general", ""):
            self.logger.info("告警在冷却期内，跳过发送")
            return
        
        # 记录告警
        alert_record = {
            'timestamp': now.isoformat(),
            'alerts': alerts,
            'consecutive_failures': self.consecutive_failures
        }
        
        self.alert_history.append(alert_record)
        self.last_alert_time = now
        
        # 打印告警信息
        self.logger.warning("=" * 50)
        self.logger.warning("🚨 系统告警")
        self.logger.warning(f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.warning(f"连续失败次数: {self.consecutive_failures}")
        
        for alert in alerts:
            severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
            self.logger.warning(f"{severity_icon} {alert['message']}")
        
        self.logger.warning("=" * 50)
        
        # TODO: 这里可以添加其他告警方式
        # - 发送邮件
        # - 发送短信
        # - 钉钉机器人
        # - 企业微信
        
    def save_monitoring_data(self, check_result):
        """保存监控数据"""
        if check_result:
            self.monitoring_history.append(check_result)
            
            # 保持最近1000条记录
            if len(self.monitoring_history) > 1000:
                self.monitoring_history = self.monitoring_history[-1000:]
    
    def generate_daily_report(self):
        """生成日报告"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 获取今天的监控数据
        today_data = [
            record for record in self.monitoring_history
            if datetime.fromisoformat(record['timestamp']) >= today_start
        ]
        
        if not today_data:
            return
        
        # 计算统计信息
        health_scores = [record['health_score'] for record in today_data]
        avg_health = sum(health_scores) / len(health_scores)
        min_health = min(health_scores)
        max_health = max(health_scores)
        
        # 计算可用性
        successful_checks = len([s for s in health_scores if s > 80])
        availability = (successful_checks / len(health_scores)) * 100
        
        # 生成报告
        report = f"""
📊 烟小环境监测系统 - 日监控报告
📅 日期: {now.strftime('%Y-%m-%d')}
⏰ 生成时间: {now.strftime('%H:%M:%S')}

📈 健康评分统计:
   平均分: {avg_health:.1f}%
   最高分: {max_health:.1f}%  
   最低分: {min_health:.1f}%

🎯 系统可用性: {availability:.1f}%
🔍 检查次数: {len(today_data)}
🚨 告警次数: {len(self.alert_history)}

💡 建议: {'系统运行稳定' if avg_health > 90 else '需要关注系统健康状况'}
"""
        
        self.logger.info(report)
        
        # 保存到文件
        report_file = Path("logs") / f"daily_report_{now.strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def run_daemon(self):
        """运行监控守护进程"""
        self.logger.info("🚀 启动生产环境监控守护进程")
        self.logger.info(f"📊 检查间隔: {self.check_interval}秒")
        self.logger.info(f"🎯 目标服务器: {self.checker.server_ip}:{self.checker.server_port}")
        
        last_daily_report = datetime.now().date()
        
        try:
            while True:
                # 执行健康检查
                check_result = self.run_health_check()
                
                # 保存监控数据
                self.save_monitoring_data(check_result)
                
                # 评估告警
                alerts = self.evaluate_alerts(check_result)
                if alerts:
                    self.send_alert(alerts)
                
                # 检查是否需要生成日报告
                current_date = datetime.now().date()
                if current_date > last_daily_report:
                    self.generate_daily_report()
                    last_daily_report = current_date
                
                # 等待下次检查
                self.logger.info(f"⏱️  等待 {self.check_interval} 秒后进行下次检查...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 监控守护进程被用户中断")
        except Exception as e:
            self.logger.error(f"❌ 监控守护进程异常: {e}")
        finally:
            self.logger.info("👋 监控守护进程已停止")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            # 启动监控守护进程
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            daemon = MonitoringDaemon(check_interval=interval)
            daemon.run_daemon()
            
        elif command == 'check':
            # 单次检查
            daemon = MonitoringDaemon()
            result = daemon.run_health_check()
            if result:
                print(f"健康评分: {result['health_score']:.1f}%")
                alerts = daemon.evaluate_alerts(result)
                if alerts:
                    daemon.send_alert(alerts)
                else:
                    print("✅ 无告警")
            
        elif command == 'report':
            # 生成报告
            daemon = MonitoringDaemon()
            daemon.generate_daily_report()
            
        elif command == 'help':
            print("""
使用方法:
  python3 monitoring_daemon.py start [interval]    # 启动监控守护进程
  python3 monitoring_daemon.py check               # 单次健康检查
  python3 monitoring_daemon.py report              # 生成日报告
  python3 monitoring_daemon.py help                # 显示帮助

参数说明:
  interval: 检查间隔（秒），默认300秒（5分钟）

示例:
  python3 monitoring_daemon.py start 180           # 每3分钟检查一次
  python3 monitoring_daemon.py start               # 使用默认间隔（5分钟）
            """)
        else:
            print(f"未知命令: {command}")
            print("使用 'help' 查看可用命令")
    else:
        print("请指定命令。使用 'help' 查看可用命令。")

if __name__ == "__main__":
    main()
