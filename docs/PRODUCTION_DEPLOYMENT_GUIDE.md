# 生产环境手动部署指南

## 🎯 部署目标

- 服务器: rockts@192.168.1.115
- MQTT 地址: lot.lekee.cc
- 服务端口: 5052

## 📋 部署步骤

### 1. SSH 连接到生产服务器

```bash
ssh rockts@192.168.1.115
```

### 2. 创建项目目录

```bash
mkdir -p /home/rockts/env-monitor/{dashboard,logs,scripts}
cd /home/rockts/env-monitor
```

### 3. 手动上传文件

将以下文件复制到生产服务器：

**dashboard/目录下的文件：**

- `mqtt_flask_server_production.py` → `/home/rockts/env-monitor/dashboard/`
- `config_production.py` → `/home/rockts/env-monitor/dashboard/`
- `index.html` → `/home/rockts/env-monitor/dashboard/`
- `requirements.txt` → `/home/rockts/env-monitor/dashboard/`

### 4. 在生产服务器上执行安装

```bash
cd /home/rockts/env-monitor/dashboard

# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 启动服务

```bash
# 后台启动服务
nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &
```

### 6. 验证服务

```bash
# 检查服务状态
curl http://localhost:5052/api/status

# 查看日志
tail -f ../logs/production.log
```

## 🔧 systemd 服务配置（可选）

### 创建服务文件

```bash
sudo nano /etc/systemd/system/env-monitor.service
```

### 服务文件内容

```
[Unit]
Description=Environment Monitor Dashboard
After=network.target

[Service]
Type=simple
User=rockts
WorkingDirectory=/home/rockts/env-monitor/dashboard
Environment=PATH=/home/rockts/env-monitor/dashboard/venv/bin
ExecStart=/home/rockts/env-monitor/dashboard/venv/bin/python mqtt_flask_server_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启用和启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable env-monitor
sudo systemctl start env-monitor
sudo systemctl status env-monitor
```

## 🌐 访问地址

- API 状态: http://192.168.1.115:5052/api/status
- 大屏界面: http://192.168.1.115:5052/index.html
- 数据接口: http://192.168.1.115:5052/data

## 📊 服务管理命令

```bash
# 查看服务状态
sudo systemctl status env-monitor

# 重启服务
sudo systemctl restart env-monitor

# 查看日志
sudo journalctl -u env-monitor -f

# 停止服务
sudo systemctl stop env-monitor
```

## 🚀 快速启动脚本

创建 `/home/rockts/env-monitor/start.sh`:

```bash
#!/bin/bash
cd /home/rockts/env-monitor/dashboard
source venv/bin/activate
nohup python mqtt_flask_server_production.py > ../logs/production.log 2>&1 &
echo "服务已启动，日志: ../logs/production.log"
```

## 🔍 故障排查

1. **MQTT 连接问题**: 检查 lot.lekee.cc 是否可达
2. **端口占用**: `sudo netstat -tlnp | grep 5052`
3. **权限问题**: 确保 rockts 用户有目录读写权限
4. **Python 依赖**: 确保虚拟环境激活并安装了所有 dependencies

## 📝 生产环境特性

- ✅ MQTT 地址更新为 lot.lekee.cc
- ✅ 生产级日志记录
- ✅ 错误处理和重连机制
- ✅ 健康检查端点
- ✅ systemd 服务管理
