# Git 多电脑同步指南

## 问题说明

文件通过云盘（SynologyDrive）同步，但 Git 提交记录在不同电脑上不一致的解决方案。

## 解决方案

### 方案一：设置远程 Git 仓库（推荐）

#### 1. 创建远程仓库

在 GitHub、GitLab、Gitee 或其他 Git 托管平台创建一个新仓库。

#### 2. 添加远程仓库

```bash
cd /Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor
git remote add origin <你的远程仓库URL>
```

#### 3. 推送到远程仓库

```bash
# 推送主分支
git push -u origin main

# 推送当前分支
git push -u origin feature/data-acquisition
```

#### 4. 在其他电脑上克隆

```bash
# 删除本地仓库，重新克隆
cd /path/to/SynologyDrive/Drive/
rm -rf Yanxiao-Env-Monitor/.git
git clone <你的远程仓库URL> Yanxiao-Env-Monitor-temp
cd Yanxiao-Env-Monitor-temp
cp -r .git ../Yanxiao-Env-Monitor/
cd ..
rm -rf Yanxiao-Env-Monitor-temp
cd Yanxiao-Env-Monitor
git status
```

### 方案二：使用 Git Bundle（适合私有项目）

#### 1. 创建 Git Bundle

```bash
cd /Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor
git bundle create ../yanxiao-env-monitor.bundle --all
```

#### 2. 在其他电脑上应用 Bundle

```bash
cd /path/to/SynologyDrive/Drive/Yanxiao-Env-Monitor
git remote add bundle ../yanxiao-env-monitor.bundle
git fetch bundle
git merge bundle/feature/data-acquisition
```

### 方案三：同步脚本（自动化）

使用我们创建的同步脚本来自动处理同步。

## 日常同步流程

### 开始工作前

```bash
# 拉取最新更改
git pull origin feature/data-acquisition
```

### 完成工作后

```bash
# 提交更改
git add .
git commit -m "描述你的更改"
git push origin feature/data-acquisition
```

## 注意事项

1. **始终在同一台电脑上提交**: 尽量在主力电脑上进行 Git 操作
2. **定期同步**: 每天工作结束后推送到远程仓库
3. **分支管理**: 为不同功能创建不同分支
4. **冲突处理**: 遇到冲突时谨慎合并

## 紧急情况处理

如果遇到同步问题：

```bash
# 创建备份
git stash push -m "紧急备份"

# 强制同步（谨慎使用）
git reset --hard origin/feature/data-acquisition

# 恢复备份
git stash pop
```
