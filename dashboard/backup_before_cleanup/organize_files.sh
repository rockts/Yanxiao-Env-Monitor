#!/bin/bash
# 智慧校园环境监测系统 - 文件整理脚本 (完善版)
# 此脚本将进一步整理项目目录

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
echo -e "${GREEN}   智慧校园环境监测系统 - 文件整理脚本 (完善版)  ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# 1. 创建临时存档目录
echo -e "${YELLOW}步骤1: 创建临时存档目录...${NC}"
mkdir -p ./old_files

# 2. 移动所有.command文件到scripts/unix目录
echo -e "${YELLOW}步骤2: 移动所有.command文件到scripts/unix目录...${NC}"
find . -maxdepth 1 -name "*.command" -exec cp {} ./scripts/unix/ \; -exec mv {} ./old_files/ \;
echo -e "${GREEN}✓ 已移动.command文件${NC}"

# 3. 移动所有.bat文件到scripts/windows目录
echo -e "${YELLOW}步骤3: 移动所有.bat文件到scripts/windows目录...${NC}"
find . -maxdepth 1 -name "*.bat" -exec cp {} ./scripts/windows/ \; -exec mv {} ./old_files/ \;
echo -e "${GREEN}✓ 已移动.bat文件${NC}"

# 4. 移动所有.sh文件到scripts/unix目录
echo -e "${YELLOW}步骤4: 移动所有.sh文件到scripts/unix目录...${NC}"
find . -maxdepth 1 -name "*.sh" ! -name "organize_files.sh" -exec cp {} ./scripts/unix/ \; -exec mv {} ./old_files/ \;
echo -e "${GREEN}✓ 已移动.sh文件${NC}"

# 5. 移动Python备份文件到backup目录
echo -e "${YELLOW}步骤5: 移动Python备份文件到backup目录...${NC}"
for file in main_all_fixed*.py main.py.* *_test.py send_*.py start_*.py; do
    if [ -f "$file" ]; then
        mv "$file" ./backup/ 2>/dev/null
    fi
done
echo -e "${GREEN}✓ 已移动Python备份文件${NC}"

# 6. 移动配置文件到config目录
echo -e "${YELLOW}步骤6: 确保所有配置文件在config目录...${NC}"
if [ -f "config.json" ]; then
    cp config.json ./config/ 2>/dev/null
    mv config.json ./old_files/ 2>/dev/null
fi
echo -e "${GREEN}✓ 已处理配置文件${NC}"

# 7. 更新README
echo -e "${YELLOW}步骤7: 更新README文件...${NC}"
if [ -f "README_NEW.md" ]; then
    cp README.md ./old_files/README.md.old 2>/dev/null
    cp README_NEW.md ./README.md 2>/dev/null
    mv README_NEW.md ./old_files/ 2>/dev/null
fi
echo -e "${GREEN}✓ 已更新README${NC}"

echo
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   文件整理完成! 旧文件已移动到old_files目录   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo -e "${YELLOW}注意: 请检查old_files目录确保没有遗漏重要文件${NC}"
echo -e "${YELLOW}      如果确认无误，可以删除old_files目录${NC}"
echo
