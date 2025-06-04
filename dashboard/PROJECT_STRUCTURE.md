# 烟小智慧环境监测物联网系统 - 项目结构说明

## 当前目录结构

```
dashboard/
├── README.md                           # 项目说明文档
├── PROJECT_STRUCTURE.md              # 项目结构说明（本文件）
├── requirements.txt                   # Python依赖文件
├── mqtt_flask_server.py              # 后端Flask服务主文件
│
├── frontend/                          # 前端文件目录
│   ├── index.html                    # 主要前端页面
│   ├── index_simple.html            # 简化版前端页面
│   ├── debug.html                   # 调试页面
│   ├── test/                        # 测试页面目录
│   │   ├── test.html               # 基础测试页面
│   │   ├── test_frontend.html      # 前端功能测试
│   │   ├── test_responsive.html    # 响应式测试
│   │   └── test_video.html         # 视频功能测试
│   └── assets/                      # 前端资源文件
│       └── img/                     # 图片资源
│           ├── logo.png
│           └── logo_white.png
│
├── backend/                          # 后端相关文件
│   ├── mqtt_flask_server.py        # Flask主服务文件
│   ├── config/                      # 配置文件目录
│   ├── api/                         # API路由模块
│   └── utils/                       # 工具函数模块
│
├── env/                             # Python虚拟环境
│   ├── bin/
│   ├── lib/
│   └── pyvenv.cfg
│
├── logs/                            # 日志文件目录
├── docs/                            # 文档目录
│   ├── API.md                      # API文档
│   ├── DEPLOYMENT.md               # 部署文档
│   └── TROUBLESHOOTING.md          # 故障排除文档
│
└── scripts/                         # 脚本文件目录
    ├── start_services.sh           # 启动服务脚本
    ├── stop_services.sh            # 停止服务脚本
    └── install_dependencies.sh     # 依赖安装脚本
```

## 服务运行状态

### 后端服务 (Flask)

- **端口**: 5051
- **URL**: http://localhost:5051
- **状态**: ✅ 运行中
- **功能**:
  - MQTT 数据采集
  - AI 建议生成
  - REST API 服务
  - 环境数据处理

### 前端服务 (HTTP Server)

- **端口**: 8080
- **URL**: http://localhost:8080
- **状态**: ✅ 运行中
- **功能**:
  - 静态文件服务
  - 数据可视化界面
  - 实时监控面板

## 主要 API 端点

- `GET /api/status` - 服务状态检查
- `GET /api/data` - 获取环境数据
- `GET /api/ai-suggestion` - 获取 AI 健康建议

## 启动命令

### 启动后端服务

```bash
cd /Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard
source env/bin/activate
python3 mqtt_flask_server.py
```

### 启动前端服务

```bash
cd /Users/gaopeng/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard
python3 -m http.server 8080 --bind 0.0.0.0
```

## 局域网访问

前端页面可通过以下 URL 在局域网内访问：

- http://192.168.0.100:8080/index.html

## 注意事项

1. 确保 Python 虚拟环境已激活
2. 确保所需端口(5051, 8080)未被占用
3. MQTT 服务需要正确配置才能接收传感器数据
4. AI 功能需要有效的 API 密钥配置
