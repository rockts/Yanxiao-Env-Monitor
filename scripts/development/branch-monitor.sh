#!/bin/bash

# 分支管理监控脚本
# 定期检查分支状态并生成报告

LOG_DIR="/tmp/branch-monitor"
REPORT_FILE="$LOG_DIR/branch-report-$(date +%Y%m%d_%H%M%S).md"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 开始分支监控检查..."

# 生成报告头部
cat > "$REPORT_FILE" << EOF
# 分支监控报告

**生成时间**: $(date)  
**检查类型**: 自动监控  

## 📊 分支状态概览

EOF

# 获取远程信息
git fetch origin &>/dev/null

# 当前分支信息
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $current_branch" >> "$REPORT_FILE"

# 工作区状态
if [ -n "$(git status --porcelain)" ]; then
    echo "工作区状态: ⚠️ 有未提交更改" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "### 未提交的文件" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    git status --short >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "工作区状态: ✅ 干净" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 分支同步状态
echo "## 🔄 分支同步状态" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 检查dev和master的差异
if git show-ref --verify --quiet refs/remotes/origin/dev && git show-ref --verify --quiet refs/remotes/origin/master; then
    dev_ahead=$(git rev-list --count origin/master..origin/dev 2>/dev/null || echo "0")
    dev_behind=$(git rev-list --count origin/dev..origin/master 2>/dev/null || echo "0")
    
    echo "- Dev分支领先Master: **$dev_ahead** 个提交" >> "$REPORT_FILE"
    echo "- Dev分支落后Master: **$dev_behind** 个提交" >> "$REPORT_FILE"
    
    # 状态判断
    if [ "$dev_behind" -gt 5 ]; then
        echo "- ⚠️ **警告**: Dev分支明显落后，建议同步" >> "$REPORT_FILE"
    elif [ "$dev_ahead" -gt 20 ]; then
        echo "- ⚠️ **警告**: Dev分支领先过多，建议发布" >> "$REPORT_FILE"
    else
        echo "- ✅ **状态**: 分支同步状态正常" >> "$REPORT_FILE"
    fi
else
    echo "- ❌ **错误**: 无法获取远程分支信息" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 最近提交历史
echo "## 📝 最近提交记录" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "### Dev分支最近5次提交" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
git log origin/dev --oneline -5 2>/dev/null >> "$REPORT_FILE" || echo "无法获取dev分支日志" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "### Master分支最近5次提交" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
git log origin/master --oneline -5 2>/dev/null >> "$REPORT_FILE" || echo "无法获取master分支日志" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 分支策略合规性检查
echo "## 🛡️ 分支策略合规性" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 检查是否有直接推送到master的提交
recent_master_commits=$(git log origin/master --since="1 day ago" --pretty=format:"%h %s" 2>/dev/null)
if [ -n "$recent_master_commits" ]; then
    echo "### 最近24小时Master分支提交" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$recent_master_commits" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "⚠️ **注意**: 检查是否遵循了发布流程" >> "$REPORT_FILE"
else
    echo "✅ 最近24小时Master分支无新提交" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 文件大小检查
echo "## 📏 仓库健康检查" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 检查大文件
large_files=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./env/*" 2>/dev/null | head -10)
if [ -n "$large_files" ]; then
    echo "### 大文件 (>1MB)" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$large_files" | xargs -I {} du -h {} >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "⚠️ **建议**: 考虑使用Git LFS管理大文件" >> "$REPORT_FILE"
else
    echo "✅ 未发现大文件" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 检查敏感文件
echo "### 敏感信息检查" >> "$REPORT_FILE"
sensitive_patterns="password|secret|token|api_key|private_key"
sensitive_files=$(grep -r -l -i "$sensitive_patterns" --include="*.py" --include="*.js" --include="*.json" --exclude-dir=".git" --exclude-dir="env" . 2>/dev/null | head -5)

if [ -n "$sensitive_files" ]; then
    echo "⚠️ **警告**: 发现可能包含敏感信息的文件" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$sensitive_files" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "✅ 未发现明显的敏感信息" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 生成建议
echo "## 💡 建议和行动项" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 基于检查结果生成建议
if [ "$dev_behind" -gt 5 ]; then
    echo "1. 🔄 **同步分支**: 运行 \`./scripts/branch-manager.sh sync\` 同步dev分支" >> "$REPORT_FILE"
fi

if [ "$dev_ahead" -gt 20 ]; then
    echo "2. 🚀 **发布建议**: Dev分支有大量新功能，考虑发布到Master" >> "$REPORT_FILE"
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "3. 💾 **提交更改**: 工作区有未提交的更改，请及时提交" >> "$REPORT_FILE"
fi

if [ -n "$large_files" ]; then
    echo "4. 📦 **文件管理**: 考虑清理或使用Git LFS管理大文件" >> "$REPORT_FILE"
fi

if [ -n "$sensitive_files" ]; then
    echo "5. 🔒 **安全检查**: 检查并移除敏感信息" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "*报告由分支监控脚本自动生成*" >> "$REPORT_FILE"

# 显示报告位置
echo -e "${GREEN}✅ 分支监控检查完成${NC}"
echo -e "${BLUE}📄 报告已保存至: $REPORT_FILE${NC}"

# 如果在终端运行，显示简要摘要
if [ -t 1 ]; then
    echo ""
    echo -e "${BLUE}=== 检查摘要 ===${NC}"
    echo -e "当前分支: ${YELLOW}$current_branch${NC}"
    
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "工作区状态: ${YELLOW}有未提交更改${NC}"
    else
        echo -e "工作区状态: ${GREEN}干净${NC}"
    fi
    
    if [ "$dev_behind" -gt 5 ]; then
        echo -e "分支状态: ${YELLOW}需要同步${NC}"
    else
        echo -e "分支状态: ${GREEN}正常${NC}"
    fi
fi

# 可选：发送报告到指定位置
if [ "$1" = "--save-to-docs" ]; then
    cp "$REPORT_FILE" "./docs/branch-monitor-$(date +%Y%m%d).md"
    echo -e "${GREEN}📋 报告已复制到docs目录${NC}"
fi
