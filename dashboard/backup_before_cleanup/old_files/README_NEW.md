# 智慧校园环境监测系统

## 项目说明

本项目是一个智慧校园环境监测系统，通过 MQTT 协议获取各类环境监测数据，并在仪表盘上实时显示。
系统支持多种数据类型，包括温湿度、CO2 浓度、TVOC、PM2.5、PM10、甲醛、UV 指数等。

## 新版项目结构

```
smart_campus_dashboard/
├── config/               # 配置文件目录
│   ├── config.json       # 默认配置
│   └── local_config.json # 本地配置（优先）
├── data/                 # 数据文件目录
├── docs/                 # 文档目录
├── logs/                 # 日志文件目录
├── scripts/              # 脚本文件目录
│   ├── unix/             # Unix系统脚本（macOS、Linux）
│   └── windows/          # Windows系统脚本
├── src/                  # 源代码目录
│   ├── core/             # 核心组件
│   │   ├── config_manager.py    # 配置管理器
│   │   └── log_manager.py       # 日志管理器
│   ├── services/         # 服务组件
│   │   ├── mqtt_bridge_service.py  # MQTT桥接服务
│   │   ├── mqtt_relay_service.py   # MQTT中继服务
│   │   └── simple_mqtt_broker.py   # 简易MQTT代理
│   ├── simulators/       # 模拟器组件
│   │   ├── sensor_data_simulator.py  # 传感器数据模拟器
│   │   └── video_stream_simulator.py # 视频流模拟器
│   ├── ui/               # 用户界面组件
│   │   ├── dashboard.py          # 主仪表盘界面
│   │   └── simple_dashboard.py   # 简化版仪表盘界面
│   ├── utils/            # 工具类组件
│   └── main_dashboard.py # 主入口文件
├── backup/               # 备份文件目录（仅供参考，不用于生产）
├── launch.py             # 统一启动器
└── README.md             # 项目说明文件
```

## 安装与依赖

本项目基于 Python 3.7+开发，依赖以下主要库：

- tkinter: 用于 GUI 开发
- paho-mqtt: 用于 MQTT 通信
- matplotlib: 用于图表绘制
- pillow (PIL): 用于图像处理

安装依赖：

```bash
# 推荐使用虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或者
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 使用统一启动器

```bash
# 启动完整仪表盘
python launch.py --dashboard

# 启动简化版仪表盘
python launch.py --simple

# 启动调试模式
python launch.py --debug

# 使用本地MQTT服务
python launch.py --local-mqtt

# 启用数据模拟
python launch.py --simulate

# 启用视频流模拟
python launch.py --video

# 指定配置文件
python launch.py --config path/to/config.json
```

### 2. 使用脚本启动

```bash
# macOS/Linux
./scripts/unix/start.command
./scripts/unix/start_with_local_mqtt.command

# Windows
scripts\windows\start_dashboard_windows.bat
```

## 配置说明

配置文件示例 (config.json):

```json
{
 "mqtt_broker_host": "localhost",
 "mqtt_broker_port": 1883,
 "mqtt_client_id": "smart_campus_dashboard_client",
 "mqtt_camera_topic": "sc/camera/stream",
 "mqtt_weather_topic": "sc/weather/data"
}
```

本地配置文件 (local_config.json) 中的设置会覆盖默认配置。

## 开发者说明

- 主要入口文件位于 `src/main_dashboard.py`
- UI 组件位于 `src/ui/` 目录
- 服务组件位于 `src/services/` 目录
- 核心工具位于 `src/core/` 目录
- 模拟器位于 `src/simulators/` 目录

## 注意事项

- 请确保 MQTT 服务器已经运行
- 如需本地测试，可使用 `--local-mqtt` 参数启动内置的 MQTT 服务
