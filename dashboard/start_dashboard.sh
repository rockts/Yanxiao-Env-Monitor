#!/bin/bash
# 智慧校园环境监测系统 - 启动脚本
cd "$(dirname "$0")"
source ../.venv/bin/activate
python dashboard.py
