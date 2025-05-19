# 智慧校园仪表盘配置文件说明

## 配置文件结构

`config.json` 文件包含以下配置项：

```json
{
 "siot_server_http": "http://192.168.1.129:8080", // SIoT服务器HTTP地址
 "siot_username": "siot", // SIoT用户名
 "siot_password": "dfrobot", // SIoT密码
 "mqtt_broker_host": "127.0.0.1", // MQTT代理主机地址
 "mqtt_broker_port": 1883, // MQTT代理端口
 "mqtt_client_id": "smart_campus_dashboard_client_001", // MQTT客户端ID
 "mqtt_camera_topic": "sc/camera/stream", // 摄像头数据主题
 "mqtt_weather_topic": "sc/weather/data", // 天气数据主题
 "update_interval": 15, // 界面更新间隔(秒)
 "chart_history_maxlen": 20, // 图表历史数据点数量
 "weather_fetch_interval": 1800 // 天气数据获取间隔(秒)
}
```

## 说明

1. **MQTT 配置**

   - `mqtt_broker_host`: MQTT 服务器的 IP 地址，默认为本地回环地址(127.0.0.1)
   - `mqtt_broker_port`: MQTT 服务器端口，标准端口为 1883
   - `mqtt_client_id`: 客户端标识符，必须唯一

2. **SIoT 配置**

   - `siot_server_http`: SIoT 服务器 HTTP 地址
   - `siot_username`: SIoT 用户名
   - `siot_password`: SIoT 密码

3. **主题配置**
   - `mqtt_camera_topic`: 接收摄像头数据的 MQTT 主题
   - `mqtt_weather_topic`: 接收天气数据的 MQTT 主题
4. **性能配置**
   - `update_interval`: UI 更新间隔，单位为秒
   - `chart_history_maxlen`: 图表显示的历史数据点数量
   - `weather_fetch_interval`: 天气 API 数据获取间隔，单位为秒

## 修改建议

1. 在生产环境中，应将`mqtt_broker_host`修改为实际 MQTT 服务器的 IP 地址
2. 如果需要更平滑的图表显示效果，可以增加`chart_history_maxlen`的值
3. 根据实际网络状况调整`update_interval`，网络不稳定时可适当增大此值
