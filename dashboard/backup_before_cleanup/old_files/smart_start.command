#!/bin/bash
# 智慧校园环境监测系统 - 统一启动脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

clear
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}     智慧校园环境监测系统 - 选择启动模式       ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# 显示选项
echo -e "请选择要启动的组件:"
echo
echo -e "1. ${GREEN}Python仪表盘${NC} (数据处理与MQTT通信)"
echo -e "2. ${GREEN}Mind+大屏${NC} (数据可视化展示)"
echo -e "3. ${GREEN}全部组件${NC} (先启动Python仪表盘，然后提示打开Mind+)"
echo -e "4. ${YELLOW}退出${NC}"
echo
echo -n "请输入选择 [1-4]: "
read choice

case $choice in
    1)
        echo
        echo -e "${BLUE}启动Python仪表盘...${NC}"
        ./launch.py
        ;;
    2)
        echo
        echo -e "${BLUE}准备打开Mind+大屏文件...${NC}"
        echo -e "${YELLOW}请手动启动Mind+软件，然后打开以下文件:${NC}"
        echo -e "${CYAN}$SCRIPT_DIR/data/烟小智慧环境监测物联网大屏.mpdb${NC}"
        echo
        echo -e "是否要尝试自动打开此文件? (y/n): "
        read auto_open
        if [[ "$auto_open" == "y" || "$auto_open" == "Y" ]]; then
            # 尝试打开文件 - 这取决于系统设置是否将.mpdb关联到Mind+
            open "$SCRIPT_DIR/data/烟小智慧环境监测物联网大屏.mpdb"
        fi
        ;;
    3)
        echo
        echo -e "${BLUE}启动Python仪表盘...${NC}"
        ./launch.py --background &
        
        echo
        echo -e "${BLUE}准备打开Mind+大屏文件...${NC}"
        echo -e "${YELLOW}请手动启动Mind+软件，然后打开以下文件:${NC}"
        echo -e "${CYAN}$SCRIPT_DIR/data/烟小智慧环境监测物联网大屏.mpdb${NC}"
        echo
        echo -e "是否要尝试自动打开此文件? (y/n): "
        read auto_open
        if [[ "$auto_open" == "y" || "$auto_open" == "Y" ]]; then
            # 尝试打开文件
            open "$SCRIPT_DIR/data/烟小智慧环境监测物联网大屏.mpdb"
        fi
        ;;
    4)
        echo
        echo -e "${YELLOW}退出程序.${NC}"
        exit 0
        ;;
    *)
        echo
        echo -e "${RED}无效的选择.${NC}"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}操作完成.${NC}"
echo "按任意键退出..."
read -n 1
