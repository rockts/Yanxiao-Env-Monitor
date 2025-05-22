#!/bin/bash
# 智慧校园环境监测系统 - 文件清理脚本
# 此脚本用于清理项目中的冗余文件

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统 - 文件清理脚本   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# 1. 确保存在需要的目录
echo -e "${YELLOW}步骤1: 创建必要的目录...${NC}"
mkdir -p ./backup
mkdir -p ./scripts/unix
mkdir -p ./scripts/windows
mkdir -p ./old_files
echo -e "${GREEN}✓ 已创建必要目录${NC}"

# 2. 识别和列出冗余文件
echo -e "${YELLOW}步骤2: 识别冗余文件...${NC}"

# 定义冗余文件列表（这些是根据目录结构分析和重构汇总识别出的冗余文件）
redundant_files=(
  "direct_run.py"
  "main_all_fixed.py"
  "main_all_fixed_new.py"
  "main_all_fixed_optimized.py"
  "main.py.new"
  "simple_test.py"
  "simple_test_output.txt"
  "vscode_compat_run.py"
  "README_updated.md"
  "debug_complete.txt"
)

# 显示冗余文件列表
echo -e "${YELLOW}识别的冗余文件列表:${NC}"
for file in "${redundant_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "  - $file ${RED}(将移动到backup目录)${NC}"
  else
    echo -e "  - $file ${GREEN}(不存在)${NC}"
  fi
done

# 3. 移动冗余文件到backup目录
echo -e "${YELLOW}步骤3: 移动冗余文件到backup目录...${NC}"
for file in "${redundant_files[@]}"; do
  if [ -f "$file" ]; then
    mv "$file" ./backup/ 2>/dev/null
    echo -e "  ${GREEN}✓ 已移动: $file${NC}"
  fi
done

# 4. 运行文件组织脚本
echo -e "${YELLOW}步骤4: 运行文件组织脚本...${NC}"
if [ -f "./organize_files.sh" ]; then
  chmod +x ./organize_files.sh
  ./organize_files.sh
else
  echo -e "${RED}错误: 找不到organize_files.sh脚本${NC}"
fi

# 5. 清理旧的根目录Python文件
echo -e "${YELLOW}步骤5: 清理旧的根目录Python文件...${NC}"
old_python_files=(
  "mqtt_bridge.py"
  "mqtt_relay.py"
  "simple_mqtt_broker.py"
)

for file in "${old_python_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "  - 移动: $file 到 old_files/"
    mv "$file" ./old_files/ 2>/dev/null
  fi
done

# 6. 更新README (如果需要)
echo -e "${YELLOW}步骤6: 更新README文件...${NC}"
if [ -f "README_NEW.md" ] && [ -f "README.md" ]; then
  cp README.md ./old_files/README.md.old 2>/dev/null
  cp README_NEW.md ./README.md 2>/dev/null
  mv README_NEW.md ./old_files/ 2>/dev/null
  echo -e "${GREEN}✓ 已更新README${NC}"
else
  echo -e "${YELLOW}未找到新README文件，跳过更新${NC}"
fi

# 7. 清理临时文件和调试日志
echo -e "${YELLOW}步骤7: 清理临时文件和调试日志...${NC}"
find . -maxdepth 1 -name "*_started.txt" -exec mv {} ./old_files/ \;
find . -maxdepth 1 -name "*.log" -exec mv {} ./logs/ \;
find . -maxdepth 1 -name "*.tmp" -exec rm {} \;
echo -e "${GREEN}✓ 已清理临时文件${NC}"

# 8. 确保关键脚本有执行权限
echo -e "${YELLOW}步骤8: 设置关键脚本的执行权限...${NC}"
chmod +x ./launch.py
chmod +x ./scripts/unix/*.sh
chmod +x ./scripts/unix/*.command
echo -e "${GREEN}✓ 已设置执行权限${NC}"

echo
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   文件清理完成!   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo -e "${YELLOW}注意:${NC}"
echo -e "${YELLOW}1. 旧文件已移动到old_files和backup目录${NC}"
echo -e "${YELLOW}2. 如果所有功能正常，您可以安全删除这些目录${NC}"
echo -e "${YELLOW}3. 新的启动方式:${NC}"
echo -e "${YELLOW}   - ./launch.py [选项]${NC}"
echo -e "${YELLOW}   - python3 ./src/main_dashboard.py${NC}"
echo -e "${YELLOW}   - ./scripts/unix/start_dashboard.command${NC}"
echo