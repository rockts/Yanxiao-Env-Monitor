# 智慧校园环境监测系统 - 重构检查清单

## 重构完成项目结构

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
│   │   ├── __init__.py
│   │   ├── config_manager.py    # 配置管理器
│   │   └── log_manager.py       # 日志管理器
│   ├── services/         # 服务组件
│   │   ├── __init__.py
│   │   ├── mqtt_bridge_service.py  # MQTT桥接服务
│   │   ├── mqtt_relay_service.py   # MQTT中继服务
│   │   └── simple_mqtt_broker.py   # 简易MQTT代理
│   ├── simulators/       # 模拟器组件
│   │   ├── __init__.py
│   │   ├── sensor_data_simulator.py  # 传感器数据模拟器
│   │   └── video_stream_simulator.py # 视频流模拟器
│   ├── ui/               # 用户界面组件
│   │   ├── __init__.py
│   │   ├── dashboard.py          # 主仪表盘界面
│   │   └── simple_dashboard.py   # 简化版仪表盘界面
│   ├── utils/            # 工具类组件
│   │   └── __init__.py
│   └── main_dashboard.py # 主入口文件
├── backup/               # 备份文件目录（仅供参考，不用于生产）
├── launch.py             # 统一启动器
├── README.md             # 项目说明文件
└── README_NEW.md         # 更新的项目说明文件
```

## 已完成事项

- [x] 创建新的目录结构
- [x] 添加所需的**init**.py 文件
- [x] 将核心文件移动到对应的目录
- [x] 将服务文件移动到 services 目录
- [x] 将模拟器文件移动到 simulators 目录
- [x] 将 UI 相关文件移动到 ui 目录
- [x] 将脚本文件整理到 scripts 目录
- [x] 创建统一的启动器(launch.py)
- [x] 创建新的项目说明文档(README_NEW.md)

## 待完成事项

- [ ] 更新所有 Python 文件中的导入语句，适应新的目录结构
- [ ] 创建完整的主仪表盘类(UI/dashboard.py)
- [ ] 更新配置管理器，使用正确的路径
- [ ] 更新日志管理器，使用正确的路径
- [ ] 测试各种启动方式
- [ ] 清理或归档不需要的文件
- [ ] 完善项目文档
- [ ] 更新根目录下的 main.py 作为简单的导入转发

## 手动重构步骤

1. 更新每个移动后的 Python 文件中的导入路径
2. 测试 launch.py 启动系统的不同模式
3. 测试 scripts 目录下的启动脚本
4. 确保配置文件路径更新
5. 验证所有功能的运行状况
6. 清理不再需要的旧文件
