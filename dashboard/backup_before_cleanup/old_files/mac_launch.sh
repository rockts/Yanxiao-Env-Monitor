#!/bin/bash

# 最简单的仪表盘启动脚本 - VS Code专用
# 此脚本会直接调用open命令在Terminal中启动应用

# 获取脚本所在绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_SCRIPT="$SCRIPT_DIR/run_simple_dashboard.py"

# 确保Python脚本可执行
chmod +x "$APP_SCRIPT"

# 输出启动信息
echo "===== 智慧校园环境监测系统 ====="
echo "正在打开系统Terminal运行仪表盘..."

# 在新的Terminal窗口中运行Python脚本
# 使用绝对路径避免路径问题
osascript -e "
tell application \"Terminal\"
    do script \"cd \\\"$SCRIPT_DIR\\\" && python3 \\\"$APP_SCRIPT\\\" && echo \\\"\\nPress any key to exit...\\\" && read -n 1\"
    activate
end tell
"

echo "已启动环境监测系统，请查看新打开的Terminal窗口"
