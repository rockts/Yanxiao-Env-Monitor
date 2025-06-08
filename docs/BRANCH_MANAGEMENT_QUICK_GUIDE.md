# 分支管理快速指南

## 🚀 快速开始

### 分支概念

- **dev 分支**: 开发测试分支，所有开发工作在此进行
- **master 分支**: 生产发布分支，只包含稳定代码

### 常用命令

#### 1. 切换到开发分支

```bash
./scripts/branch-manager.sh dev
```

#### 2. 查看分支状态

```bash
./scripts/branch-manager.sh status
```

#### 3. 同步分支

```bash
./scripts/branch-manager.sh sync
```

#### 4. 切换到生产分支

```bash
./scripts/branch-manager.sh master
```

## 📋 日常工作流程

### 开发流程 (在 dev 分支)

```bash
# 1. 确保在dev分支
./scripts/branch-manager.sh dev

# 2. 进行开发
# ... 编码、测试 ...

# 3. 提交更改
git add .
git commit -m "feat: 添加新功能"

# 4. 推送到远程
git push origin dev
```

### 发布流程 (从 dev 到 master)

```bash
# 1. 确保dev分支测试完成
./scripts/branch-manager.sh status

# 2. 切换到master分支
git checkout master
git pull origin master

# 3. 合并dev分支稳定功能
git merge dev --no-ff -m "release: v1.x.x"

# 4. 推送到生产环境
git push origin master

# 5. 创建版本标签
git tag -a v1.x.x -m "版本说明"
git push origin v1.x.x
```

## 🔧 工具使用

### 分支管理工具

```bash
# 显示帮助
./scripts/branch-manager.sh help

# 所有可用命令
./scripts/branch-manager.sh status   # 查看状态
./scripts/branch-manager.sh dev      # 切换dev分支
./scripts/branch-manager.sh master   # 切换master分支
./scripts/branch-manager.sh sync     # 同步分支
```

### Git 配置

```bash
# 应用推荐配置
./scripts/setup-git-config.sh
```

## ⚠️ 重要原则

1. **测试代码不合并到 master**: 所有测试、调试代码只在 dev 分支
2. **master 分支稳定**: 只包含经过测试的稳定代码
3. **定期同步**: 及时将 master 的更新同步到 dev 分支
4. **提交规范**: 使用规范的提交信息格式

## 🛡️ 安全检查

### Pre-commit 钩子

系统会自动检查：

- 分支提交确认
- Python 语法错误
- 大文件警告
- 敏感信息扫描

### 提交格式

```
类型(范围): 简短描述

详细说明（可选）

相关问题（可选）
```

类型: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🚨 常见问题

### Q: 如何撤销错误的合并？

```bash
git reset --hard HEAD~1  # 撤销最后一次合并
```

### Q: 如何查看分支差异？

```bash
git log dev..master --oneline  # master比dev多的提交
git log master..dev --oneline  # dev比master多的提交
```

### Q: 如何处理冲突？

```bash
git merge dev           # 可能产生冲突
# 手动解决冲突后
git add .
git commit -m "resolve: 解决合并冲突"
```

## 📞 技术支持

如果遇到问题：

1. 查看分支管理策略文档
2. 使用分支管理工具检查状态
3. 参考实施报告中的详细说明

---

_快速指南 - 让分支管理更简单_
