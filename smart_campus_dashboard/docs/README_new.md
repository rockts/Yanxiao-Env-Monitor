# 烟铺小学智慧校园仪表盘系统

## 项目概述

烟铺小学智慧校园仪表盘系统是一个用于监控校园环境数据的可视化平台，通过实时显示各类环境传感器数据和校园摄像头画面，为校园管理提供决策支持。

## 目录结构

项目已经进行了优化整理，现在的目录结构如下：

```
smart_campus_dashboard/
├── src/                   # 主要源代码目录
│   ├── main.py            # 主程序（仪表盘界面）
│   ├── mqtt_bridge.py     # MQTT桥接程序
│   ├── mqtt_relay.py      # MQTT中继程序
│   ├── send_test_data.py  # 传感器测试数据发生器
│   ├── send_video_test.py # 视频测试数据发生器
│   └── simple_mqtt_broker.py # 简易MQTT代理
├── config/                # 配置文件目录
│   ├── config.json        # 主配置文件
│   └── python_config.env  # Python环境配置
├── logs/                  # 日志文件目录
├── utils/                 # 工具脚本目录
├── scripts/               # 旧版启动脚本目录
├── docs/                  # 文档目录
├── backup/                # 备份和旧版文件
├── start.command          # 简化的启动脚本
└── start_test.command     # 带测试数据的启动脚本

```

## 启动方法

### 基本仪表盘启动

```bash
./start.command
```

此脚本将启动基本仪表盘，需要外部 MQTT 服务提供数据源。

### 测试模式启动

```bash
./start_test.command
```

此脚本会自动启动：

1. MQTT 代理服务器
2. 传感器测试数据发生器
3. 视频测试数据发生器
4. 仪表盘主程序

适合在没有实际传感器和摄像头的环境中进行测试。

## 配置文件

系统配置存储在 `config/config.json` 文件中，主要参数包括：

- `mqtt_broker_host`：MQTT 服务器地址
- `mqtt_broker_port`：MQTT 服务器端口
- `mqtt_camera_topic`：摄像头数据的 MQTT 主题
- `update_interval`：界面更新间隔（秒）
- `chart_history_maxlen`：图表历史数据点数量

## 界面优化

本次优化包括以下方面：

1. **视频显示改进**：

   - 增加了视频显示区域尺寸（450x340）
   - 改进了视频帧处理逻辑，提高显示稳定性

2. **布局优化**：

   - 调整了面板比例为 3:3:7（左:中:右）
   - 改进了左侧数据区域的对齐方式
   - 数值采用右对齐，提高美观度

3. **文件组织**：
   - 按功能将文件分类到各个目录
   - 简化了启动流程
   - 统一配置文件管理

## 注意事项

- 首次运行时，系统会在 logs 目录创建日志文件
- 如遇显示问题，可检查 config/config.json 中的配置参数
- 视频流问题可通过运行 src/send_video_test.py 测试
