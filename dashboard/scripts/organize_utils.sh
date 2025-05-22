#!/bin/bash
# 智慧校园环境监测系统 - 整理工具目录脚本
# 2025-05-22

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 整合工具目录   ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 创建utils子目录结构
echo -e "${YELLOW}[步骤 1]${NC} 创建工具目录结构..."
mkdir -p utils/scripts
mkdir -p utils/python
mkdir -p utils/mqtt
mkdir -p utils/testing

# 移动utils目录下的文件
echo -e "${YELLOW}[步骤 2]${NC} 整理dashboard/utils下的文件..."
if [ -f "utils/clean_data.py" ]; then
  mv utils/clean_data.py utils/python/
  echo "  - 已移动 clean_data.py 到 utils/python/"
fi

if [ -f "utils/clean_empty_files.sh" ]; then
  mv utils/clean_empty_files.sh utils/scripts/
  echo "  - 已移动 clean_empty_files.sh 到 utils/scripts/"
fi

if [ -f "utils/clean_data.command" ]; then
  rm -f utils/clean_data.command
  echo "  - 已删除冗余的 clean_data.command"
fi

# 移动src/utils下的文件到主utils目录
echo -e "${YELLOW}[步骤 3]${NC} 整合src/utils下的文件..."
if [ -f "src/utils/simple_mqtt_broker.py" ]; then
  mv src/utils/simple_mqtt_broker.py utils/mqtt/
  echo "  - 已移动 simple_mqtt_broker.py 到 utils/mqtt/"
fi

if [ -f "src/utils/tkinter_test.py" ]; then
  mv src/utils/tkinter_test.py utils/testing/
  echo "  - 已移动 tkinter_test.py 到 utils/testing/"
fi

# 创建README文件
echo -e "${YELLOW}[步骤 4]${NC} 创建README文件..."
cat > utils/README.md << EOF
# 工具目录

此目录包含智慧校园环境监测系统各种工具和实用程序。

## 目录结构

- **python/** - Python工具脚本，包括数据清理工具
- **scripts/** - 通用Shell脚本工具
- **mqtt/** - MQTT相关工具，包括模拟代理
- **testing/** - 测试工具和脚本

## 已整合工具

以下工具已从重复的utils目录整合到此处：

- **clean_data.py** - 数据清理Python工具
- **clean_empty_files.sh** - 空文件清理脚本
- **simple_mqtt_broker.py** - 简易MQTT代理模拟器
- **tkinter_test.py** - Tkinter界面测试工具

## 使用方法

大多数工具都可以直接在终端中运行，例如：

\`\`\`bash
# Python工具
python3 utils/python/clean_data.py

# Shell脚本
./utils/scripts/clean_empty_files.sh
\`\`\`

更新日期: 2025-05-22
EOF

# 创建子目录README文件
echo -e "${YELLOW}[步骤 5]${NC} 创建子目录README文件..."
mkdir -p utils/python utils/scripts utils/mqtt utils/testing

cat > utils/python/README.md << EOF
# Python工具目录

此目录包含项目使用的各种Python工具脚本。

## 可用工具

- **clean_data.py** - 数据清理Python工具，用于清理旧的传感器数据和日志
EOF

cat > utils/scripts/README.md << EOF
# 脚本工具目录

此目录包含各类Shell脚本工具。

## 可用工具

- **clean_empty_files.sh** - 用于删除项目中的空文件
EOF

cat > utils/mqtt/README.md << EOF
# MQTT工具目录

此目录包含与MQTT相关的工具和模拟器。

## 可用工具

- **simple_mqtt_broker.py** - 用于本地测试的简易MQTT代理模拟器
EOF

cat > utils/testing/README.md << EOF
# 测试工具目录

此目录包含用于测试界面和功能的工具。

## 可用工具

- **tkinter_test.py** - Tkinter界面测试工具
EOF

# 清理空的src/utils目录
echo -e "${YELLOW}[步骤 6]${NC} 清理空目录..."
if [ -d "src/utils" ]; then
  rmdir --ignore-fail-on-non-empty src/utils
  if [ $? -ne 0 ]; then
    echo -e "${RED}警告: src/utils目录非空，无法删除${NC}"
    echo "请手动检查src/utils中是否还有重要文件"
    mkdir -p src/utils/archive
    mv src/utils/* src/utils/archive/ 2>/dev/null
    echo "已将src/utils中的剩余文件移动到src/utils/archive/"
    echo -e "${YELLOW}请在确认文件无用后手动删除此目录${NC}"
  else
    echo "已删除空的src/utils目录"
  fi
fi

echo -e "${GREEN}[完成]${NC} 工具目录整理完毕！"
echo "所有工具已整合到统一的utils目录结构中。"
