#!/usr/bin/env bash
# 智慧校园环境监测系统 - 清理空文件和无用文件

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
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 清理空文件     ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 创建临时存放目录
mkdir -p archive/empty_files

# 查找并移动空文件
empty_count=0
for file in *.py *.command *.sh; do
    if [ -f "$file" ] && [ ! -s "$file" ] && [ "$file" != "dashboard.py" ]; then
        echo -e "${YELLOW}[移动]${NC} 空文件: $file -> archive/empty_files/"
        mv "$file" "archive/empty_files/" 2>/dev/null
        empty_count=$((empty_count+1))
    fi
done

# 移动其他中文命名文件
cn_count=0
for file in 配置文件优化.py 启动仪表盘.command 完整版启动.command 智慧校园启动器.py; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} 中文命名文件: $file -> archive/empty_files/"
        mv "$file" "archive/empty_files/" 2>/dev/null
        cn_count=$((cn_count+1))
    fi
done

# 移动非核心文件
other_count=0
for file in direct_run.py easy_launch.* easy_start.py fixed_dashboard.py mac_launch.sh minimal_dashboard.py pure_dashboard.py quick_fix.py quick_start.sh run_dashboard_macos.sh run_full_dashboard.py run_simple_dashboard.py run_simplified.* simplified_dashboard.py simplified_launcher.py smart_dashboard.command smart_launcher.py smart_start.command start.sh vscode_compat_run.py vscode_start.command cleanup.sh; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}[移动]${NC} 非核心文件: $file -> archive/empty_files/"
        mv "$file" "archive/empty_files/" 2>/dev/null
        other_count=$((other_count+1))
    fi
done

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     清理完成!     ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}[信息]${NC} 已移动 $empty_count 个空文件"
echo -e "${YELLOW}[信息]${NC} 已移动 $cn_count 个中文命名文件"
echo -e "${YELLOW}[信息]${NC} 已移动 $other_count 个非核心文件"
echo -e "${BLUE}=======================================================${NC}"
