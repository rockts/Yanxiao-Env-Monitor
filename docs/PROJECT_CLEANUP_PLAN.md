# 项目结构清理和分支策略实施计划

## 🎯 目标
- 保持master分支干净，适合生产环境
- dev分支保留开发文档和测试文件
- 减少文件冗余，提高项目可维护性

## 📋 清理计划

### 1. 根目录冗余文件处理
需要移动或删除的文件：
- `BRANCH_MANAGEMENT_COMPLETION_CERTIFICATE.md` → `docs/`
- `FINAL_SUCCESS_CONFIRMATION.md` → `docs/` 或删除
- `FINAL_VERIFICATION_REPORT.md` → `docs/` 或删除  
- `PROJECT_COMPLETION_CONFIRMATION.txt` → `docs/` 或删除
- `PROJECT_FINAL_STATUS.md` → `docs/` 或删除
- `auto_deploy_test.txt` → 删除（测试文件）
- `deployment_test.txt` → 删除（测试文件）

### 2. 生产环境master分支结构
保留核心文件：
```
Yanxiao-Env-Monitor/
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── .gitignore                   # Git忽略规则
├── dashboard/                   # Web仪表板
├── monitoring/                  # 监控核心代码
├── scripts/                     # 核心脚本（生产用）
├── deployment/                  # 部署脚本
├── docs/                        # 必要文档
└── assets/                      # 资源文件
```

### 3. 开发分支dev结构
保留所有开发文档和工具：
```
Yanxiao-Env-Monitor/
├── [生产环境所有文件]
├── docs/
│   ├── [所有分支管理文档]
│   ├── [项目完成报告]
│   └── [开发指南]
├── scripts/
│   ├── [所有开发和管理脚本]
│   └── [分支管理工具]
└── logs/                        # 开发日志
```

## 🔄 执行步骤

1. **在dev分支上清理文件结构**
2. **创建干净的生产环境配置**
3. **将dev分支的稳定功能发布到master**
4. **确保master分支只包含生产必需文件**

## ⚠️ 注意事项
- 先在dev分支完成清理
- 测试功能正常后再合并到master
- 保留重要的开发文档在dev分支
- master分支专注于生产环境稳定性
