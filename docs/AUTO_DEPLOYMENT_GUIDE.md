# 自动部署配置指南

## 概述

本项目支持 Git 推送触发的自动部署，代码推送到生产服务器后会自动更新并重启服务。

## 部署架构

```
本地开发环境
    ↓ git push
GitHub/Gitee远程仓库
    ↓ git push production
生产服务器 (192.168.1.115)
    ↓ post-receive hook
自动部署和重启服务
```

## 快速设置

### 1. 初始化自动部署

```bash
# 执行自动部署设置脚本
./deployment/setup-auto-deploy.sh
```

### 2. 推送和部署

```bash
# 推送到GitHub/Gitee
git push origin master

# 推送到生产环境（触发自动部署）
git push production master

# 或者一次性推送到所有远程仓库
git push origin master && git push production master
```

### 3. 验证部署

```bash
# 检查服务状态
curl http://192.168.1.115:5052/health

# 查看部署日志
ssh rockts@192.168.1.115 'tail -f /home/rockts/deployment.log'
```

## 自动部署流程

当代码推送到生产服务器时，post-receive 钩子会自动执行以下操作：

1. **备份当前版本** - 备份到 `/home/rockts/env-monitor-backup`
2. **拉取最新代码** - 从 Git 仓库拉取最新代码
3. **更新依赖** - 如果有 requirements.txt，自动更新 Python 依赖
4. **停止旧服务** - 停止运行中的服务进程
5. **启动新服务** - 启动监控守护进程和 Web 服务
6. **健康检查** - 验证服务是否正常启动
7. **设置权限** - 确保文件权限正确

## 监控和调试

### 查看部署日志

```bash
ssh rockts@192.168.1.115 'tail -f /home/rockts/deployment.log'
```

### 查看服务日志

```bash
# Web服务日志
ssh rockts@192.168.1.115 'tail -f /home/rockts/env-monitor/logs/production.log'

# 监控守护进程日志
ssh rockts@192.168.1.115 'tail -f /home/rockts/env-monitor/logs/monitor_daemon.log'
```

### 手动重启服务

```bash
ssh rockts@192.168.1.115 << 'EOF'
cd /home/rockts/env-monitor
sudo pkill -f "mqtt_flask_server_production.py"
sudo pkill -f "monitoring_daemon.py"
sleep 2
cd dashboard && sudo nohup python3 mqtt_flask_server_production.py > ../logs/production.log 2>&1 &
cd ../monitoring && sudo nohup python3 monitoring_daemon.py > ../logs/monitor_daemon.log 2>&1 &
EOF
```

## 回滚操作

如果部署出现问题，可以快速回滚到备份版本：

```bash
ssh rockts@192.168.1.115 << 'EOF'
sudo pkill -f "mqtt_flask_server_production.py"
sudo pkill -f "monitoring_daemon.py"
sudo rm -rf /home/rockts/env-monitor
sudo mv /home/rockts/env-monitor-backup /home/rockts/env-monitor
cd /home/rockts/env-monitor/dashboard
sudo nohup python3 mqtt_flask_server_production.py > ../logs/production.log 2>&1 &
EOF
```

## 生产环境地址

- **Web 界面**: http://192.168.1.115:5052/
- **健康检查**: http://192.168.1.115:5052/health
- **API 状态**: http://192.168.1.115:5052/api/status

## 注意事项

1. **权限**: 确保 Git 仓库和部署脚本有正确的执行权限
2. **网络**: 确保生产服务器可以访问 GitHub/Gitee
3. **依赖**: 生产服务器需要安装 Python3、pip3、git 等基础工具
4. **防火墙**: 确保 5052 端口在生产服务器上开放
5. **监控**: 建议设置服务监控，确保服务异常时能及时重启
