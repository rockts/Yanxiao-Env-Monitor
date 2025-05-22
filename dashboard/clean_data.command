#!/bin/bash
# 智慧校园环境监测系统 - 数据清理快捷脚本
# 版本: 1.0
# 日期: 2025-05-22

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 调用实际的清理脚本
./scripts/clean_data.sh "$@"

# 脚本结束提示
echo ""
echo "快捷方式: clean_data.command"

# 显示标题
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}     烟铺小学智慧校园环境监测系统 - 数据清理     ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 首选命令顺序：python3, python
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version)
        echo -e "${GREEN}[成功]${NC} 找到 $version"
        PYTHON_CMD=$cmd
        break
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

# 默认保留7天的数据
DAYS=7

# 解析参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --days) DAYS="$2"; shift ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
    shift
done

echo -e "${YELLOW}[信息]${NC} 将清理 ${DAYS} 天之前的数据..."
echo -e "${YELLOW}[信息]${NC} 数据将备份到各目录的backup文件夹中"
echo ""

# 运行清理工具
$PYTHON_CMD src/data_cleaner.py --days $DAYS

echo ""
echo -e "${GREEN}[完成]${NC} 数据清理完成"
read -p "按回车键退出..."
