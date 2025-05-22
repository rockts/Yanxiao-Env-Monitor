#!/usr/bin/env bash
# 智慧校园环境监测系统 - 文件整理脚本
# 创建于 2025年5月22日

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 文件整理     ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 设置目录
DASHBOARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DASHBOARD_DIR"

# 创建必要的目录结构
echo -e "${BLUE}[信息]${NC} 创建目录结构..."
mkdir -p archive/old_versions
mkdir -p archive/test_scripts
mkdir -p backup/$(date +"%Y%m%d")
mkdir -p config
mkdir -p data/sensor_logs
mkdir -p docs
mkdir -p logs
mkdir -p src
mkdir -p utils

# 保留的核心文件列表
CORE_FILES=(
    "full_dashboard_new.py"
    "run_full_dashboard.command"
    "simple_working_dashboard.py"
    "simple_working_dashboard.command"
    "requirements.txt"
    "README.md"
    "start_dashboard.command"
)

# 备份当前的所有文件
echo -e "${BLUE}[信息]${NC} 备份当前文件..."
for file in *.py *.command *.sh *.md; do
    if [ -f "$file" ]; then
        cp "$file" "backup/$(date +"%Y%m%d")/" 2>/dev/null
    fi
done

# 移动废弃的核心文件到archive/old_versions
echo -e "${BLUE}[信息]${NC} 移动废弃的核心文件..."
for file in 真完整版启动.* 原始完整版启动.* 完整版仪表盘.py 快速启动.* 修复版仪表盘.* 修复版启动.py; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> archive/old_versions/"
        mv "$file" "archive/old_versions/" 2>/dev/null
    fi
done

# 移动测试和临时脚本到archive/test_scripts
echo -e "${BLUE}[信息]${NC} 移动测试和临时文件..."
for file in test_*.* temp_*.* *_test.* debug_*.* run_with_python3.* cleanup_dashboard.py; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> archive/test_scripts/"
        mv "$file" "archive/test_scripts/" 2>/dev/null
    fi
done

# 移动中文命名文件到archive
echo -e "${BLUE}[信息]${NC} 移动中文命名文件..."
for file in 超级简单版*.* 使用说明.* 智慧校园监测系统.* 仪表盘诊断.* 一键启动.*; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> archive/"
        mv "$file" "archive/" 2>/dev/null
    fi
done

# 移动文档到docs目录
echo -e "${BLUE}[信息]${NC} 整理文档文件..."
for file in *_SUMMARY.md *_REPORT.md *_GUIDE.md 修复报告.md; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> docs/"
        mv "$file" "docs/" 2>/dev/null
    fi
done

# 移动日志文件
echo -e "${BLUE}[信息]${NC} 移动日志文件..."
for file in *.log; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> logs/"
        mv "$file" "logs/" 2>/dev/null
    fi
done

# 移动实用工具脚本到utils
echo -e "${BLUE}[信息]${NC} 整理实用工具脚本..."
for file in clean_data.* fix_config.* launch*.py; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} $file -> utils/"
        mv "$file" "utils/" 2>/dev/null
    fi
done

# 确保核心文件保留在主目录
echo -e "${BLUE}[信息]${NC} 确保核心文件在主目录..."
for file in "${CORE_FILES[@]}"; do
    if [ -f "archive/$file" ]; then
        echo -e "${GREEN}[恢复]${NC} archive/$file -> ./"
        cp "archive/$file" "./" 2>/dev/null
    fi
    if [ -f "archive/old_versions/$file" ]; then
        echo -e "${GREEN}[恢复]${NC} archive/old_versions/$file -> ./"
        cp "archive/old_versions/$file" "./" 2>/dev/null
    fi
done

# 创建符号链接以便于访问
echo -e "${BLUE}[信息]${NC} 创建符号链接..."
if [ -f "full_dashboard_new.py" ]; then
    ln -sf "full_dashboard_new.py" "dashboard.py" 2>/dev/null
    echo -e "${GREEN}[链接]${NC} full_dashboard_new.py -> dashboard.py"
fi

# 设置文件权限
echo -e "${BLUE}[信息]${NC} 设置文件权限..."
chmod +x *.command *.sh 2>/dev/null
chmod +x utils/*.command utils/*.sh 2>/dev/null

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     文件整理完成!     ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}[信息]${NC} 核心文件保留在主目录"
echo -e "${YELLOW}[信息]${NC} 废弃的文件已移动到archive目录"
echo -e "${YELLOW}[信息]${NC} 备份已保存在backup/$(date +"%Y%m%d")目录"
echo -e "${YELLOW}[信息]${NC} 可运行 ./dashboard.py 或 ./run_full_dashboard.command 启动系统"
echo -e "${BLUE}=======================================================${NC}"