#!/usr/bin/env bash
# 智慧校园环境监测系统 - 智能启动脚本
# 提供用户选择启动哪个版本的仪表盘

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 清屏
clear

echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 启动向导     ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo ""
echo -e "${BLUE}请选择要启动的仪表盘版本:${NC}"
echo ""
echo -e "${GREEN}1) 完整版${NC} - 包含所有功能，带视频监控和数据记录"
echo -e "${GREEN}2) 简单版${NC} - 基础功能，适合性能较弱的设备"
echo -e "${GREEN}3) 清理数据${NC} - 清理旧的日志和数据文件"
echo -e "${GREEN}4) 退出${NC}"
echo ""

# 检查文件是否存在
if [ ! -f "full_dashboard_new.py" ]; then
    echo -e "${RED}[错误]${NC} 找不到完整版仪表盘文件 (full_dashboard_new.py)"
    echo -e "${RED}[错误]${NC} 请确保文件完整性"
    read -p "按回车键继续..."
    exit 1
fi

if [ ! -f "simple_working_dashboard.py" ]; then
    echo -e "${RED}[错误]${NC} 找不到简单版仪表盘文件 (simple_working_dashboard.py)"
    echo -e "${RED}[错误]${NC} 请确保文件完整性"
    read -p "按回车键继续..."
    exit 1
fi

# 获取用户选择
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo -e "${BLUE}[信息]${NC} 启动完整版仪表盘..."
        if [ -f "run_full_dashboard.command" ]; then
            ./run_full_dashboard.command
        else
            # 检查Python版本
            for cmd in python3 python; do
                if command -v $cmd &> /dev/null; then
                    version=$($cmd --version)
                    if [[ $version == *"Python 3"* ]]; then
                        PYTHON_CMD=$cmd
                        break
                    fi
                fi
            done
            
            if [ -z "$PYTHON_CMD" ]; then
                echo -e "${RED}[错误]${NC} 未找到Python 3"
                read -p "按回车键退出..."
                exit 1
            fi
            
            $PYTHON_CMD full_dashboard_new.py
        fi
        ;;
    2)
        echo -e "${BLUE}[信息]${NC} 启动简单版仪表盘..."
        if [ -f "simple_working_dashboard.command" ]; then
            ./simple_working_dashboard.command
        else
            # 检查Python版本
            for cmd in python3 python; do
                if command -v $cmd &> /dev/null; then
                    version=$($cmd --version)
                    if [[ $version == *"Python 3"* ]]; then
                        PYTHON_CMD=$cmd
                        break
                    fi
                fi
            done
            
            if [ -z "$PYTHON_CMD" ]; then
                echo -e "${RED}[错误]${NC} 未找到Python 3"
                read -p "按回车键退出..."
                exit 1
            fi
            
            $PYTHON_CMD simple_working_dashboard.py
        fi
        ;;
    3)
        echo -e "${BLUE}[信息]${NC} 启动数据清理工具..."
        if [ -f "utils/clean_data.command" ]; then
            ./utils/clean_data.command
        else
            echo -e "${RED}[错误]${NC} 找不到数据清理工具"
            read -p "按回车键继续..."
        fi
        ;;
    4)
        echo -e "${BLUE}[信息]${NC} 退出程序"
        exit 0
        ;;
    *)
        echo -e "${RED}[错误]${NC} 无效的选项"
        read -p "按回车键继续..."
        exit 1
        ;;
esac
