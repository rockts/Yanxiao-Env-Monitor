#!/bin/bash
# 智慧校园环境监测系统 - 最终文件整理脚本
# 此脚本用于完成项目的最终整理工作

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   智慧校园环境监测系统 - 最终文件整理脚本   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# 1. 移动根目录中的Python脚本
echo -e "${YELLOW}步骤1: 整理根目录中的Python脚本...${NC}"

# 保留在根目录的关键Python文件
keep_files=("launch.py" "easy_start.py" "smart_launcher.py" "run_simple_dashboard.py")

# 检查并移动其他Python文件
echo -e "${YELLOW}检查Python文件...${NC}"
find "$PROJECT_ROOT" -maxdepth 1 -name "*.py" | while read py_file; do
    base_name=$(basename "$py_file")
    # 检查此文件是否应保留
    should_keep=false
    for keep in "${keep_files[@]}"; do
        if [ "$base_name" = "$keep" ]; then
            should_keep=true
            break
        fi
    done
    
    if [ "$should_keep" = false ]; then
        echo -e "  - 移动: $base_name 到 backup/"
        mv "$py_file" "$PROJECT_ROOT/backup/" 2>/dev/null
    else
        echo -e "  ${GREEN}✓ 保留: $base_name${NC}"
    fi
done

# 2. 整理配置文件
echo -e "${YELLOW}步骤2: 确保所有配置文件在config目录...${NC}"
find "$PROJECT_ROOT" -maxdepth 1 -name "*.json" | while read json_file; do
    base_name=$(basename "$json_file")
    echo -e "  - 移动: $base_name 到 config/"
    cp "$json_file" "$PROJECT_ROOT/config/" 2>/dev/null
    mv "$json_file" "$PROJECT_ROOT/old_files/" 2>/dev/null
done
echo -e "${GREEN}✓ 已处理配置文件${NC}"

# 3. 整理日志文件
echo -e "${YELLOW}步骤3: 整理日志文件...${NC}"
find "$PROJECT_ROOT" -maxdepth 1 -name "*.log" | while read log_file; do
    base_name=$(basename "$log_file")
    echo -e "  - 移动: $base_name 到 logs/"
    mv "$log_file" "$PROJECT_ROOT/logs/" 2>/dev/null
done
echo -e "${GREEN}✓ 已处理日志文件${NC}"

# 4. 移动临时文件和调试输出
echo -e "${YELLOW}步骤4: 处理临时文件和调试输出...${NC}"
find "$PROJECT_ROOT" -maxdepth 1 -name "*_started.txt" -o -name "*.tmp" -o -name "*_output.txt" | while read tmp_file; do
    base_name=$(basename "$tmp_file")
    echo -e "  - 移动: $base_name 到 old_files/"
    mv "$tmp_file" "$PROJECT_ROOT/old_files/" 2>/dev/null
done
echo -e "${GREEN}✓ 已处理临时文件${NC}"

# 5. 整理src目录中的冗余文件
echo -e "${YELLOW}步骤5: 整理src目录中的冗余文件...${NC}"
# 检查旧的配置管理器、日志管理器等文件是否仍在src根目录
src_files_to_check=("config_manager.py" "log_manager.py" "simple_dashboard.py" "mqtt_bridge_service.py" "mqtt_relay_service.py" "simple_mqtt_broker.py" "sensor_data_simulator.py" "video_stream_simulator.py")

for file in "${src_files_to_check[@]}"; do
    if [ -f "$PROJECT_ROOT/src/$file" ]; then
        # 确定目标目录
        target_dir=""
        case $file in
            "config_manager.py"|"log_manager.py")
                target_dir="$PROJECT_ROOT/src/core"
                ;;
            "simple_dashboard.py")
                target_dir="$PROJECT_ROOT/src/ui"
                ;;
            "mqtt_bridge_service.py"|"mqtt_relay_service.py"|"simple_mqtt_broker.py")
                target_dir="$PROJECT_ROOT/src/services"
                ;;
            "sensor_data_simulator.py"|"video_stream_simulator.py")
                target_dir="$PROJECT_ROOT/src/simulators"
                ;;
        esac
        
        if [ -n "$target_dir" ]; then
            echo -e "  - 移动: src/$file 到 $target_dir/"
            # 检查目标文件是否已存在
            if [ -f "$target_dir/$file" ]; then
                echo -e "    ${YELLOW}目标文件已存在，将源文件备份${NC}"
                mv "$PROJECT_ROOT/src/$file" "$PROJECT_ROOT/backup/src_$file" 2>/dev/null
            else
                cp "$PROJECT_ROOT/src/$file" "$target_dir/" 2>/dev/null
                mv "$PROJECT_ROOT/src/$file" "$PROJECT_ROOT/backup/src_$file" 2>/dev/null
            fi
        fi
    fi
done
echo -e "${GREEN}✓ 已整理src目录${NC}"

# 6. 确保关键脚本有执行权限
echo -e "${YELLOW}步骤6: 设置关键脚本的执行权限...${NC}"
chmod +x "$PROJECT_ROOT/launch.py" 2>/dev/null
chmod +x "$PROJECT_ROOT/easy_start.py" 2>/dev/null
chmod +x "$PROJECT_ROOT/smart_launcher.py" 2>/dev/null
chmod +x "$PROJECT_ROOT/run_simple_dashboard.py" 2>/dev/null
chmod +x "$PROJECT_ROOT/scripts/unix/"*.sh 2>/dev/null
chmod +x "$PROJECT_ROOT/scripts/unix/"*.command 2>/dev/null
echo -e "${GREEN}✓ 已设置执行权限${NC}"

echo
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}   文件整理完成!   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo -e "${YELLOW}注意:${NC}"
echo -e "${YELLOW}1. 冗余文件已移动到backup目录${NC}"
echo -e "${YELLOW}2. 项目结构已完全整理${NC}"
echo -e "${YELLOW}3. 请使用以下启动方式:${NC}"
echo -e "${YELLOW}   - ./launch.py [选项]${NC}"
echo -e "${YELLOW}   - ./easy_start.py${NC}"
echo -e "${YELLOW}   - python3 ./src/main_dashboard.py${NC}"
echo
