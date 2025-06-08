# 烟小环境监测系统 - 多电脑 Git 同步完整方案

## 📋 概述

本文档详细介绍如何在多台电脑间同步 **烟小智慧环境监测物联网系统** 的代码，解决通过云盘同步文件但 Git 提交记录不一致的问题。

## 🎯 解决的问题

- ✅ 文件通过 SynologyDrive 云盘同步，但 Git 提交历史不一致
- ✅ 多台电脑开发时代码版本管理混乱
- ✅ 需要手动处理 Git 冲突和同步
- ✅ 缺乏统一的代码同步流程

## 🛠️ 解决方案

我们提供了两种同步方案和配套工具：

### 方案 A：远程仓库同步（推荐）

- 适合有网络环境的团队协作
- 使用 GitHub、GitLab 或 Gitee 等平台
- 提供完整的版本控制和协作功能

### 方案 B：Bundle 文件同步

- 适合私有项目或无网络环境
- 通过云盘传输 Git bundle 文件
- 保持完整的 Git 历史记录

## 📁 已创建的工具文件

```
scripts/
├── git_sync_tool.sh         # 交互式Git同步管理工具
├── quick_sync.sh            # 快速提交和同步脚本
└── sync_config.json         # 同步配置文件

git_sync_guide.md            # 详细同步指南
MULTI_COMPUTER_SYNC_SETUP.md # 本文档（完整设置指南）
```

## 🚀 快速开始

### 1. 日常快速同步

```bash
# 方法1: 使用默认提交信息
./scripts/quick_sync.sh

# 方法2: 指定提交信息
./scripts/quick_sync.sh "修复传感器数据显示问题"
```

### 2. 完整同步管理

```bash
# 运行交互式同步工具
./scripts/git_sync_tool.sh
```

## 📝 详细使用步骤

### 第一次设置（主开发机）

1. **确认当前状态**

   ```bash
   cd /Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor
   git status
   git log --oneline -5
   ```

2. **选择同步方案**

   **方案 A - 设置远程仓库：**

   ```bash
   # 在GitHub/GitLab/Gitee创建新仓库后
   git remote add origin <你的仓库URL>
   git push -u origin feature/data-acquisition
   ```

   **方案 B - 使用 Bundle 同步：**

   ```bash
   ./scripts/quick_sync.sh "初始化项目"
   # 会自动创建bundle文件在上级目录
   ```

### 其他电脑设置

#### 方案 A - 使用远程仓库

```bash
cd /path/to/SynologyDrive/Drive/Yanxiao-Env-Monitor

# 如果已有.git目录，先备份
mv .git .git_backup

# 初始化并连接远程仓库
git init
git remote add origin <仓库URL>
git fetch origin
git checkout -b feature/data-acquisition origin/feature/data-acquisition

# 验证同步成功
git log --oneline -5
```

#### 方案 B - 使用 Bundle 文件

```bash
cd /path/to/SynologyDrive/Drive/

# 找到最新的bundle文件
ls -la yanxiao-env-monitor-sync-*.bundle

# 应用bundle
cd Yanxiao-Env-Monitor
git remote add bundle ../yanxiao-env-monitor-sync-最新时间戳.bundle
git fetch bundle
git merge bundle/feature/data-acquisition
```

## 🔄 日常工作流程

### 开始工作前

```bash
# 方案A - 从远程仓库拉取
git pull origin feature/data-acquisition

# 方案B - 应用最新bundle（如果有）
./scripts/git_sync_tool.sh  # 选择 "6) 应用Git Bundle"
```

### 工作完成后

```bash
# 快速提交并同步
./scripts/quick_sync.sh "完成XXX功能开发"

# 方案A - 自动推送到远程仓库
# 方案B - 自动创建新的bundle文件
```

## ⚙️ 配置文件说明

编辑 `scripts/sync_config.json` 可以自定义同步行为：

```json
{
 "sync_config": {
  "method": "bundle", // "remote" 或 "bundle"
  "auto_commit": true, // 是否自动提交
  "default_commit_message": "自动同步提交",
  "bundle_path": "../bundles/", // bundle文件存储路径
  "remote_url": "", // 远程仓库URL
  "main_branch": "feature/data-acquisition"
 }
}
```

## 🎨 工具特性

### git_sync_tool.sh 功能菜单

```
1) 检查Git状态         - 查看当前工作区状态
2) 提交当前更改         - 交互式提交未保存的更改
3) 推送到远程仓库       - 上传到GitHub/GitLab等
4) 从远程仓库拉取       - 下载最新版本
5) 创建Git Bundle      - 生成离线同步文件
6) 应用Git Bundle      - 从bundle文件同步
7) 完整同步流程         - 自动执行完整同步
8) 设置远程仓库         - 配置GitHub/GitLab连接
```

### quick_sync.sh 特性

- 🚀 一键快速同步
- 📝 智能提交信息生成
- 🔄 自动选择同步方案
- ✅ 彩色状态提示
- 📦 自动 Bundle 创建

## 🔧 故障排除

### 常见问题及解决方案

1. **提示"不是 Git 仓库"**

   ```bash
   cd /Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor
   git init
   git add .
   git commit -m "初始化仓库"
   ```

2. **推送失败**

   ```bash
   # 检查远程仓库配置
   git remote -v

   # 重新设置远程仓库
   git remote remove origin
   git remote add origin <正确的URL>
   ```

3. **Bundle 文件不存在**

   ```bash
   # 手动创建bundle
   git bundle create ../manual-sync.bundle --all
   ```

4. **合并冲突**

   ```bash
   # 查看冲突文件
   git status

   # 手动解决冲突后
   git add .
   git commit -m "解决合并冲突"
   ```

## 📊 同步状态监控

使用以下命令检查同步状态：

```bash
# 检查本地状态
git status
git log --oneline -10

# 检查远程同步状态（方案A）
git remote -v
git fetch origin
git log --oneline origin/feature/data-acquisition -5

# 检查bundle文件（方案B）
ls -la ../yanxiao-env-monitor-sync-*.bundle
```

## 🎯 最佳实践

1. **主开发机原则**：指定一台电脑为主开发机，负责主要的 Git 操作
2. **定期同步**：每天工作结束后执行同步
3. **清晰的提交信息**：使用有意义的提交描述
4. **分支管理**：为不同功能创建专门的分支
5. **备份习惯**：定期创建项目备份

## 📅 同步计划建议

- **每日同步**：使用 `quick_sync.sh` 提交当天更改
- **每周备份**：创建完整的项目 bundle 备份
- **版本发布**：重要功能完成后推送到远程仓库
- **多人协作**：使用远程仓库进行团队同步

## 🆘 技术支持

如果遇到问题，请：

1. 查看 `git_sync_guide.md` 详细指南
2. 运行 `./scripts/git_sync_tool.sh` 使用交互式工具
3. 检查 `scripts/sync_config.json` 配置是否正确

---

> 💡 **提示**：建议优先使用方案 A（远程仓库），它提供更好的版本控制和协作体验。方案 B 适合对代码隐私有要求或网络受限的环境。
