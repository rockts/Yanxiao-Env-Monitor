#!/bin/zsh

# 简洁的启动脚本 - 改进版

# 确定脚本所在目录
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "====== 智慧校园仪表盘启动 ======"
echo "当前工作目录: $SCRIPT_DIR"
echo "启动仪表盘主程序..."

# 切换到src目录并启动主程序
cd "$SCRIPT_DIR/src" && python3 main.py

echo "仪表盘已关闭"
