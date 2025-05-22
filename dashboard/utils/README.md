# 工具目录

此目录包含智慧校园环境监测系统各种工具和实用程序。

## 目录结构

- **python/** - Python 工具脚本，包括数据清理工具
- **scripts/** - 通用 Shell 脚本工具
- **mqtt/** - MQTT 相关工具，包括模拟代理
- **testing/** - 测试工具和脚本

## 已整合工具

以下工具已从重复的 utils 目录整合到此处：

- **clean_data.py** - 数据清理 Python 工具
- **clean_empty_files.sh** - 空文件清理脚本
- **simple_mqtt_broker.py** - 简易 MQTT 代理模拟器
- **tkinter_test.py** - Tkinter 界面测试工具

## 使用方法

大多数工具都可以直接在终端中运行，例如：

```bash
# Python工具
python3 utils/python/clean_data.py

# Shell脚本
./utils/scripts/clean_empty_files.sh
```

更新日期: 2025-05-22
