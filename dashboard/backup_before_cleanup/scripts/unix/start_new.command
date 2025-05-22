#!/bin/bash
# 智慧校园环境监测系统 - 新版启动指南

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # 无颜色

clear
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}     智慧校园环境监测系统 - 新版启动指南       ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo -e "${CYAN}项目已完成重构，现在有多种启动方式:${NC}"
echo
echo -e "1. ${GREEN}使用统一启动器:${NC}"
echo -e "   ${YELLOW}./launch.py${NC} [选项]"
echo
echo -e "   可用选项:"
echo -e "   ${BLUE}--simple${NC}     - 启动简化版仪表盘"
echo -e "   ${BLUE}--debug${NC}      - 启动调试模式"
echo -e "   ${BLUE}--local-mqtt${NC} - 使用本地MQTT服务"
echo -e "   ${BLUE}--simulate${NC}   - 启用传感器数据模拟"
echo -e "   ${BLUE}--video${NC}      - 启用视频流模拟"
echo
echo -e "2. ${GREEN}使用脚本启动:${NC}"
echo -e "   ${YELLOW}./scripts/unix/start_dashboard.command${NC}"
echo
echo -e "3. ${GREEN}直接启动主程序:${NC}"
echo -e "   ${YELLOW}python3 src/main_dashboard.py${NC}"
echo
echo -e "${RED}注意: 旧的启动脚本已移至scripts目录，但仍然可用${NC}"
echo
echo -e "${CYAN}详细信息请参阅 README.md 文件${NC}"
echo
echo -e "${BLUE}===============================================${NC}"

echo
echo "按任意键启动应用(使用默认选项)..."
read -n 1

# 执行新的启动器
python3 launch.py
