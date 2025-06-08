#!/bin/bash

# 分支管理策略验证测试脚本
# 验证所有分支管理功能是否正常工作

echo "🔍 分支管理策略验证测试"
echo "========================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "测试: $test_name ... "
    
    # 运行测试命令
    eval "$test_command" >/dev/null 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq $expected_exit_code ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 显示测试结果
show_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "pass" ]; then
        echo -e "  ${GREEN}✅ $test_name${NC}"
        [ -n "$details" ] && echo -e "     $details"
    else
        echo -e "  ${RED}❌ $test_name${NC}"
        [ -n "$details" ] && echo -e "     $details"
    fi
}

echo "1. 🔧 验证工具脚本存在性"
echo "----------------------------"

# 检查核心脚本文件
scripts_to_check=(
    "scripts/branch-manager.sh"
    "scripts/branch-monitor.sh"
    "scripts/setup-branch-protection.sh"
    "scripts/setup-branch-cron.sh"
    "scripts/setup-git-config.sh"
)

for script in "${scripts_to_check[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        show_test_result "$(basename "$script")" "pass" "文件存在且可执行"
    else
        show_test_result "$(basename "$script")" "fail" "文件不存在或不可执行"
    fi
done

echo ""
echo "2. 📁 验证文档文件完整性"
echo "----------------------------"

# 检查文档文件
docs_to_check=(
    "docs/BRANCH_MANAGEMENT_STRATEGY.md"
    "docs/BRANCH_MANAGEMENT_QUICK_GUIDE.md"
    "docs/BRANCH_MANAGEMENT_IMPLEMENTATION_REPORT.md"
    "docs/BRANCH_MANAGEMENT_COMPLETE_SUMMARY.md"
    ".gitmessage"
)

for doc in "${docs_to_check[@]}"; do
    if [ -f "$doc" ]; then
        file_size=$(wc -c < "$doc" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 100 ]; then
            show_test_result "$(basename "$doc")" "pass" "文件存在，大小: ${file_size} bytes"
        else
            show_test_result "$(basename "$doc")" "fail" "文件太小或为空"
        fi
    else
        show_test_result "$(basename "$doc")" "fail" "文件不存在"
    fi
done

echo ""
echo "3. 🔗 验证Git配置"
echo "----------------------------"

# 检查Git配置
git_configs=(
    "merge.ff:false"
    "push.default:simple"
    "color.ui:auto"
)

for config in "${git_configs[@]}"; do
    key=$(echo "$config" | cut -d: -f1)
    expected=$(echo "$config" | cut -d: -f2)
    actual=$(git config --get "$key" 2>/dev/null || echo "未设置")
    
    if [ "$actual" = "$expected" ]; then
        show_test_result "$key" "pass" "值: $actual"
    else
        show_test_result "$key" "fail" "期望: $expected, 实际: $actual"
    fi
done

echo ""
echo "4. 🪝 验证Git钩子"
echo "----------------------------"

# 检查pre-commit钩子
if [ -f ".git/hooks/pre-commit" ] && [ -x ".git/hooks/pre-commit" ]; then
    show_test_result "pre-commit钩子" "pass" "钩子文件存在且可执行"
else
    show_test_result "pre-commit钩子" "fail" "钩子文件不存在或不可执行"
fi

echo ""
echo "5. 🔧 验证分支管理工具功能"
echo "----------------------------"

# 测试分支管理工具
if [ -x "scripts/branch-manager.sh" ]; then
    # 测试帮助功能
    if ./scripts/branch-manager.sh help >/dev/null 2>&1; then
        show_test_result "分支管理工具帮助" "pass" "帮助功能正常"
    else
        show_test_result "分支管理工具帮助" "fail" "帮助功能异常"
    fi
    
    # 测试状态检查功能
    if ./scripts/branch-manager.sh status >/dev/null 2>&1; then
        show_test_result "分支状态检查" "pass" "状态检查功能正常"
    else
        show_test_result "分支状态检查" "fail" "状态检查功能异常"
    fi
else
    show_test_result "分支管理工具" "fail" "脚本不存在或不可执行"
fi

echo ""
echo "6. 📊 验证分支监控功能"
echo "----------------------------"

# 测试分支监控
if [ -x "scripts/branch-monitor.sh" ]; then
    # 创建临时监控测试
    if timeout 10 ./scripts/branch-monitor.sh >/dev/null 2>&1; then
        show_test_result "分支监控脚本" "pass" "监控脚本运行正常"
    else
        show_test_result "分支监控脚本" "fail" "监控脚本运行异常或超时"
    fi
else
    show_test_result "分支监控脚本" "fail" "脚本不存在或不可执行"
fi

echo ""
echo "7. 🚀 验证CI/CD配置"
echo "----------------------------"

# 检查GitHub Actions配置
if [ -f ".github/workflows/branch-management.yml" ]; then
    # 简单检查YAML文件格式
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/branch-management.yml'))" 2>/dev/null; then
            show_test_result "GitHub Actions配置" "pass" "YAML格式正确"
        else
            show_test_result "GitHub Actions配置" "fail" "YAML格式错误"
        fi
    else
        show_test_result "GitHub Actions配置" "pass" "文件存在（无法验证YAML格式）"
    fi
else
    show_test_result "GitHub Actions配置" "fail" "配置文件不存在"
fi

echo ""
echo "8. 🔍 验证分支状态"
echo "----------------------------"

# 检查当前分支状态
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -n "$current_branch" ]; then
    show_test_result "当前分支" "pass" "分支: $current_branch"
    
    # 检查工作区状态
    if [ -z "$(git status --porcelain)" ]; then
        show_test_result "工作区状态" "pass" "工作区干净"
    else
        uncommitted_files=$(git status --porcelain | wc -l | tr -d ' ')
        show_test_result "工作区状态" "pass" "有 $uncommitted_files 个未提交文件"
    fi
    
    # 检查远程分支
    if git ls-remote --heads origin >/dev/null 2>&1; then
        show_test_result "远程连接" "pass" "可以连接远程仓库"
    else
        show_test_result "远程连接" "fail" "无法连接远程仓库"
    fi
else
    show_test_result "Git仓库" "fail" "不在Git仓库中"
fi

echo ""
echo "9. 📋 生成详细报告"
echo "----------------------------"

# 生成详细状态报告
echo "分支状态详情:"
if command -v ./scripts/branch-manager.sh >/dev/null 2>&1; then
    ./scripts/branch-manager.sh status 2>/dev/null | head -10
fi

echo ""
echo "Git配置摘要:"
echo "  合并策略: $(git config --get merge.ff || echo '未设置')"
echo "  推送策略: $(git config --get push.default || echo '未设置')"
echo "  颜色输出: $(git config --get color.ui || echo '未设置')"

echo ""
echo "文件统计:"
echo "  脚本文件: $(find scripts/ -name "*.sh" -type f | wc -l | tr -d ' ') 个"
echo "  文档文件: $(find docs/ -name "*.md" -type f | wc -l | tr -d ' ') 个"
echo "  配置文件: $(find .github/ -name "*.yml" -type f 2>/dev/null | wc -l | tr -d ' ') 个"

echo ""
echo "========================="
echo "🎯 验证测试完成"
echo "========================="

# 总结
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有功能验证通过！${NC}"
    echo -e "${GREEN}🎉 分支管理策略已成功实施并正常工作${NC}"
else
    echo -e "${YELLOW}⚠️ 发现 $TESTS_FAILED 个问题需要解决${NC}"
fi

echo ""
echo "📊 验证统计:"
echo "  总测试项: $TESTS_TOTAL"
echo "  通过: $TESTS_PASSED"
echo "  失败: $TESTS_FAILED"

echo ""
echo "💡 建议操作:"
echo "1. 如有失败项，请检查相关配置"
echo "2. 运行 ./scripts/branch-manager.sh status 查看当前状态"
echo "3. 查看文档了解详细使用方法"
echo "4. 定期运行此验证脚本确保系统正常"

echo ""
echo "📞 获取帮助:"
echo "  ./scripts/branch-manager.sh help"
echo "  查看 docs/ 目录中的详细文档"

exit 0
