# 烟铺小学智慧环境监测物联网系统

## 项目概述

烟铺小学智慧环境监测物联网系统是一个集成了室内外环境数据采集、可视化展示、AI 健康建议、校园监控等功能的现代化物联网系统。通过 MQTT 协议实现传感器数据的实时采集与传输，结合 Web 技术提供直观的大屏可视化界面，助力校园环境智能管理与健康守护。

## 核心功能

### 🌡️ 环境数据监测

- **实时监测**: 温度、湿度、空气质量(AQI)、PM2.5、eCO₂、TVOC、紫外线、噪音等多项环境指标
- **数据可视化**: 美观的仪表盘、折线图，动态反映环境变化趋势，y 轴自适应且曲线平滑
- **历史数据**: 数据存储与历史趋势分析
- **异常预警**: 环境参数超标时的实时告警机制

### 🤖 AI 智能建议

- **室内建议**: 基于实时环境数据生成智能化的室内环境改善建议
- **室外建议**: 结合天气和空气质量数据提供户外活动指导
- **健康守护**: 贴合校园场景的个性化健康建议

### 📹 校园监控集成

- **实时监控**: 支持图片快照和流媒体监控
- **自动刷新**: 提升监控画面的实时性
- **多点位**: 支持多个监控点位的统一管理

### 💻 现代化界面

- **响应式设计**: 适配各种屏幕尺寸，特别优化大屏显示效果
- **实时更新**: 数据实时刷新，界面流畅美观
- **用户友好**: 信息分区清晰，操作简单直观

## 快速启动

### 系统要求

- Python 3.8+
- 现代浏览器 (Chrome/Firefox/Safari/Edge)
- 网络连接 (用于外部 API 调用)

### 一键启动 (推荐)

```bash
# 进入项目目录
cd /path/to/Yanxiao-Env-Monitor/dashboard

# 启动所有服务
./scripts/start_services.sh

# 检查服务状态
./scripts/check_status.sh
```

### 手动启动

```bash
# 1. 安装依赖
cd dashboard
source env/bin/activate
pip install -r requirements.txt

# 2. 启动后端服务
python3 mqtt_flask_server.py

# 3. 启动前端服务 (新终端窗口)
python3 -m http.server 8080 --bind 0.0.0.0
```

### 访问地址

- **前端大屏**: http://localhost:8080/index.html
- **局域网访问**: http://[本机 IP]:8080/index.html
- **后端 API**: http://localhost:5051/api/status

### 停止服务

```bash
./scripts/stop_services.sh
```

## Git 多电脑同步管理

本项目提供了完整的Git多电脑同步解决方案，支持通过云盘同步文件但保持Git提交记录一致。

### 🚀 快速同步

```bash
# 快速提交并同步当前更改
./scripts/quick_sync.sh "更新描述"

# 使用默认提交信息
./scripts/quick_sync.sh
```

### 🔧 完整同步管理

```bash
# 运行交互式同步工具
./scripts/git_sync_tool.sh

# 自动同步管理器
./scripts/sync_manager.sh
```

### 📋 同步方案

#### 方案A：远程仓库同步（推荐）
- 在GitHub/GitLab/Gitee创建仓库
- 支持多人协作和完整版本控制
- 自动推送拉取同步

#### 方案B：Bundle文件同步
- 适合私有项目或无网络环境
- 通过云盘传输Git bundle文件
- 保持完整的Git历史记录

### 🔄 自动同步（可选）

```bash
# 启动自动同步守护进程
./scripts/sync_manager.sh start

# 查看自动同步状态
./scripts/sync_manager.sh status

# 停止自动同步
./scripts/sync_manager.sh stop
```

### 📖 详细文档

- `git_sync_guide.md` - 基础同步指南
- `MULTI_COMPUTER_SYNC_SETUP.md` - 完整设置指南
- `scripts/sync_config.json` - 同步配置文件

## 技术架构

### 前端技术栈

- **Vue3** + **ECharts** + **Element Plus** - 现代化前端框架
- **原生 JavaScript** - 实时数据处理与交互
- **响应式 CSS** - 适配各种设备屏幕

### 后端技术栈

- **Flask** - 轻量级 Web 框架
- **paho-mqtt** - MQTT 协议客户端
- **通义千问-Turbo** - AI 大模型集成
- **requests** - HTTP 请求处理

### 数据源

- **本地 MQTT 传感器** - 实时环境数据采集
- **OpenWeather API** - 外部天气与空气质量数据
- **AI 大模型 API** - 智能建议生成

## 项目结构

```
Yanxiao-Env-Monitor/                    # 项目根目录
├── README.md                          # 项目主要说明文档
├── .gitignore                         # Git忽略文件配置
├── environment.mp                     # 环境配置文件
│
├── dashboard/                         # 核心仪表盘系统
│   ├── README.md                     # 仪表盘子系统说明
│   ├── PROJECT_STRUCTURE.md          # 项目结构详细说明
│   ├── DEPLOYMENT_REPORT.md          # 部署完成报告
│   ├── requirements.txt              # Python依赖配置
│   ├── mqtt_flask_server.py          # 后端Flask服务主文件
│   ├── index.html                    # 前端主页面
│   ├── 烟小智慧环境监测物联网大屏.mpdb  # MindManager设计文档
│   │
│   ├── frontend/                     # 前端文件目录
│   │   ├── debug.html               # 调试页面
│   │   ├── index_simple.html        # 简化版页面
│   │   ├── assets/                  # 前端资源文件
│   │   │   └── img/                 # 图片资源
│   │   │       ├── logo.png
│   │   │       └── logo_white.png
│   │   └── test/                    # 测试页面集合
│   │       ├── test.html
│   │       ├── test_frontend.html
│   │       ├── test_responsive.html
│   │       └── test_video.html
│   │
│   ├── scripts/                     # 系统管理脚本
│   │   ├── start_services.sh        # 启动服务脚本
│   │   ├── stop_services.sh         # 停止服务脚本
│   │   ├── check_status.sh          # 状态检查脚本
│   │   └── install_dependencies.sh  # 依赖安装脚本
│   │
│   ├── logs/                        # 系统运行日志
│   ├── env/                         # Python虚拟环境
│   └── __pycache__/                 # Python缓存文件
│
├── assets/                          # 项目资源文件
│   ├── dashboard_concept.png        # 系统概念图
│   ├── data_collection_ventilation_control.png
│   ├── mobile_terminal.png          # 移动端界面
│   ├── smart_terminal.png           # 智能终端界面
│   ├── xingkong_board_display.png   # 星空板显示效果
│   ├── bg_image.png                 # 背景图片
│   ├── tvoc_icon.png                # TVOC图标
│   └── 截屏2025-05-18 20.55.08.png  # 系统截图
│
├── env/                             # 项目级Python虚拟环境
└── logs/                            # 历史运行日志
    ├── dashboard_20250519_023326.log
    ├── dashboard_20250521_*.log     # 按日期的历史日志
    └── ...
```

## 系统特性

### 🚀 性能优势

- **快速启动**: 系统启动时间 < 10 秒
- **实时响应**: API 响应时间 < 100ms
- **低资源占用**: 内存使用 < 80MB
- **高稳定性**: 7x24 小时稳定运行

### 📱 多端适配

- **大屏优化**: 专为校园大屏显示优化
- **响应式设计**: 支持 PC、平板、手机访问
- **局域网共享**: 支持多设备同时访问

### 🔧 易于维护

- **一键管理**: 提供完整的启动/停止/状态检查脚本
- **日志完善**: 详细的运行日志便于问题诊断
- **模块化**: 前后端分离，便于独立开发和维护

## 开发团队

本项目为烟铺小学智慧校园环境监测系统，集成了现代物联网技术、人工智能、Web 可视化等多项技术栈。

## 详细文档

- **仪表盘系统**: [dashboard/README.md](dashboard/README.md)
- **项目结构**: [dashboard/PROJECT_STRUCTURE.md](dashboard/PROJECT_STRUCTURE.md)
- **部署报告**: [dashboard/DEPLOYMENT_REPORT.md](dashboard/DEPLOYMENT_REPORT.md)

## 版权与许可

© 2025 烟铺小学智慧校园项目组  
本项目遵循开源协议，仅供教育和学习使用。
