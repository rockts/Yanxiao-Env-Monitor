#!/bin/bash

# 烟铺小学智慧校园环境监测系统 - VS Code命令文件启动器
# 此文件专为VS Code设计，会自动在macOS Terminal中启动应用

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "===== 环境监测系统启动程序 ====="
echo "项目路径: $PROJECT_ROOT"

# 创建临时启动脚本
TEMP_SCRIPT="$PROJECT_ROOT/temp_vscode_launch.command"

cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
cd "$PROJECT_ROOT"
echo "===== 智慧校园环境监测系统 ====="
echo "正在启动仪表盘..."
python3 "$PROJECT_ROOT/run_simple_dashboard.py"
echo "程序已退出，按回车键关闭窗口..."
read
EOF

# 添加执行权限
chmod +x "$TEMP_SCRIPT"

# 使用macOS的open命令运行命令文件
echo "正在打开系统Terminal运行仪表盘..."
open "$TEMP_SCRIPT"

echo "已启动环境监测系统，请查看新打开的Terminal窗口"
