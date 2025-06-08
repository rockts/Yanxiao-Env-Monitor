#!/bin/bash

# Git post-receive hook for automatic deployment
# 生产环境自动部署钩子

# 配置项
PRODUCTION_PATH="/home/rockts/env-monitor"
BACKUP_PATH="/home/rockts/env-monitor-backup"
LOG_FILE="/home/rockts/deployment.log"
BRANCH="master"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 错误处理
handle_error() {
    log "ERROR: $1"
    exit 1
}

# 检查分支
while read oldrev newrev refname; do
    # 只处理master分支的推送
    if [[ $refname == "refs/heads/$BRANCH" ]]; then
        log "=== 开始自动部署 ==="
        log "分支: $BRANCH"
        log "旧版本: $oldrev"
        log "新版本: $newrev"
        
        # 备份当前版本
        log "备份当前版本..."
        if [ -d "$PRODUCTION_PATH" ]; then
            sudo rm -rf "$BACKUP_PATH" 2>/dev/null || true
            sudo cp -r "$PRODUCTION_PATH" "$BACKUP_PATH" || handle_error "备份失败"
            log "备份完成: $BACKUP_PATH"
        fi
        
        # 部署新版本
        log "部署新版本..."
        cd "$PRODUCTION_PATH" || handle_error "无法进入生产目录"
        
        # 拉取最新代码
        sudo git fetch origin || handle_error "Git fetch 失败"
        sudo git reset --hard origin/$BRANCH || handle_error "Git reset 失败"
        
        # 检查Python依赖
        if [ -f "requirements.txt" ]; then
            log "更新Python依赖..."
            sudo pip3 install -r requirements.txt || log "WARNING: 依赖安装可能有问题"
        fi
        
        # 重启服务
        log "重启服务..."
        
        # 停止旧服务
        sudo pkill -f "mqtt_flask_server_production.py" 2>/dev/null || true
        sudo pkill -f "monitoring_daemon.py" 2>/dev/null || true
        sleep 2
        
        # 确保日志目录存在
        sudo mkdir -p logs
        
        # 启动监控守护进程
        if [ -f "monitoring/monitoring_daemon.py" ]; then
            log "启动监控守护进程..."
            cd monitoring
            sudo nohup python3 monitoring_daemon.py > ../logs/monitor_daemon.log 2>&1 &
            cd ..
        fi
        
        # 启动Web服务
        if [ -f "dashboard/mqtt_flask_server_production.py" ]; then
            log "启动Web服务..."
            cd dashboard
            sudo nohup python3 mqtt_flask_server_production.py > ../logs/production.log 2>&1 &
            cd ..
        fi
        
        sleep 3
        
        # 健康检查
        log "执行健康检查..."
        if curl -s "http://localhost:5052/health" | grep -q "healthy"; then
            log "✅ 部署成功！服务运行正常"
        else
            log "⚠️ 部署完成，但健康检查未通过"
        fi
        
        # 设置文件权限
        sudo chown -R rockts:rockts "$PRODUCTION_PATH"
        sudo chmod +x scripts/*.sh 2>/dev/null || true
        sudo chmod +x deployment/*.sh 2>/dev/null || true
        
        log "=== 自动部署完成 ==="
        
        # 发送通知（可选）
        # curl -X POST "YOUR_NOTIFICATION_WEBHOOK" -d "环境监控系统已自动部署更新"
        
    fi
done
