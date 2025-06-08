# 研学环境监控系统

## 项目概述

一个基于 Python 和 Flask 的环境监控系统，支持温度、湿度、气压等环境数据的实时监控，提供 Web 仪表板和 MQTT 数据传输功能。

## 项目结构

```
Yanxiao-Env-Monitor/
├── README.md                   # 项目说明文档
├── .gitignore                  # Git忽略文件配置
├── requirements.txt            # Python依赖包配置
├── monitoring/                 # 监控核心模块
│   ├── production_health_check.py    # 生产环境健康检查
│   ├── monitoring_daemon.py          # 监控守护进程
│   └── mqtt_diagnostic.py            # MQTT诊断工具
├── dashboard/                  # Web仪表板
│   ├── app.py                 # Flask应用主程序
│   ├── static/                # 静态资源
│   ├── templates/             # HTML模板
│   └── config/                # 配置文件
├── scripts/                   # 脚本工具
│   ├── monitor_manager.sh     # 监控管理脚本
│   ├── health_monitor.sh      # 健康检查脚本
│   ├── setup_cron.sh          # 定时任务设置
│   └── log_rotation.sh        # 日志轮转脚本
├── deployment/                # 部署配置
│   ├── deploy_production.sh   # 生产环境部署
│   └── upload_files.sh        # 文件上传脚本
├── docs/                      # 项目文档
│   ├── PRODUCTION_MONITORING_GUIDE.md
│   ├── MQTT_DEPRECATION_FIX_REPORT.md
│   └── ...
├── logs/                      # 日志文件
└── assets/                    # 资源文件
```

## 功能特性

- 🌡️ 实时环境数据监控（温度、湿度、气压）
- 📊 Web 仪表板可视化
- 📡 MQTT 数据传输支持
- 🔔 异常告警系统
- 📈 历史数据分析
- 🚀 自动化部署
- 📋 健康检查监控

## 快速开始

### 环境要求

- Python 3.8+
- Flask
- MQTT Broker (如 Mosquitto)

### 安装步骤

1. 克隆项目

```bash
git clone [repository-url]
cd Yanxiao-Env-Monitor
```

2. 创建虚拟环境

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# 或
env\Scripts\activate     # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境

```bash
cp dashboard/config/config.example.py dashboard/config/config.py
# 编辑配置文件
```

5. 启动服务

```bash
# 启动Web仪表板
cd dashboard && python app.py

# 启动监控守护进程
python monitoring/monitoring_daemon.py
```

## 部署指南

详细的生产环境部署指南请参考：[PRODUCTION_DEPLOYMENT_GUIDE.md](docs/PRODUCTION_DEPLOYMENT_GUIDE.md)

## 监控指南

系统监控和维护指南请参考：[PRODUCTION_MONITORING_GUIDE.md](docs/PRODUCTION_MONITORING_GUIDE.md)

## 开发指南

### 目录说明

- `monitoring/` - 核心监控逻辑
- `dashboard/` - Web 界面和 API
- `scripts/` - 运维脚本
- `deployment/` - 部署相关
- `docs/` - 项目文档

### 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者：[维护者姓名]
- 问题反馈：[GitHub Issues]
