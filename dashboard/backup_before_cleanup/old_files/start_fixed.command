#!/bin/bash

# 智慧校园仪表盘启动脚本

# 确保当前目录为脚本所在目录
cd "$(dirname "$0")"

# 设置Python路径（如果需要）
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 输出诊断信息
echo "=== 启动智慧校园仪表盘 ==="
echo "当前目录: $(pwd)"
echo "Python 版本: $(python3 --version)"

# 启动主程序
echo "启动主程序..."
cd src
python3 main.py

# 程序结束
echo "程序已退出，按任意键关闭窗口..."
read -n 1
