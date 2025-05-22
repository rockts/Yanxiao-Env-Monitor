# 智慧校园环境监测系统 - 启动指南

本文档提供了关于如何启动仪表盘的详细说明。

## 快速启动方法

### 方法 1: 双击启动（推荐）

在 macOS 系统上，直接双击 `启动仪表盘.command` 文件即可启动仪表盘。

### 方法 2: 使用优化启动器

```bash
python3 launch_dashboard.py
```

这个方法使用了我们优化过的启动脚本，它会：

1. 自动检查并修复配置文件
2. 处理 macOS 上的 GUI 启动问题
3. 提供详细的错误诊断信息

### 方法 3: 使用简化版仪表盘

```bash
python3 run_simple_dashboard.py
```

这个方法直接启动简化版仪表盘。

### 方法 4: 使用 macOS 专用启动脚本

```bash
./run_dashboard_macos.sh
```

这个脚本专为 macOS 设计，使用 AppleScript 确保 GUI 能够正确显示。

## 常见问题解决

### 1. 仪表盘窗口未显示

如果您运行了启动脚本但没有看到仪表盘窗口，请尝试：

- 在 macOS 上，使用 `./run_dashboard_macos.sh` 或双击 `启动仪表盘.command`
- 检查终端输出是否有错误信息
- 修复配置文件: `python3 fix_config.py`

### 2. MQTT 连接错误

如果仪表盘报告无法连接到 MQTT 服务器：

- 这是正常现象，仪表盘会自动切换到模拟数据模式
- 如果需要真实数据，请确保本地 MQTT 服务器正在运行

### 3. 配置文件错误

如果遇到配置相关错误：

```bash
python3 fix_config.py
```

这个脚本会自动修复配置文件问题。

## 文件说明

- `launch_dashboard.py`: 优化版启动脚本，具有更好的错误处理和兼容性
- `run_simple_dashboard.py`: 简化版仪表盘启动脚本
- `run_dashboard_macos.sh`: macOS 专用启动脚本
- `启动仪表盘.command`: macOS 用户友好的双击启动文件
- `fix_config.py`: 配置文件修复工具

## 技术细节

我们解决了以下技术问题：

1. **导入错误**: 修复了 `from src.ui.dashboard import Dashboard` 的错误，正确导入 `SimpleDashboard` 类
2. **配置加载**: 确保配置文件存在且包含所有必要参数
3. **macOS GUI 显示**: 使用 AppleScript 解决了 macOS 上 tkinter 窗口不显示的问题
4. **错误处理**: 添加了详细的错误诊断和报告机制
