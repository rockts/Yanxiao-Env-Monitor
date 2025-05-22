# 项目重构与优化记录

## 修复事项

1. 在项目重构期间，主程序(`main.py`)的主函数入口点(`if __name__ == "__main__":`)和 Tkinter 主循环(`root.mainloop()`)被遗漏。已添加此关键部分，使仪表盘能够正常显示。

2. 修复了一个方法名称错误：将`reconnect_mqtt`方法引用修改为正确的`connect_mqtt`。

## 项目结构

新的项目结构组织如下：

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

## 启动方式

1. **基本启动**：

   ```bash
   ./start.command
   ```

   - 直接启动仪表盘主程序

2. **测试模式启动**：
   ```bash
   ./start_test.command
   ```
   - 启动 MQTT 代理服务器
   - 启动传感器测试数据发生器
   - 启动视频测试数据发生器
   - 启动仪表盘主程序

## 配置管理

通过`config/config.json`统一管理配置项，支持：

- MQTT 连接参数
- 传感器主题配置
- 天气 API 配置
- 界面更新间隔
- 图表历史数据量配置

## 视觉优化

- 增加视频显示区域尺寸：450x340
- 改进数据面板比例：3:3:7（左:中:右）
- 数值右对齐，提高美观度
