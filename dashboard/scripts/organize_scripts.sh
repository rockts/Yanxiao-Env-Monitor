#!/bin/bash
# 智慧校园环境监测系统 - 脚本文件最终整理脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统 - 脚本文件最终整理   ${NC}"
echo -e "${BLUE}===============================================${NC}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PARENT_DIR"

# 步骤1：移动根目录下的脚本文件到scripts目录
echo -e "${YELLOW}[步骤 1]${NC} 移动根目录下的脚本文件到scripts目录..."

if [ -f "advanced_cleanup.sh" ]; then
  echo "  - 移动 advanced_cleanup.sh 到 scripts/maintenance/"
  mkdir -p scripts/maintenance
  mv advanced_cleanup.sh scripts/maintenance/
fi

if [ -f "cleanup_redundant_files.sh" ]; then
  echo "  - 移动 cleanup_redundant_files.sh 到 scripts/maintenance/"
  mkdir -p scripts/maintenance
  mv cleanup_redundant_files.sh scripts/maintenance/
fi

# 步骤2：移动src目录下的脚本文件
echo -e "${YELLOW}[步骤 2]${NC} 移动src目录下的脚本文件..."

if [ -f "src/cleanup_src.sh" ]; then
  echo "  - 移动 src/cleanup_src.sh 到 scripts/maintenance/"
  mkdir -p scripts/maintenance
  cp src/cleanup_src.sh scripts/maintenance/
  rm src/cleanup_src.sh
fi

# 步骤3：确保所有脚本具有可执行权限
echo -e "${YELLOW}[步骤 3]${NC} 设置脚本可执行权限..."
chmod +x scripts/*.sh
chmod +x scripts/maintenance/*.sh
chmod +x scripts/utils/*.sh 2>/dev/null || true  # 如果没有utils目录下的脚本，忽略错误

# 步骤4：整理command文件
echo -e "${YELLOW}[步骤 4]${NC} 整理command文件..."
# 确保clean_data.command链接到scripts/clean_data.sh
if [ -f "clean_data.command" ] && [ -f "scripts/clean_data.sh" ]; then
  rm -f clean_data.command
  ln -s scripts/clean_data.sh clean_data.command
  echo "  - 更新了 clean_data.command 链接"
fi

# 步骤5：创建脚本目录的README
echo -e "${YELLOW}[步骤 5]${NC} 更新脚本目录README..."
cat > scripts/README.md << EOF
# 脚本目录

此目录包含智慧校园环境监测系统运行所需的各类脚本文件。

## 目录结构

- **clean_data.sh** - 数据清理脚本，用于处理和整理传感器数据
- **final_cleanup.sh** - 最终空文件清理脚本，用于系统部署前的整理工作
- **maintenance/** - 维护和清理脚本目录，包含高级清理和冗余文件处理脚本
- **utils/** - 实用工具脚本目录，包含各种辅助功能脚本

## 使用方法

大多数脚本可以直接在终端中执行：

```bash
./scripts/脚本名.sh
```

针对数据清理，也可以使用项目根目录下的`clean_data.command`快捷方式。
EOF

# 步骤6：创建维护脚本目录的README
mkdir -p scripts/maintenance
cat > scripts/maintenance/README.md << EOF
# 维护脚本目录

此目录包含智慧校园环境监测系统的维护和清理脚本。

## 可用脚本

- **advanced_cleanup.sh** - 进阶清理脚本，用于删除空文件和冗余文件
- **cleanup_redundant_files.sh** - 清理多余文件脚本，用于删除重复和无用文件
- **cleanup_src.sh** - 源代码目录清理脚本，用于整理src目录文件

这些脚本主要用于系统维护和整理，通常不需要日常运行。
EOF

echo -e "${GREEN}[完成]${NC} 脚本文件整理完毕！"
echo "所有shell脚本已移动到合适的位置并设置了可执行权限。"
