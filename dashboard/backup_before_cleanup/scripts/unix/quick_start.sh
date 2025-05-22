#!/bin/bash

# 智慧校园环境监测系统 - 快速启动脚本
# 此脚本解决了VS Code终端无法显示GUI窗口的问题

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# 设置Python路径
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

echo "智慧校园环境监测系统 启动中..."
echo "项目路径: $PROJECT_ROOT"

# 检查是否在VS Code终端中运行
if [ -n "$VSCODE_GIT_IPC_HANDLE" ] || [ "$TERM_PROGRAM" = "vscode" ]; then
    echo "检测到VS Code终端环境，将使用外部终端启动..."
    
    # 创建临时启动脚本
    TEMP_SCRIPT="$PROJECT_ROOT/temp_vscode_launch.sh"
    
    cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
cd "$PROJECT_ROOT"
python3 "$PROJECT_ROOT/run_simple_dashboard.py"
echo "程序已退出，按任意键关闭窗口..."
read -n 1
EOF
    
    # 添加执行权限
    chmod +x "$TEMP_SCRIPT"
    
    # 使用open命令在Terminal中运行脚本
    open -a Terminal "$TEMP_SCRIPT"
    
    echo "已在外部Terminal中启动仪表盘。"
    echo "如果窗口没有出现，请手动执行: python3 $PROJECT_ROOT/run_simple_dashboard.py"
else
    # 在普通终端中直接运行Python脚本
    echo "在普通终端环境中，直接启动仪表盘..."
    python3 "$PROJECT_ROOT/run_simple_dashboard.py"
fi
