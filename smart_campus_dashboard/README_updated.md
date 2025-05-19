# 烟铺小学智慧校园环境监测系统

## 项目概述

烟铺小学智慧校园环境监测系统是一个大屏展示项目，实时监控并展示校园环境数据，包括温度、湿度、空气质量、噪音、天气以及实时摄像头监控画面等。该系统通过 MQTT 协议接收各传感器数据，以直观的界面呈现给用户，并提供基于数据的智能环境建议。

## 功能特点

- **实时数据监测**：显示环境温度、湿度、AQI 空气质量指数、eCO2、TVOC、紫外线指数、噪音等数据
- **实时图表**：以时间序列图表展示温度、湿度、噪音的历史变化趋势
- **摄像头监控**：实时显示校园监控画面
- **天气信息**：通过第三方 API 获取并展示当前天气状况、风速等信息
- **智能建议**：基于监测数据提供环境改善的智能建议
- **模拟模式**：在无传感器或测试环境中，可启用模拟数据模式

## 系统要求

- Python 3.8 或更高版本
- 依赖库：
  - paho-mqtt：MQTT 通信
  - Pillow (PIL)：图像处理
  - matplotlib：数据可视化图表
  - tkinter：UI 界面（Python 标准库）
  - requests：API 网络请求

## 安装与运行

### 快速启动（推荐）

#### macOS 用户

1. 双击 `start_dashboard_macos.command` 文件
2. 如果出现权限提示，请在终端执行: `chmod +x start_dashboard_macos.command`

#### Windows 用户

1. 双击 `start_dashboard_windows.bat` 文件

### 手动启动

1. **安装依赖**：

   ```bash
   pip install paho-mqtt Pillow matplotlib requests
   ```

2. **运行方式**：

   - 使用原始启动脚本：
     ```bash
     ./start_dashboard.sh
     ```
   - 脚本选项：

     - `--start-all`：同时启动主面板和测试数据发送程序
     - `--start-dashboard`：仅启动主面板程序
     - `--start-test-data`：仅启动测试数据发送程序
     - `--mqtt-server=<地址>`：指定 MQTT 服务器地址
     - `--mqtt-port=<端口号>`：指定 MQTT 服务器端口

   - 或直接运行主程序（**使用 python3 命令**）：
     ```bash
     python3 main_all_fixed.py
     ```

3. **测试数据模拟**：
   如果没有真实传感器数据，可运行模拟数据发送程序：
   ```bash
   python3 send_test_data.py
   ```

## 故障排除

1. **如果窗口无法显示或者程序卡住**：

   - 确保使用 `python3` 而不是 `python` 命令运行
   - 使用提供的启动脚本 `start_dashboard_macos.command`(macOS) 或 `start_dashboard_windows.bat`(Windows)

2. **如果图表不更新**：

   - 检查 MQTT 连接是否成功
   - 启动测试数据发送器 `python3 send_test_data.py`

3. **如果程序 CPU 使用率高**：
   - 调整更新频率：在 `config.json` 中增加 `"update_interval": 15`（单位：秒）

## MQTT 主题结构

系统通过以下 MQTT 主题接收数据：

| 主题               | 描述               | 数据格式                                     |
| ------------------ | ------------------ | -------------------------------------------- |
| `siot/环境温度`    | 环境温度数据       | 数值（°C）                                   |
| `siot/环境湿度`    | 环境湿度数据       | 数值（%RH）                                  |
| `siot/aqi`         | 空气质量指数       | 数值                                         |
| `siot/tvoc`        | 总挥发性有机化合物 | 数值（ppb）                                  |
| `siot/eco2`        | 等效二氧化碳浓度   | 数值（ppm）                                  |
| `siot/紫外线指数`  | 紫外线强度指数     | 数值                                         |
| `siot/uv风险等级`  | 紫外线风险等级     | 文本（低/中/高）                             |
| `siot/噪音`        | 噪音水平           | 数值（dB）                                   |
| `sc/camera/stream` | 摄像头画面流       | Base64 编码图像或 JSON 对象（含 image 字段） |
| `sc/weather/data`  | 天气数据           | JSON 对象                                    |

### 数据格式示例

- **传感器数据**：直接发送数值或字符串，如 `"25.6"` 或 `"低"`
- **摄像头数据**：
  ```json
  {
   "image": "base64编码的图像数据..."
  }
  ```
- **天气数据**：
  ```json
  {
   "weather": [{ "description": "晴天", "icon": "01d" }],
   "main": {
    "temp": 25.6,
    "humidity": 65
   },
   "wind": {
    "speed": 3.1
   }
  }
  ```

## 配置文件

系统配置存储在 `config.json` 文件中，可根据需要调整以下参数：

```json
{
 "mqtt": {
  "host": "192.168.1.129",
  "port": 1883,
  "username": "siot",
  "password": "dfrobot"
 },
 "topics": {
  "temp": {
   "base_topic_name": "环境温度",
   "color": "#FF5733",
   "unit": "°C"
  },
  "humi": {
   "base_topic_name": "环境湿度",
   "color": "#3385FF",
   "unit": "%"
  }
 },
 "update_interval": 10,
 "chart_history_length": 60
}
```

## 最近更新

- **修复性能问题**：优化图表渲染逻辑，减少 CPU 占用
- **增强兼容性**：确保在各 Python 版本和操作系统上正常运行
- **改进 MQTT 订阅**：添加通配符订阅，确保捕获所有相关数据
- **用户体验优化**：添加数据状态显示和断线检测
