#!/bin/bash
# 智慧校园环境监测系统 - 统一启动脚本
# 针对macOS系统优化的启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 启动向导      ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo

# 检测Python
PYTHON_CMD=$(command -v python3)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}错误: 找不到Python 3。${NC}"
    echo -e "${YELLOW}请安装Python 3后再试。${NC}"
    read -p "按回车键退出..."
    exit 1
fi

echo -e "${GREEN}Python 3已找到: $PYTHON_CMD${NC}"

# 检查是否存在图形界面启动器
if [ -f "智慧校园监测系统.py" ]; then
    # 查看是否有tkinter库
    $PYTHON_CMD -c "import tkinter" 2>/dev/null
    if [ $? -eq 0 ]; then
        # 有tkinter库，启动图形界面
        echo -e "${GREEN}启动图形界面向导...${NC}"
        
        # 使用AppleScript启动新终端运行Python程序
        osascript <<EOF
        tell application "Terminal"
            do script "cd '$SCRIPT_DIR' && '$PYTHON_CMD' '智慧校园监测系统.py'"
            set current settings of window 1 to settings set "Homebrew"
            set background color of window 1 to {0, 0, 0}
            set normal text color of window 1 to {50000, 50000, 50000}
            set the number of rows to 24
            set the number of columns to 80
            set the title of window 1 to "智慧校园环境监测系统"
        end tell
EOF
        echo -e "${GREEN}已在新窗口中启动图形界面向导${NC}"
    else
        # 没有tkinter库，显示命令行菜单
        echo -e "${YELLOW}警告: 未安装tkinter库，无法启动图形界面。${NC}"
        echo -e "${GREEN}使用命令行菜单...${NC}"
        echo
        echo "请选择要启动的组件:"
        echo "1) 启动真·完整版仪表盘"
        echo "2) 启动简化版仪表盘"
        echo "3) 运行系统诊断"
        echo "4) 安装必要的依赖"
        echo "5) 退出"
        echo
        read -p "请输入选项 [1-5]: " option
        
        case $option in
            1)
                echo -e "${GREEN}启动真·完整版仪表盘...${NC}"
                if [ -f "真完整版启动.command" ]; then
                    osascript -e 'tell application "Terminal" to do script "cd \"'$SCRIPT_DIR'\" && ./真完整版启动.command"'
                else
                    $PYTHON_CMD 真完整版启动.py
                fi
                ;;
            2)
                echo -e "${GREEN}启动简化版仪表盘...${NC}"
                $PYTHON_CMD 超级简单版仪表盘.py
                ;;
            3)
                echo -e "${GREEN}运行系统诊断...${NC}"
                if [ -f "仪表盘诊断.command" ]; then
                    osascript -e 'tell application "Terminal" to do script "cd \"'$SCRIPT_DIR'\" && ./仪表盘诊断.command"'
                else
                    $PYTHON_CMD 仪表盘诊断.py
                fi
                ;;
            4)
                echo -e "${GREEN}安装必要的依赖...${NC}"
                $PYTHON_CMD -m pip install paho-mqtt matplotlib pillow tkinter
                echo -e "${GREEN}依赖安装完成，请重新运行此脚本。${NC}"
                read -p "按回车键继续..."
                ;;
            5)
                echo -e "${GREEN}谢谢使用，再见！${NC}"
                ;;
            *)
                echo -e "${RED}无效的选项，请重新运行脚本并选择有效的选项。${NC}"
                ;;
        esac
    fi
else
    # 没有图形界面启动器，显示命令行菜单
    echo -e "${YELLOW}警告: 找不到图形界面启动器。${NC}"
    echo -e "${GREEN}使用命令行菜单...${NC}"
    echo
    echo "请选择要启动的组件:"
    echo "1) 启动真·完整版仪表盘"
    echo "2) 启动简化版仪表盘"
    echo "3) 运行系统诊断"
    echo "4) 安装必要的依赖"
    echo "5) 退出"
    echo
    read -p "请输入选项 [1-5]: " option
    
    case $option in
        1)
            echo -e "${GREEN}启动真·完整版仪表盘...${NC}"
            if [ -f "真完整版启动.command" ]; then
                osascript -e 'tell application "Terminal" to do script "cd \"'$SCRIPT_DIR'\" && ./真完整版启动.command"'
            else
                $PYTHON_CMD 真完整版启动.py
            fi
            ;;
        2)
            echo -e "${GREEN}启动简化版仪表盘...${NC}"
            $PYTHON_CMD 超级简单版仪表盘.py
            ;;
        3)
            echo -e "${GREEN}运行系统诊断...${NC}"
            if [ -f "仪表盘诊断.command" ]; then
                osascript -e 'tell application "Terminal" to do script "cd \"'$SCRIPT_DIR'\" && ./仪表盘诊断.command"'
            else
                $PYTHON_CMD 仪表盘诊断.py
            fi
            ;;
        4)
            echo -e "${GREEN}安装必要的依赖...${NC}"
            $PYTHON_CMD -m pip install paho-mqtt matplotlib pillow tkinter
            echo -e "${GREEN}依赖安装完成，请重新运行此脚本。${NC}"
            read -p "按回车键继续..."
            ;;
        5)
            echo -e "${GREEN}谢谢使用，再见！${NC}"
            ;;
        *)
            echo -e "${RED}无效的选项，请重新运行脚本并选择有效的选项。${NC}"
            ;;
    esac
fi

echo
echo "如遇到任何问题，请运行系统诊断工具或查看使用说明.md文件"
echo "仪表盘启动器已在新窗口中启动，此窗口可以关闭"
read -p "按回车键关闭此窗口..."
