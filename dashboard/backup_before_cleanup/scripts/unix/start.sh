#!/bin/bash

# 智慧校园环境监测系统 - 自动启动脚本
# 此脚本可以在VS Code中使用，会自动检测环境并使用合适的方式启动

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 调用Python智能启动器
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/smart_launcher.py"
