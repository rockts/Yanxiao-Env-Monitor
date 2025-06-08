# Scripts 目录结构说明

## 📂 目录组织

### 🔧 development/ - 开发工具

开发和分支管理相关的脚本工具：

- `branch-manager.sh` - 主分支管理工具（包含所有分支操作）
- `multi-remote-sync.sh` - 多远程仓库同步工具
- `branch-monitor.sh` - 分支状态监控
- `branch-management-test.sh` - 分支管理功能测试
- `setup-branch-cron.sh` - 分支定时任务设置
- `setup-branch-protection.sh` - 分支保护规则设置
- `setup-git-config.sh` - Git 配置脚本

### 🚀 production/ - 生产环境工具

生产环境监控和管理脚本：

- `monitor_manager.sh` - 监控系统管理器
- `health_monitor.sh` - 健康检查脚本
- `service_manager.sh` - 服务管理工具
- `auto_sync_daemon.sh` - 自动同步守护进程
- `git_sync_tool.sh` - Git 同步工具
- `sync_manager.sh` - 同步管理器
- `quick_deploy.sh` - 快速部署脚本
- `quick_sync.sh` - 快速同步脚本
- `log_rotation.sh` - 日志轮转管理
- `setup_cron.sh` - 定时任务设置
- `monitoring_deployment_summary.sh` - 监控部署摘要

### 📄 配置文件

- `sync_config.json` - 同步配置文件

## 🎯 使用指南

### 开发环境使用

```bash
# 分支管理
./scripts/development/branch-manager.sh status
./scripts/development/branch-manager.sh sync-all

# 多远程同步
./scripts/development/multi-remote-sync.sh
```

### 生产环境使用

```bash
# 启动监控
./scripts/production/monitor_manager.sh start

# 健康检查
./scripts/production/health_monitor.sh

# 快速部署
./scripts/production/quick_deploy.sh
```

## 📋 注意事项

- development/ 目录中的脚本主要用于开发阶段
- production/ 目录中的脚本用于生产环境
- 所有脚本都保持可执行权限
- 配置文件统一存放在 scripts 根目录
