#!/bin/bash

# Git post-receive hook for automatic deployment
# 生产环境自动部署钩子 - 修复版本

# 配置项
PRODUCTION_PATH="/home/rockts/env-monitor"
BACKUP_PATH="/home/rockts/env-monitor-backup"
LOG_FILE="/home/rockts/deployment.log"
BRANCH="master"
GIT_DIR="/home/rockts/env-monitor-repo.git"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 错误处理
handle_error() {
    log "ERROR: $1"
    return 1
}

# 检查分支
while read oldrev newrev refname; do
    # 只处理master分支的推送
    if [[ $refname == "refs/heads/$BRANCH" ]]; then
        log "=== 开始自动部署 ==="
        log "分支: $BRANCH"
        log "旧版本: $oldrev"
        log "新版本: $newrev"
        
        # 备份当前版本 (不使用sudo，避免权限问题)
        log "备份当前版本..."
        if [ -d "$PRODUCTION_PATH" ]; then
            rm -rf "$BACKUP_PATH" 2>/dev/null || true
            cp -r "$PRODUCTION_PATH" "$BACKUP_PATH" || log "WARNING: 备份失败，继续部署"
            log "备份完成: $BACKUP_PATH"
        fi
        
        # 确保生产目录存在
        mkdir -p "$PRODUCTION_PATH"
        
        # 使用git checkout从bare仓库部署到工作目录
        log "部署新版本..."
        cd "$GIT_DIR" || handle_error "无法进入Git仓库目录"
        
        # 使用git checkout部署文件
        if git --git-dir="$GIT_DIR" --work-tree="$PRODUCTION_PATH" checkout -f $BRANCH; then
            log "✅ 代码部署成功"
        else
            handle_error "Git checkout 失败"
        fi
        
        # 切换到生产目录
        cd "$PRODUCTION_PATH" || handle_error "无法进入生产目录"
        
        # 检查Python依赖
        if [ -f "requirements.txt" ]; then
            log "更新Python依赖..."
            pip3 install -r requirements.txt --user || log "WARNING: 依赖安装可能有问题"
        fi
        
        # 检查dashboard目录下的依赖
        if [ -f "dashboard/config/requirements.txt" ]; then
            log "更新Dashboard依赖..."
            pip3 install -r dashboard/config/requirements.txt --user || log "WARNING: Dashboard依赖安装可能有问题"
        fi
        
        # 重启服务
        log "重启服务..."
        
        # 停止旧服务
        pkill -f "mqtt_flask_server_production.py" 2>/dev/null || true
        pkill -f "monitoring_daemon.py" 2>/dev/null || true
        sleep 2
        
        # 确保日志目录存在
        mkdir -p logs
        mkdir -p dashboard/logs
        
        # 启动监控守护进程
        if [ -f "monitoring/monitoring_daemon.py" ]; then
            log "启动监控守护进程..."
            cd monitoring
            nohup python3 monitoring_daemon.py > ../logs/monitor_daemon.log 2>&1 &
            cd ..
            log "监控守护进程已启动"
        fi
        
        # 启动Web服务
        if [ -f "dashboard/server/mqtt_flask_server_production.py" ]; then
            log "启动Web服务..."
            cd dashboard/server
            nohup python3 mqtt_flask_server_production.py > ../../logs/production.log 2>&1 &
            cd ../..
            log "Web服务已启动"
        fi
        
        sleep 3
        
        # 健康检查
        log "执行健康检查..."
        health_check_count=0
        max_checks=5
        
        while [ $health_check_count -lt $max_checks ]; do
            if curl -s "http://localhost:5052/health" | grep -q "healthy"; then
                log "✅ 部署成功！服务运行正常"
                break
            else
                health_check_count=$((health_check_count + 1))
                log "健康检查 $health_check_count/$max_checks 失败，等待重试..."
                sleep 2
            fi
        done
        
        if [ $health_check_count -eq $max_checks ]; then
            log "⚠️ 部署完成，但健康检查未通过"
        fi
        
        # 设置文件权限
        chown -R rockts:rockts "$PRODUCTION_PATH" 2>/dev/null || true
        chmod +x scripts/*.sh 2>/dev/null || true
        chmod +x deployment/*.sh 2>/dev/null || true
        
        # 显示服务状态
        log "当前运行的相关进程:"
        ps aux | grep -E "(mqtt_flask_server|monitoring_daemon)" | grep -v grep | while read line; do
            log "  $line"
        done
        
        log "=== 自动部署完成 ==="
        
        # 可选：发送通知
        # curl -X POST "YOUR_NOTIFICATION_WEBHOOK" -d "环境监控系统已自动部署更新: $newrev"
        
    fi
done
