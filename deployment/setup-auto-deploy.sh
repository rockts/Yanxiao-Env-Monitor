#!/bin/bash

# 生产环境自动部署设置脚本
# Setup automatic deployment for production environment

set -e

PRODUCTION_SERVER="rockts@192.168.1.115"
PRODUCTION_PATH="/home/rockts/env-monitor"
REPO_URL="https://github.com/rockts/Yanxiao-Env-Monitor.git"

echo "🚀 设置生产环境自动部署..."

# 在生产服务器上创建bare repository用于自动部署
ssh $PRODUCTION_SERVER << 'EOF'
    # 创建目录
    mkdir -p /home/rockts/env-monitor-repo.git
    mkdir -p /home/rockts/env-monitor
    mkdir -p /home/rockts/env-monitor-backup
    
    # 初始化bare repository
    cd /home/rockts/env-monitor-repo.git
    git init --bare
    
    # 如果生产目录为空，先克隆代码
    if [ ! -f "/home/rockts/env-monitor/.git/config" ]; then
        echo "初始化生产环境代码..."
        cd /home/rockts/env-monitor
        git clone https://github.com/rockts/Yanxiao-Env-Monitor.git .
    fi
    
    echo "✅ 生产服务器准备完成"
EOF

echo "📤 上传post-receive钩子..."
scp deployment/post-receive-hook.sh $PRODUCTION_SERVER:/home/rockts/env-monitor-repo.git/hooks/post-receive

echo "🔧 设置钩子权限..."
ssh $PRODUCTION_SERVER 'chmod +x /home/rockts/env-monitor-repo.git/hooks/post-receive'

echo "🔗 配置Git远程仓库..."
# 添加生产服务器作为远程仓库
git remote remove production 2>/dev/null || true
git remote add production $PRODUCTION_SERVER:/home/rockts/env-monitor-repo.git

echo "🧪 测试自动部署..."
git push production master

echo ""
echo "✅ 自动部署设置完成！"
echo ""
echo "📝 使用说明："
echo "1. 推送到生产环境："
echo "   git push production master"
echo ""
echo "2. 推送到GitHub/Gitee和生产环境："
echo "   git push origin master && git push production master"
echo ""
echo "3. 检查部署状态："
echo "   ssh $PRODUCTION_SERVER 'tail -f /home/rockts/deployment.log'"
echo ""
echo "4. 检查服务状态："
echo "   curl http://192.168.1.115:5052/health"
echo ""
echo "🔍 生产环境地址："
echo "   - Web界面: http://192.168.1.115:5052/"
echo "   - 健康检查: http://192.168.1.115:5052/health"
echo "   - API状态: http://192.168.1.115:5052/api/status"
