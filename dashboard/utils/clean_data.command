#!/usr/bin/env bash
# 智慧校园环境监测系统 - 数据清理启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 数据清理     ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 检查Python版本
echo -e "${BLUE}[信息]${NC} 检查Python环境..."

# 首选命令顺序：python3, python
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version)
        echo -e "${GREEN}[成功]${NC} 找到 $version"
        
        # 检查是Python 3
        if [[ $version == *"Python 3"* ]]; then
            PYTHON_CMD=$cmd
            break
        else
            echo -e "${YELLOW}[警告]${NC} 检测到Python 2，尝试寻找Python 3..."
        fi
    fi
done

# 如果没有找到任何Python
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[错误]${NC} 未找到Python 3。请安装Python 3后再试。"
    echo -e "可以从 https://www.python.org/downloads/ 下载安装"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 运行清理脚本
echo -e "${BLUE}[信息]${NC} 运行数据清理工具..."

# 询问用户是否需要自定义清理选项
echo -e "${YELLOW}[询问]${NC} 是否需要自定义清理选项? (y/n) [默认: n]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # 询问保留多少天的传感器日志
    echo -e "${BLUE}[配置]${NC} 保留多少天的传感器数据日志? [默认: 7]"
    read -r sensor_days
    sensor_days=${sensor_days:-7}
    
    # 询问保留多少天的应用程序日志
    echo -e "${BLUE}[配置]${NC} 保留多少天的应用程序日志? [默认: 30]"
    read -r app_days
    app_days=${app_days:-30}
    
    # 启动清理程序
    $PYTHON_CMD utils/clean_data.py --sensor-days $sensor_days --app-days $app_days
else
    # 使用默认选项
    $PYTHON_CMD utils/clean_data.py
fi

# 如果程序意外终止，等待用户确认
echo ""
echo -e "${GREEN}[信息]${NC} 数据清理已完成"
read -p "按回车键退出..."
