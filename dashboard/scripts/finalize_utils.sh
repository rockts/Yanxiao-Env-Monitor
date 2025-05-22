#!/bin/bash
# 智慧校园环境监测系统 - 工具目录清理脚本
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
echo -e "${GREEN}   烟铺小学智慧校园环境监测系统 - 工具目录最终清理   ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 删除src/utils中的原始文件（因为它们已经被移动到整合目录）
echo -e "${YELLOW}[步骤 1]${NC} 清理src/utils原始文件..."
if [ -f "src/utils/simple_mqtt_broker.py" ]; then
  rm -f src/utils/simple_mqtt_broker.py
  echo "  - 已删除 src/utils/simple_mqtt_broker.py"
fi

if [ -f "src/utils/tkinter_test.py" ]; then
  rm -f src/utils/tkinter_test.py
  echo "  - 已删除 src/utils/tkinter_test.py"
fi

# 在src/utils中添加重定向README.md
if [ -d "src/utils" ]; then
  cat > src/utils/README.md << EOF
# 源代码工具目录

此目录下的工具已被移动到项目根目录的utils目录中进行统一管理。

请使用 \`/dashboard/utils\` 目录下的工具。

更新日期: 2025-05-22
EOF
  echo "  - 已在src/utils中添加重定向README.md"
fi

# 删除根目录中多余的文件
echo -e "${YELLOW}[步骤 2]${NC} 删除utils根目录中多余的文件..."
# 删除冗余的clean_data.command
if [ -f "utils/clean_data.command" ]; then
  rm -f utils/clean_data.command
  echo "  - 已删除冗余的 utils/clean_data.command"
fi

# 为项目结构文档添加utils目录说明
echo -e "${YELLOW}[步骤 3]${NC} 更新项目结构文档..."
if [ -f "docs/PROJECT_STRUCTURE.md" ]; then
  # 使用sed为utils添加子目录说明
  sed -i '' 's|└── utils/                          # 工具目录|└── utils/                          # 工具目录\n    ├── python/                     # Python工具脚本\n    ├── scripts/                    # Shell脚本工具\n    ├── mqtt/                       # MQTT工具和模拟器\n    └── testing/                    # 测试和界面工具|g' docs/PROJECT_STRUCTURE.md
  echo "  - 已更新项目结构文档"
fi

echo -e "${GREEN}[完成]${NC} 工具目录最终清理完毕！"
echo "所有工具文件现在都统一整理在dashboard/utils目录下。"
