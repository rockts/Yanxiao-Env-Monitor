#!/bin/bash
# 智慧校园环境监测系统 - 进阶清理脚本
# 删除空文件和冗余文件

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[开始进阶清理] 删除空文件和冗余文件...${NC}"

# 删除空文件
echo -e "${GREEN}[步骤 1] 删除空白Python文件${NC}"
find . -type f -name "*.py" -size 0 -print -exec rm -f {} \;

# 删除空的命令文件
echo -e "${GREEN}[步骤 2] 删除空白命令文件${NC}"
find . -type f -name "*.command" -size 0 -print -exec rm -f {} \;

# 删除多余的文档文件
echo -e "${GREEN}[步骤 3] 整理文档文件${NC}"
mkdir -p docs/archive
mv CLEANUP_SUMMARY.md REFACTOR_SUMMARY.md SOLUTION_REPORT.md STARTUP_GUIDE.md docs/
rm -f 使用说明.md 修复报告.md 超级简单版说明.md
echo "  - 文档已移至docs目录"

# 保留核心启动脚本，删除其他重复脚本
echo -e "${GREEN}[步骤 4] 整理启动脚本${NC}"
rm -f run_simple_dashboard.py run_full_dashboard.py run_dashboard_macos.sh
rm -f start.sh start_dashboard.command smart_start.command smart_dashboard.command
rm -f 完整版启动.command 修复版仪表盘.command 快速启动.command
echo "  - 已清理重复启动脚本，保留核心脚本"

# 整理文档目录
echo -e "${GREEN}[步骤 5] 整理文档和备份目录${NC}"
rm -f docs/*.bak docs/*.tmp 
# 删除备份目录中的空文件
find ./backup -type f -size 0 -delete
# 删除多余的配置文件
mkdir -p config/backup
mv config/config_new.json config/local_config.json config/backup/
echo "  - 已清理文档和备份目录"

# 将无用的工具脚本移到scripts目录
echo -e "${GREEN}[步骤 6] 整理工具脚本${NC}"
mkdir -p scripts/utils
mv organize_files.sh cleanup.sh scripts/utils/
rm -f 修复版启动.py 配置文件优化.py
echo "  - 已将工具脚本整理至scripts/utils目录"

# 更新README文件
echo -e "${GREEN}[步骤 7] 更新README${NC}"
cat > README.md <<EOF
# 智慧校园环境监测系统

这是烟铺小学智慧校园环境监测系统，通过各种传感器收集并展示校园环境数据。

## 快速启动

1. **完整版**: 运行 \`run_full_dashboard.command\` 启动带有全部功能的仪表盘
2. **简化版**: 运行 \`simple_working_dashboard.command\` 启动轻量级仪表盘
3. **智能启动器**: 运行 \`smart_launcher.command\` 选择要启动的功能

## 目录结构

- \`dashboard.py\`: 主仪表盘程序(符号链接到full_dashboard_new.py)
- \`full_dashboard_new.py\`: 完整版仪表盘源代码
- \`simple_working_dashboard.py\`: 简化版仪表盘源代码
- \`config/\`: 配置文件目录
- \`data/\`: 数据存储目录
- \`docs/\`: 文档目录
- \`src/\`: 源代码目录
- \`scripts/\`: 实用脚本目录

## 数据维护

- 运行 \`clean_data.command\` 清理旧数据

更新日期: 2025-05-22
EOF
echo "  - 已更新README.md"

echo -e "${YELLOW}[清理完成] 项目结构已进一步简化${NC}"
