#!/bin/bash
# 清理多余文件脚本
# 日期: 2025-05-22

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[开始清理] 正在删除多余和重复的文件...${NC}"

# 删除空文件
echo -e "${GREEN}[步骤 1] 删除空文件${NC}"
rm -f smart_launcher.py 智慧校园启动器.py
echo "  - 已删除空文件: smart_launcher.py 智慧校园启动器.py"

# 删除测试和临时文件
echo -e "${GREEN}[步骤 2] 删除测试和临时文件${NC}"
rm -f temp_run_dashboard.py test_fixes.command simple_test.py vscode_compat_run.py
echo "  - 已删除测试/临时文件"

# 删除重复的启动脚本(只保留主要的几个)
echo -e "${GREEN}[步骤 3] 删除重复的启动脚本${NC}"
rm -f easy_launch.command easy_start.py launch.py quick_start.sh mac_launch.sh
rm -f direct_run.py run_simplified.command run_simplified.py run_with_python3.command
rm -f vscode_start.command
rm -f 一键启动.command 原始完整版启动.command 原始完整版启动.py
rm -f 真完整版启动.command 真完整版启动.py
echo "  - 已删除重复的启动脚本"

# 删除重复的Python脚本
echo -e "${GREEN}[步骤 4] 删除重复的Python脚本${NC}"
rm -f quick_fix.py fix_config.py fixed_dashboard.py
rm -f launch_dashboard.py minimal_dashboard.py pure_dashboard.py
rm -f simplified_dashboard.py simplified_launcher.py easy_launch.py
echo "  - 已删除重复的Python脚本"

# 备份原有的backup_before_cleanup目录到archive，然后删除
echo -e "${GREEN}[步骤 5] 处理旧备份文件夹${NC}"
if [ -d "backup_before_cleanup" ]; then
  echo "  - 将backup_before_cleanup备份到archive目录"
  mkdir -p archive/old_backups
  tar -czf archive/old_backups/backup_before_cleanup_$(date +"%Y%m%d").tar.gz backup_before_cleanup
  echo "  - 删除backup_before_cleanup目录"
  rm -rf backup_before_cleanup
fi

# 最后，整理组织结构
echo -e "${GREEN}[步骤 6] 整理目录结构${NC}"
# 创建环境变量文件
if [ ! -f ".env" ]; then
  echo "# 智慧校园环境监测系统 环境配置" > .env
  echo "PYTHON_PATH=$(which python3)" >> .env
  echo "DASHBOARD_HOME=$(pwd)" >> .env
  echo "LOG_LEVEL=INFO" >> .env
  echo "  - 已创建.env环境配置文件"
fi

# 创建一个README
cat > README.md <<EOF
# 智慧校园环境监测系统

## 推荐使用方式
1. **完整版仪表盘**: 运行 \`run_full_dashboard.command\` 启动完整功能版本
2. **简化版仪表盘**: 运行 \`simple_working_dashboard.command\` 启动简化版本
3. **智能启动器**: 运行 \`smart_launcher.command\` 选择需要的功能

## 主要文件
- \`dashboard.py\`: 主仪表盘(指向full_dashboard_new.py的符号链接)
- \`full_dashboard_new.py\`: 完整版仪表盘源代码
- \`simple_working_dashboard.py\`: 简化版仪表盘源代码

## 目录结构
- \`config/\`: 配置文件目录
- \`data/\`: 数据存储目录
- \`logs/\`: 日志文件目录
- \`src/\`: 源代码目录
- \`utils/\`: 实用工具脚本

更新日期: 2025-05-22
EOF
echo "  - 已更新README.md"

echo -e "${YELLOW}[清理完成] 系统文件已整理，保留了必要的核心文件${NC}"
