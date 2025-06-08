# Git配置脚本 - 分支管理设置

# 设置默认分支推送行为
git config push.default simple

# 设置合并时的默认行为（禁用快进）
git config merge.ff false

# 设置拉取时的默认行为
git config pull.rebase false

# 设置提交模板
git config commit.template .gitmessage

# 设置分支自动跟踪
git config branch.autosetupmerge always
git config branch.autosetuprebase always

# 设置颜色输出
git config color.ui auto
git config color.status auto
git config color.branch auto
git config color.diff auto

# 设置别名
git config alias.st status
git config alias.co checkout
git config alias.br branch
git config alias.ci commit
git config alias.lg "log --oneline --graph --decorate --all"
git config alias.last "log -1 HEAD"
git config alias.unstage "reset HEAD --"

echo "Git配置完成！"
