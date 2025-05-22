# 智慧校园环境监测系统 - 项目结构说明

本文档描述了智慧校园环境监测系统的文件和目录结构。

## 项目结构

```
dashboard/
├── dashboard.py                    # dashboard.py (符号链接指向full_dashboard_new.py)
├── full_dashboard_new.py           # 主仪表盘完整实现
├── simple_working_dashboard.py     # 简化版仪表盘实现
├── README.md                       # 项目说明文档
├── requirements.txt                # Python依赖包列表
├── .env                            # 环境变量配置文件
│
├── clean_data.command              # 数据清理快捷脚本
├── run_full_dashboard.command      # 完整仪表盘启动脚本
├── simple_working_dashboard.command # 简化版仪表盘启动脚本
├── smart_launcher.command          # 智能启动器脚本
│
├── archive/                        # 归档文件目录
│   ├── cn_files/                   # 中文命名文件存档
│   ├── empty_files/                # 空文件存档
│   ├── old_backups/                # 旧备份存档
│   ├── old_versions/               # 旧版本存档
│   └── test_scripts/               # 测试脚本存档
│
├── backup/                         # 备份文件目录
│   └── 20250522/                   # 按日期组织的备份
│
├── config/                         # 配置文件目录
│   ├── config.json                 # 当前配置文件
│   ├── default_config.json         # 默认配置文件
│   ├── python_config.env           # Python环境配置
│   └── backup/                     # 配置备份目录
│
├── data/                           # 数据文件目录
│   └── sensor_logs/                # 传感器日志数据
│
├── docs/                           # 文档目录
│   └── archive/                    # 归档文档
│
├── logs/                           # 日志文件目录
│
├── scripts/                        # 脚本文件目录
│   ├── clean_data.sh               # 数据清理脚本
│   ├── final_cleanup.sh            # 最终清理脚本
│   ├── organize_scripts.sh         # 脚本组织工具
│   ├── maintenance/                # 维护脚本目录
│   │   ├── advanced_cleanup.sh     # 高级清理脚本
│   │   ├── cleanup_redundant_files.sh # 冗余文件清理
│   │   └── cleanup_src.sh         # 源代码清理脚本
│   └── utils/                      # 工具脚本目录
│
├── src/                            # 源代码目录
│   ├── alert_manager.py            # 告警管理模块
│   ├── config_loader.py            # 配置加载模块
│   ├── config_manager.py           # 配置管理模块
│   ├── data_cleaner.py             # 数据清理模块
│   ├── data_logger.py              # 数据记录模块
│   ├── log_manager.py              # 日志管理模块
│   ├── mqtt_bridge_service.py      # MQTT桥接服务
│   ├── mqtt_relay_service.py       # MQTT中继服务
│   ├── simple_dashboard.py         # 简单仪表盘实现
│   ├── updates.py                  # 更新管理模块
│   ├── archive/                    # 源代码归档
│   ├── backup/                     # 源代码备份
│   ├── config/                     # 源代码配置
│   ├── core/                       # 核心功能模块
│   ├── data/                       # 源代码数据
│   ├── logs/                       # 源代码日志
│   ├── models/                     # 数据模型
│   ├── services/                   # 服务模块
│   ├── simulators/                 # 模拟器模块
│   ├── ui/                         # 用户界面组件
│   └── utils/                      # 工具函数
│
└── utils/                          # 工具目录
    ├── mqtt/                       # MQTT工具和模拟器
    │   └── simple_mqtt_broker.py   # 简易MQTT代理模拟器
    ├── python/                     # Python工具脚本
    │   └── clean_data.py           # 数据清理Python工具
    ├── scripts/                    # Shell脚本工具
    │   └── clean_empty_files.sh    # 空文件清理脚本
    └── testing/                    # 测试和界面工具
        └── tkinter_test.py         # Tkinter界面测试工具
```

## 主要文件说明

- **dashboard.py**: 主仪表盘入口点，实际是 full_dashboard_new.py 的符号链接
- **full_dashboard_new.py**: 完整版仪表盘的最新实现
- **simple_working_dashboard.py**: 简化版仪表盘，用于低配置环境或快速启动

## 命令文件说明

- **clean_data.command**: 用于清理和整理数据文件
- **run_full_dashboard.command**: 启动完整版仪表盘
- **simple_working_dashboard.command**: 启动简化版仪表盘
- **smart_launcher.command**: 智能启动器，根据系统环境选择适合的版本启动

## 目录说明

- **archive/**: 存储不再使用的文件，但可能有历史参考价值
- **backup/**: 重要文件的备份
- **config/**: 系统配置文件
- **data/**: 数据文件，包括传感器数据
- **docs/**: 项目文档
- **logs/**: 运行日志
- **scripts/**: 维护和辅助脚本
- **src/**: 源代码
- **utils/**: 通用工具

## 更新日期

最后更新: 2025 年 5 月 22 日
