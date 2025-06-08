# 分支管理策略

## 分支结构

### master 分支

- **作用**: 生产环境发布分支
- **稳定性**: 高度稳定，只包含经过充分测试的代码
- **权限**: 受保护，只允许通过 Pull Request 合并
- **发布**: 直接从此分支部署到生产环境

### dev 分支

- **作用**: 开发和测试分支
- **功能**: 日常开发、功能测试、集成测试
- **权限**: 开发者可以直接推送
- **测试**: 所有测试代码和实验性功能都在此分支进行

## 工作流程

### 日常开发流程

1. **开发阶段**

   ```bash
   # 切换到dev分支
   git checkout dev

   # 拉取最新代码
   git pull origin dev

   # 进行开发和测试
   # ...编码、测试、调试...

   # 提交更改
   git add .
   git commit -m "描述性提交信息"

   # 推送到dev分支
   git push origin dev
   ```

2. **生产发布流程**

   ```bash
   # 确保dev分支测试完成且稳定
   git checkout dev
   git pull origin dev

   # 切换到master分支
   git checkout master
   git pull origin master

   # 合并dev分支到master（仅合并稳定功能）
   git merge dev --no-ff -m "Release: 版本描述"

   # 推送到生产环境
   git push origin master

   # 创建版本标签
   git tag -a v1.x.x -m "版本说明"
   git push origin v1.x.x
   ```

### 特殊情况处理

#### 热修复（Hotfix）

如果生产环境需要紧急修复：

1. 从 master 分支创建 hotfix 分支
2. 在 hotfix 分支进行修复
3. 测试修复效果
4. 将 hotfix 合并到 master
5. 将 hotfix 同步到 dev 分支

#### 功能分支（Feature Branch）

对于大型功能开发：

1. 从 dev 分支创建 feature 分支
2. 在 feature 分支开发
3. 测试完成后合并回 dev 分支
4. 删除 feature 分支

## 分支保护规则

### master 分支保护

- 禁止直接推送
- 要求 Pull Request 审核
- 要求状态检查通过
- 要求分支保持最新

### 提交规范

#### 提交信息格式

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

#### 提交类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 版本管理

### 版本号规范

采用语义化版本控制（Semantic Versioning）：

- `MAJOR.MINOR.PATCH`
- MAJOR: 不兼容的 API 修改
- MINOR: 向下兼容的功能性新增
- PATCH: 向下兼容的问题修正

### 发布周期

- **开发版本**: dev 分支持续集成
- **测试版本**: 每周从 dev 分支发布
- **正式版本**: 每月从 master 分支发布
- **紧急版本**: 根据需要发布 hotfix

## 注意事项

1. **测试代码不合并到 master**: 所有测试、调试、实验性代码只保留在 dev 分支
2. **保持分支同步**: 定期将 master 的稳定更新同步到 dev 分支
3. **代码审查**: 重要功能合并到 master 前进行代码审查
4. **自动化测试**: 设置 CI/CD 流水线自动测试
5. **备份策略**: 重要节点创建备份和标签

## 工具和自动化

### Git Hooks

- pre-commit: 代码格式检查
- pre-push: 单元测试检查
- post-merge: 自动化部署触发

### CI/CD 配置

- dev 分支: 自动运行测试套件
- master 分支: 自动部署到生产环境
- 状态报告: 自动发送构建状态通知

---

_本文档将根据项目需要持续更新和完善_
