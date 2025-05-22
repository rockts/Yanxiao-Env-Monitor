#!/bin/bash
# 智慧校园环境监测系统 - 最终空文件清理脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统 - 最终空文件清理   ${NC}"
echo -e "${BLUE}===============================================${NC}"

# 删除空日志文件
echo -e "${YELLOW}[步骤 1]${NC} 删除空日志文件..."
find ../logs -name "*.log" -size 0 -print -delete
find ./logs -name "*.log" -size 0 -print -delete
find ./src/logs -name "*.log" -size 0 -print -delete
echo "  - 已删除空日志文件"

# 清理空的文档文件
echo -e "${YELLOW}[步骤 2]${NC} 清理空文档文件..."
find ./docs -name "*.md" -size 0 -print -delete
find ./archive -name "*.md" -size 0 -print -delete
echo "  - 已删除空的文档文件"

# 清理空的脚本文件
echo -e "${YELLOW}[步骤 3]${NC} 清理空脚本文件..."
find ./scripts -name "*.sh" -size 0 -print -delete
echo "  - 已删除空的脚本文件"

# 修复目录结构
echo -e "${YELLOW}[步骤 4]${NC} 修复目录结构..."
# 确保脚本目录结构正确
mkdir -p ./scripts/utils

# 确认clean_data.command是否存在，如果存在则复制内容到script/clean_data.sh
if [ -f "../clean_data.command" ]; then
    echo "  - 发现clean_data.command，复制到scripts/clean_data.sh..."
    cp ../clean_data.command ./clean_data.sh
    chmod +x ./clean_data.sh
fi

# 确保所有目录都有README.md文件
for dir in ./utils ./scripts ./config ./data; do
    if [ ! -f "$dir/README.md" ]; then
        echo "# $(basename $dir) 目录" > "$dir/README.md"
        echo "" >> "$dir/README.md"
        echo "此目录用于存储$(basename $dir)相关文件。" >> "$dir/README.md"
        echo "" >> "$dir/README.md"
        echo "更新日期: $(date '+%Y-%m-%d')" >> "$dir/README.md"
        echo "  - 已创建 $dir/README.md"
    fi
done

echo -e "${GREEN}[完成]${NC} 最终清理已完成！项目结构已最终整理。"