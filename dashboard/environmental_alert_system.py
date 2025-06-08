# -*- coding: utf-8 -*-
"""
环境监测警报系统
Environmental Alert System

功能：
- 监测环境数据阈值
- 生成警报和通知
- 记录警报日志
- 发送警报消息
"""

import json
import logging
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum

class AlertLevel(Enum):
    """警报级别"""
    INFO = "info"        # 信息
    WARNING = "warning"  # 警告
    CRITICAL = "critical" # 严重
    EMERGENCY = "emergency" # 紧急

class AlertType(Enum):
    """警报类型"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    AQI = "aqi"
    CO2 = "co2"
    TVOC = "tvoc"
    NOISE = "noise"
    UV = "uv"

@dataclass
class AlertThreshold:
    """警报阈值配置"""
    metric: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    level: AlertLevel = AlertLevel.WARNING
    message: str = ""
    enabled: bool = True

@dataclass
class Alert:
    """警报对象"""
    id: str
    timestamp: datetime
    metric: str
    current_value: float
    threshold_value: float
    level: AlertLevel
    message: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class EnvironmentalAlertSystem:
    """环境监测警报系统"""
    
    def __init__(self, config_file: str = "alert_config.json"):
        self.config_file = config_file
        self.thresholds = self._load_thresholds()
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.callbacks: List[Callable] = []
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 创建警报日志文件
        alert_handler = logging.FileHandler('logs/alerts.log', encoding='utf-8')
        alert_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.alert_logger = logging.getLogger('alerts')
        self.alert_logger.addHandler(alert_handler)
        
    def _load_thresholds(self) -> Dict[str, List[AlertThreshold]]:
        """加载警报阈值配置"""
        default_thresholds = {
            "temperature": [
                AlertThreshold("temperature", min_value=16, level=AlertLevel.WARNING, 
                             message="室内温度过低，建议加强保暖措施"),
                AlertThreshold("temperature", max_value=32, level=AlertLevel.WARNING,
                             message="室内温度过高，建议开启空调或通风"),
                AlertThreshold("temperature", min_value=10, level=AlertLevel.CRITICAL,
                             message="室内温度严重偏低，可能影响学生健康"),
                AlertThreshold("temperature", max_value=35, level=AlertLevel.CRITICAL,
                             message="室内温度严重偏高，可能影响学生健康")
            ],
            "humidity": [
                AlertThreshold("humidity", min_value=30, level=AlertLevel.WARNING,
                             message="室内湿度过低，可能导致皮肤干燥"),
                AlertThreshold("humidity", max_value=70, level=AlertLevel.WARNING,
                             message="室内湿度过高，可能滋生细菌"),
                AlertThreshold("humidity", min_value=20, level=AlertLevel.CRITICAL,
                             message="室内湿度严重偏低，影响舒适度"),
                AlertThreshold("humidity", max_value=80, level=AlertLevel.CRITICAL,
                             message="室内湿度严重偏高，影响舒适度")
            ],
            "aqi": [
                AlertThreshold("aqi", max_value=3, level=AlertLevel.WARNING,
                             message="空气质量轻度污染，建议减少户外活动"),
                AlertThreshold("aqi", max_value=4, level=AlertLevel.CRITICAL,
                             message="空气质量中度污染，建议关闭门窗"),
                AlertThreshold("aqi", max_value=5, level=AlertLevel.EMERGENCY,
                             message="空气质量重度污染，立即关闭门窗并启动净化器")
            ],
            "eco2": [
                AlertThreshold("eco2", max_value=1000, level=AlertLevel.WARNING,
                             message="CO2浓度偏高，建议开窗通风"),
                AlertThreshold("eco2", max_value=1500, level=AlertLevel.CRITICAL,
                             message="CO2浓度过高，立即开窗通风"),
                AlertThreshold("eco2", max_value=2000, level=AlertLevel.EMERGENCY,
                             message="CO2浓度危险，立即疏散并通风")
            ],
            "tvoc": [
                AlertThreshold("tvoc", max_value=500, level=AlertLevel.WARNING,
                             message="TVOC浓度偏高，建议检查污染源"),
                AlertThreshold("tvoc", max_value=1000, level=AlertLevel.CRITICAL,
                             message="TVOC浓度过高，立即通风并排查污染源")
            ],
            "noise": [
                AlertThreshold("noise", max_value=60, level=AlertLevel.WARNING,
                             message="噪音水平较高，可能影响学习效果"),
                AlertThreshold("noise", max_value=70, level=AlertLevel.CRITICAL,
                             message="噪音水平过高，严重影响学习环境")
            ],
            "uv_index": [
                AlertThreshold("uv_index", max_value=3, level=AlertLevel.WARNING,
                             message="紫外线强度较高，户外活动请注意防护"),
                AlertThreshold("uv_index", max_value=4, level=AlertLevel.CRITICAL,
                             message="紫外线强度很高，避免长时间户外暴露")
            ]
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 将配置转换为AlertThreshold对象
                thresholds = {}
                for metric, threshold_list in config.items():
                    thresholds[metric] = [
                        AlertThreshold(**threshold) for threshold in threshold_list
                    ]
                return thresholds
        except FileNotFoundError:
            self.logger.info(f"配置文件 {self.config_file} 不存在，使用默认配置")
            # 保存默认配置
            self._save_thresholds(default_thresholds)
            return default_thresholds
    
    def _save_thresholds(self, thresholds: Dict[str, List[AlertThreshold]]):
        """保存警报阈值配置"""
        config = {}
        for metric, threshold_list in thresholds.items():
            config[metric] = [
                {
                    'metric': t.metric,
                    'min_value': t.min_value,
                    'max_value': t.max_value,
                    'level': t.level.value,
                    'message': t.message,
                    'enabled': t.enabled
                }
                for t in threshold_list
            ]
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """添加警报回调函数"""
        self.callbacks.append(callback)
    
    def check_thresholds(self, sensor_data: Dict[str, float]) -> List[Alert]:
        """检查传感器数据是否超过阈值"""
        new_alerts = []
        
        for metric, value in sensor_data.items():
            if metric not in self.thresholds:
                continue
            
            for threshold in self.thresholds[metric]:
                if not threshold.enabled:
                    continue
                
                alert_triggered = False
                threshold_value = None
                
                # 检查最小值阈值
                if threshold.min_value is not None and value < threshold.min_value:
                    alert_triggered = True
                    threshold_value = threshold.min_value
                
                # 检查最大值阈值
                if threshold.max_value is not None and value > threshold.max_value:
                    alert_triggered = True
                    threshold_value = threshold.max_value
                
                if alert_triggered:
                    alert_id = f"{metric}_{threshold.level.value}_{int(time.time())}"
                    
                    # 检查是否已存在相同类型的活跃警报
                    existing_alert_key = f"{metric}_{threshold.level.value}"
                    if existing_alert_key not in self.active_alerts:
                        alert = Alert(
                            id=alert_id,
                            timestamp=datetime.now(),
                            metric=metric,
                            current_value=value,
                            threshold_value=threshold_value,
                            level=threshold.level,
                            message=threshold.message
                        )
                        
                        self.active_alerts[existing_alert_key] = alert
                        self.alert_history.append(alert)
                        new_alerts.append(alert)
                        
                        # 记录警报日志
                        self.alert_logger.warning(
                            f"警报触发 - {metric}: {value} "
                            f"{'<' if threshold.min_value and value < threshold.min_value else '>'} "
                            f"{threshold_value} - {threshold.message}"
                        )
                        
                        # 调用回调函数
                        for callback in self.callbacks:
                            try:
                                callback(alert)
                            except Exception as e:
                                self.logger.error(f"警报回调执行失败: {e}")
        
        # 检查是否有警报需要解除
        self._check_alert_resolution(sensor_data)
        
        return new_alerts
    
    def _check_alert_resolution(self, sensor_data: Dict[str, float]):
        """检查警报是否应该解除"""
        resolved_alerts = []
        
        for alert_key, alert in list(self.active_alerts.items()):
            metric = alert.metric
            if metric not in sensor_data:
                continue
                
            current_value = sensor_data[metric]
            
            # 查找对应的阈值配置
            threshold = None
            for t in self.thresholds.get(metric, []):
                if t.level == alert.level:
                    threshold = t
                    break
            
            if threshold is None:
                continue
            
            # 检查是否回到安全范围
            is_safe = True
            if threshold.min_value is not None and current_value < threshold.min_value:
                is_safe = False
            if threshold.max_value is not None and current_value > threshold.max_value:
                is_safe = False
            
            if is_safe:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                resolved_alerts.append(alert_key)
                
                self.alert_logger.info(
                    f"警报解除 - {metric}: {current_value} 已回到安全范围"
                )
        
        # 移除已解除的警报
        for alert_key in resolved_alerts:
            del self.active_alerts[alert_key]
    
    def get_active_alerts(self) -> List[Alert]:
        """获取当前活跃的警报"""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict:
        """获取警报摘要"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_active": len(active_alerts),
            "by_level": {
                "emergency": len([a for a in active_alerts if a.level == AlertLevel.EMERGENCY]),
                "critical": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                "warning": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                "info": len([a for a in active_alerts if a.level == AlertLevel.INFO])
            },
            "recent_alerts": [
                {
                    "metric": a.metric,
                    "level": a.level.value,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                    "current_value": a.current_value
                }
                for a in sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)[:5]
            ]
        }
        
        return summary
    
    def clear_resolved_alerts(self):
        """清除已解除的历史警报"""
        self.alert_history = [a for a in self.alert_history if not a.resolved]
    
    def export_alert_log(self, filename: str = None) -> str:
        """导出警报日志"""
        if filename is None:
            filename = f"alert_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "active_alerts": [
                {
                    "id": a.id,
                    "timestamp": a.timestamp.isoformat(),
                    "metric": a.metric,
                    "current_value": a.current_value,
                    "threshold_value": a.threshold_value,
                    "level": a.level.value,
                    "message": a.message,
                    "resolved": a.resolved,
                    "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
                }
                for a in self.get_active_alerts()
            ],
            "alert_history": [
                {
                    "id": a.id,
                    "timestamp": a.timestamp.isoformat(),
                    "metric": a.metric,
                    "current_value": a.current_value,
                    "threshold_value": a.threshold_value,
                    "level": a.level.value,
                    "message": a.message,
                    "resolved": a.resolved,
                    "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
                }
                for a in self.alert_history[-100:]  # 最近100条记录
            ]
        }
        
        filepath = f"logs/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filepath

# 示例回调函数
def console_alert_callback(alert: Alert):
    """控制台警报回调"""
    level_emojis = {
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.CRITICAL: "🚨",
        AlertLevel.EMERGENCY: "🆘"
    }
    
    print(f"{level_emojis.get(alert.level, '🔔')} "
          f"[{alert.level.value.upper()}] "
          f"{alert.metric}: {alert.current_value} - {alert.message}")

def web_notification_callback(alert: Alert):
    """Web通知回调（可扩展为实际的Web推送）"""
    # 这里可以集成Web推送、邮件通知、短信等
    notification_data = {
        "title": f"环境监测警报 - {alert.level.value.upper()}",
        "body": f"{alert.metric}: {alert.current_value} - {alert.message}",
        "icon": "alert-icon.png",
        "tag": f"alert_{alert.metric}",
        "timestamp": alert.timestamp.isoformat()
    }
    
    # 保存到通知队列文件
    try:
        with open('logs/notifications.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(notification_data, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"保存通知失败: {e}")

if __name__ == "__main__":
    # 测试警报系统
    alert_system = EnvironmentalAlertSystem()
    
    # 添加回调函数
    alert_system.add_alert_callback(console_alert_callback)
    alert_system.add_alert_callback(web_notification_callback)
    
    # 模拟传感器数据
    test_data = {
        "temperature": 35.5,  # 温度过高
        "humidity": 85,       # 湿度过高
        "aqi": 4,            # 空气质量差
        "eco2": 1200,        # CO2浓度高
        "tvoc": 600,         # TVOC浓度高
        "noise": 75,         # 噪音高
        "uv_index": 5        # 紫外线强
    }
    
    print("🧪 测试环境警报系统...")
    print(f"测试数据: {test_data}")
    print()
    
    # 检查阈值
    alerts = alert_system.check_thresholds(test_data)
    
    print(f"\n📊 警报摘要:")
    summary = alert_system.get_alert_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 导出警报日志
    log_file = alert_system.export_alert_log()
    print(f"\n📄 警报日志已导出到: {log_file}")
