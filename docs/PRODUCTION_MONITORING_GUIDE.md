# 烟小环境监测系统 - 生产环境监控使用指南

## 📋 概述

本文档介绍如何使用新开发的监控工具来持续监控生产环境中的烟小环境监测系统（运行在 `192.168.1.115:5052`）。

## 🛠️ 监控工具组件

### 1. 健康检查工具 (`production_health_check.py`)

- **功能**: 对生产服务器进行全面健康检查
- **检查项目**: 网络连接、端口状态、API 服务、数据流、MQTT 连接、日志获取
- **支持模式**: 完整检查、快速检查、日志获取、数据检查

### 2. 自动监控守护进程 (`monitoring_daemon.py`)

- **功能**: 自动化监控生产环境，定期检查并发送告警
- **特性**: 自动告警、监控历史记录、日报告生成、智能冷却
- **告警条件**: 连续失败、健康评分过低、网络/API/MQTT 异常

### 3. 监控管理脚本 (`monitor_manager.sh`)

- **功能**: 统一管理监控工具的启动、停止、状态查看
- **便捷性**: 一键操作、日志查看、状态报告

## 🚀 快速开始

### 1. 执行单次健康检查

```bash
# 进入项目目录
cd /Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor

# 完整健康检查
python3 production_health_check.py

# 快速检查
python3 production_health_check.py quick

# 仅获取日志
python3 production_health_check.py logs

# 仅检查数据流
python3 production_health_check.py data
```

### 2. 启动自动监控

```bash
# 使用监控管理脚本 (推荐)
./monitor_manager.sh start          # 默认5分钟检查一次
./monitor_manager.sh start 180      # 每3分钟检查一次
./monitor_manager.sh start 600      # 每10分钟检查一次

# 或直接使用Python脚本
python3 monitoring_daemon.py start 300
```

### 3. 查看监控状态

```bash
# 查看完整状态
./monitor_manager.sh status

# 查看监控守护进程状态
./monitor_manager.sh quick
```

## 📊 监控管理

### 启动监控

```bash
./monitor_manager.sh start [检查间隔秒数]
```

### 停止监控

```bash
./monitor_manager.sh stop
```

### 重启监控

```bash
./monitor_manager.sh restart [检查间隔秒数]
```

### 查看日志

```bash
./monitor_manager.sh logs monitor      # 监控日志
./monitor_manager.sh logs daemon       # 守护进程日志
./monitor_manager.sh logs production   # 生产服务器日志
```

### 生成报告

```bash
./monitor_manager.sh report
```

## 📈 监控数据解读

### 健康评分计算

- **100%**: 所有检查项目通过
- **80-99%**: 大部分正常，有轻微问题
- **60-79%**: 存在明显问题，需要关注
- **60%以下**: 系统异常，需要立即处理

### 检查项目说明

1. **网络连接**: 能否 ping 通生产服务器
2. **端口状态**: 5052 端口是否开放
3. **API 服务**: Flask API 是否响应正常
4. **数据流**: 能否获取传感器数据
5. **健康端点**: /health 端点是否正常
6. **SSH 服务**: 能否 SSH 连接服务器
7. **日志获取**: 能否获取远程日志

### MQTT 连接状态

- **已连接**: MQTT 正常连接到 lot.lekee.cc
- **未连接**: MQTT 连接异常，传感器数据可能不更新

## 🚨 告警机制

### 告警触发条件

1. **连续失败**: 连续 3 次检查失败
2. **健康评分低**: 评分低于 60%
3. **网络异常**: 无法连接到服务器
4. **API 异常**: API 服务无响应
5. **MQTT 断开**: MQTT 连接中断
6. **数据流异常**: 无法获取传感器数据

### 告警冷却机制

- **冷却时间**: 30 分钟
- **作用**: 避免短时间内重复告警
- **例外**: 严重级别告警可能绕过冷却

### 告警级别

- **🔴 严重 (Critical)**: 网络连接失败、API 服务异常、连续失败
- **🟡 警告 (Warning)**: MQTT 断开、数据流异常、健康评分偏低

## 📂 文件结构

```
/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/
├── production_health_check.py    # 健康检查工具
├── monitoring_daemon.py          # 自动监控守护进程
├── monitor_manager.sh            # 监控管理脚本
└── logs/                         # 日志目录
    ├── production_monitor.log    # 监控日志
    ├── monitor_daemon.log        # 守护进程日志
    ├── monitor_daemon.pid        # 守护进程PID文件
    └── daily_report_YYYYMMDD.txt # 日报告
```

## 🔧 配置说明

### 监控目标配置

在 `production_health_check.py` 中修改：

```python
self.server_ip = "192.168.1.115"    # 生产服务器IP
self.server_port = 5052              # 服务端口
self.ssh_user = "rockts"             # SSH用户名
```

### 告警阈值配置

在 `monitoring_daemon.py` 中修改：

```python
self.alert_config = {
    'consecutive_failures': 3,        # 连续失败次数
    'health_score_threshold': 60,     # 健康评分阈值
    'data_freshness_minutes': 10,     # 数据新鲜度
}
```

### 监控间隔配置

```bash
# 可在启动时指定间隔（秒）
./monitor_manager.sh start 300    # 5分钟
./monitor_manager.sh start 180    # 3分钟
./monitor_manager.sh start 600    # 10分钟
```

## 📋 日常使用建议

### 1. 启动监控

在每天开始工作时启动监控：

```bash
./monitor_manager.sh start 300
```

### 2. 定期检查状态

每隔几小时查看一次状态：

```bash
./monitor_manager.sh status
```

### 3. 问题排查

当收到告警时，执行详细检查：

```bash
./monitor_manager.sh check
./monitor_manager.sh logs production
```

### 4. 查看日报告

每天结束时查看监控报告：

```bash
./monitor_manager.sh report
```

## 🎯 最佳实践

1. **长期监控**: 建议全天候运行监控守护进程
2. **合理间隔**: 生产环境推荐 5-10 分钟检查间隔
3. **日志管理**: 定期清理或轮转日志文件
4. **告警处理**: 及时响应告警，分析根本原因
5. **备份监控**: 可在多台机器上运行监控备份

## 🔍 故障排查

### 监控工具无法运行

1. 检查 Python 环境和依赖
2. 确认网络连接到生产服务器
3. 验证 SSH 密钥配置

### 健康检查失败

1. 检查生产服务器是否正常运行
2. 验证 MQTT 服务 lot.lekee.cc 是否可达
3. 查看生产服务器日志

### 告警过于频繁

1. 调整告警阈值
2. 增加冷却时间
3. 检查网络稳定性

## 📞 技术支持

如需进一步帮助，请：

1. 查看详细日志文件
2. 运行完整健康检查
3. 检查生产服务器状态
4. 联系系统管理员

---

**文档版本**: v1.0  
**更新时间**: 2025-01-26  
**适用环境**: 烟小环境监测系统生产环境
