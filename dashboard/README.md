# 烟铺小学智慧环境监测物联网系统

## 项目简介

本项目为烟铺小学定制的智慧环境监测物联网系统，集成了室内外环境数据采集、可视化展示、AI 健康建议、校园监控等功能，助力校园环境智能管理与健康守护。

## 主要功能

- **环境数据监测**：实时采集并展示室内外温度、湿度、空气质量（AQI、PM2.5）、eCO₂、TVOC、紫外线、噪音等多项环境指标。
- **数据可视化**：美观的仪表盘与折线图，动态反映环境变化趋势，y 轴自适应且曲线平滑。
- **AI 健康建议**：基于实时环境数据，自动生成“室内 AI 建议”和“室外 AI 建议”，内容智能分支，贴合实际温度和校园场景。
- **校园监控**：支持图片快照和流媒体监控，自动刷新，提升实时性。
- **系统美化**：现代化 UI 设计，信息分区清晰，适配校园大屏展示。

## 技术架构

- **前端**：Vue3 + ECharts + Element Plus，单页应用，所有逻辑集中于 `index.html`。
- **后端**：Flask + paho-mqtt，负责 MQTT 数据采集、AI 建议生成（接入通义千问-Turbo 大模型）、API 服务。
- **数据源**：本地 MQTT 传感器、OpenWeather 天气与空气质量 API。

## 目录结构

```
dashboard/
├── README.md                           # 项目说明文档
├── PROJECT_STRUCTURE.md              # 项目结构详细说明
├── requirements.txt                   # Python依赖文件
├── mqtt_flask_server.py              # 后端Flask服务主文件
├── index.html                        # 主要前端页面
│
├── frontend/                          # 前端文件目录
│   ├── debug.html                    # 调试页面
│   ├── index_simple.html            # 简化版前端页面
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
├── scripts/                          # 管理脚本目录
│   ├── start_services.sh            # 启动服务脚本
│   ├── stop_services.sh             # 停止服务脚本
│   ├── check_status.sh              # 状态检查脚本
│   └── install_dependencies.sh      # 依赖安装脚本
│
├── logs/                            # 日志文件目录
│   ├── backend.log                  # 后端服务日志
│   └── frontend.log                 # 前端服务日志
│
└── env/                             # Python虚拟环境
    ├── bin/
    ├── lib/
    └── pyvenv.cfg
```

## 快速启动

1. **安装依赖**（建议使用 Python 3.8+，已集成 Flask、paho-mqtt、requests、markdown 等）：
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install flask flask-cors paho-mqtt requests markdown
   ```
2. **启动后端服务**（务必用 python3，避免 alias 问题）：
   ```bash
   python3 mqtt_flask_server.py
   ```
   默认监听 5051 端口。
3. **打开前端页面**：
   - 直接用浏览器打开 `index.html`，推荐 Chrome/Edge。
   - 或使用本地静态服务器（推荐，避免部分浏览器跨域限制）：
     ```bash
     # 任选其一
     python3 -m http.server 8080 --bind 0.0.0.0
     # 局域网访问：在其他电脑浏览器输入 http://你的本机IP:8080/index.html
     # 例如 http://192.168.1.100:8080/index.html
     # 或
     npx serve .
     # 或
     npm install -g http-server && http-server -p 8080
     ```
   - 然后浏览器访问：http://localhost:8080/index.html

## 局域网访问配置

为了让局域网内其他设备能够访问系统，需要进行以下配置：

1. **启动前端服务（绑定到所有网卡）**：

   ```bash
   python3 -m http.server 8080 --bind 0.0.0.0
   ```

2. **确保后端服务监听所有接口**（代码已配置）：

   - 后端服务已配置为 `host="0.0.0.0"`，可接受来自任何 IP 的连接

3. **防火墙配置**：

   - 确保防火墙允许 8080 和 5051 端口的入站连接
   - macOS 用户可能需要在"系统偏好设置 > 安全性与隐私 > 防火墙"中允许 Python 应用

4. **局域网访问方式**：

   - 前端页面：`http://你的本机IP:8080`（例如：http://192.168.1.135:8080）
   - 系统会自动检测访问来源，适配正确的后端 API 地址

5. **IP 地址获取**：
   ```bash
   # 查看本机IP地址
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

### 局域网访问示例

- 假设服务器 IP 为 192.168.1.135
- 前端访问地址：http://192.168.1.135:8080
- 后端 API 地址：http://192.168.1.135:5051（自动配置）

### 智能地址适配

系统具备智能地址适配功能：

- 通过 localhost 访问时，API 请求发送到 localhost:5051
- 通过 IP 地址访问时，API 请求自动发送到相同 IP 的 5051 端口
- 支持 URL 参数指定服务器：`?server=192.168.1.100`

## 主要亮点

- **AI 建议智能分支**：后端 prompt 已优化，能根据温度等数值智能判断，避免模板化建议。
- **数据链路健壮**：接口异常自动兜底，前端展示不出错。
- **视觉统一**：卡片、仪表盘、图表、AI 建议区风格一致，适合校园场景。
- **易扩展**：支持更多环境指标、监控类型、AI 能力扩展。

## 版本信息

- 版本号：v1.1.0
- 更新时间：2025-06-05
- 更新内容：增加局域网访问支持，优化前端 API 地址自动适配

---

如需定制或技术支持，请联系开发者。
