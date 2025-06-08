#!/bin/bash

# 设置分支管理相关的定时任务

echo "⏰ 设置分支管理定时任务..."

# 获取项目路径
PROJECT_PATH=$(pwd)
echo "项目路径: $PROJECT_PATH"

# 创建crontab条目
CRON_JOBS="
# 分支管理定时任务
# 每天早上9点检查分支状态
0 9 * * * cd $PROJECT_PATH && ./scripts/branch-monitor.sh --save-to-docs

# 每周一早上检查分支同步状态
0 9 * * 1 cd $PROJECT_PATH && ./scripts/branch-manager.sh status

# 每月1号清理旧的监控报告
0 0 1 * * find $PROJECT_PATH/docs -name 'branch-monitor-*.md' -mtime +30 -delete
"

# 备份现有的crontab
echo "📋 备份现有crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "没有现有的crontab条目"

# 检查是否已经存在相关任务
if crontab -l 2>/dev/null | grep -q "branch-monitor"; then
    echo "⚠️ 检测到已存在的分支监控任务"
    read -p "是否覆盖现有任务? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "❌ 取消设置定时任务"
        exit 0
    fi
    
    # 移除现有的分支管理相关任务
    crontab -l 2>/dev/null | grep -v "branch-monitor\|branch-manager" | crontab -
fi

# 添加新的定时任务
echo "📅 添加分支管理定时任务..."
(crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ 定时任务设置成功!"
    echo ""
    echo "📋 已设置的任务:"
    echo "- 每天9:00 AM: 分支状态监控"
    echo "- 每周一9:00 AM: 分支同步检查"
    echo "- 每月1号: 清理旧监控报告"
    echo ""
    echo "📝 查看当前crontab: crontab -l"
    echo "🗑️ 移除定时任务: crontab -r"
else
    echo "❌ 定时任务设置失败"
    exit 1
fi

# 创建日志目录
mkdir -p "$PROJECT_PATH/logs/cron"
echo "📁 创建cron日志目录: $PROJECT_PATH/logs/cron"

echo ""
echo "🎯 使用说明:"
echo "1. 监控报告将保存在 docs/ 目录"
echo "2. Cron日志可以重定向到 logs/cron/ 目录"
echo "3. 手动运行监控: ./scripts/branch-monitor.sh"
echo "4. 手动检查状态: ./scripts/branch-manager.sh status"
echo ""
echo "✅ 分支管理定时任务配置完成!"
