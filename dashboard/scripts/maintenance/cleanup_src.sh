#!/bin/bash
# 源代码目录清理脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[开始清理] 整理src目录...${NC}"

# 删除备份文件
echo -e "${GREEN}[步骤 1] 删除备份文件${NC}"
find . -name "*.bak" -type f -print -delete
find . -name "*.new" -type f -print -delete
find . -name "*.tmp" -type f -print -delete

# 创建备份目录
mkdir -p backup
mkdir -p archive/test

# 移动测试文件
echo -e "${GREEN}[步骤 2] 整理测试文件${NC}"
mv tkinter_test.py archive/test/
mv simple_mqtt_broker.py utils/
touch utils/__init__.py

# 整理旧的主文件
echo -e "${GREEN}[步骤 3] 整理旧的主文件${NC}"
mv main.py backup/main.py.$(date +"%Y%m%d")
mv main_dashboard.py backup/main_dashboard.py.$(date +"%Y%m%d")

# 整理模拟器文件
echo -e "${GREEN}[步骤 4] 整理模拟器文件${NC}"
mkdir -p simulators 2>/dev/null
mv sensor_data_simulator.py simulators/
mv video_stream_simulator.py simulators/
touch simulators/__init__.py

# 创建必要的空目录
echo -e "${GREEN}[步骤 5] 创建必要的空目录${NC}"
mkdir -p logs 2>/dev/null
mkdir -p data 2>/dev/null
mkdir -p config 2>/dev/null

# 创建README文件
echo -e "${GREEN}[步骤 6] 创建README文件${NC}"
cat > README.md <<EOF
# 智慧校园环境监测系统 - 源代码目录

此目录包含智慧校园环境监测系统的核心源代码。

## 主要模块

- \`alert_manager.py\`: 警报管理器
- \`config_loader.py\`: 配置加载器
- \`data_cleaner.py\`: 数据清理工具
- \`data_logger.py\`: 数据记录器
- \`core/\`: 核心功能模块
- \`models/\`: 数据模型定义
- \`services/\`: 服务组件
- \`simulators/\`: 数据模拟器
- \`ui/\`: 用户界面组件
- \`utils/\`: 工具函数

更新日期: 2025-05-22
EOF

echo -e "${YELLOW}[清理完成] src目录已整理${NC}"
