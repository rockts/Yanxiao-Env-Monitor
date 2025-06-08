#!/bin/bash

# GitHub分支保护规则设置脚本
# 需要GitHub CLI (gh)工具

echo "🔒 设置GitHub分支保护规则..."

# 检查是否安装了GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 错误: 需要安装GitHub CLI工具"
    echo "请访问: https://cli.github.com/"
    echo "或运行: brew install gh"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 错误: 请先登录GitHub CLI"
    echo "运行: gh auth login"
    exit 1
fi

# 获取仓库信息
REPO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "📍 当前仓库: $REPO"

echo "设置master分支保护规则..."

# 设置master分支保护
gh api repos/$REPO/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["master-cd"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

if [ $? -eq 0 ]; then
    echo "✅ Master分支保护规则设置成功"
else
    echo "❌ 设置master分支保护规则失败"
fi

echo "设置dev分支保护规则..."

# 设置dev分支保护（相对宽松）
gh api repos/$REPO/branches/dev/protection \
  --method PUT \
  --field required_status_checks='{"strict":false,"contexts":["dev-ci"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews=null \
  --field restrictions=null \
  --field allow_force_pushes=true \
  --field allow_deletions=false

if [ $? -eq 0 ]; then
    echo "✅ Dev分支保护规则设置成功"
else
    echo "❌ 设置dev分支保护规则失败"
fi

echo ""
echo "🎯 分支保护规则总结:"
echo "📋 Master分支:"
echo "   - 需要Pull Request审核 (1人)"
echo "   - 需要状态检查通过"
echo "   - 禁止强制推送"
echo "   - 管理员也需要遵守规则"
echo ""
echo "📋 Dev分支:"
echo "   - 需要CI检查通过"
echo "   - 允许直接推送"
echo "   - 允许强制推送"
echo ""

echo "📖 使用说明:"
echo "1. 日常开发在dev分支进行"
echo "2. 发布时通过PR从dev合并到master"
echo "3. Master分支受到严格保护"
echo "4. 所有更改都会自动运行CI/CD"

echo ""
echo "✅ 分支保护规则设置完成！"
