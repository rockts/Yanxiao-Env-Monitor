#!/bin/bash

# 智慧校园仪表盘项目整理脚本
# 用于组织文件夹结构，使项目更加清晰

# 确保在脚本所在目录执行
cd "$(dirname "$0")"
BASE_DIR=$(pwd)

echo "智慧校园仪表盘项目整理工具"
echo "===================="
echo "当前工作目录: $BASE_DIR"
echo

# 创建必要的子文件夹
echo "创建必要的文件夹结构..."
mkdir -p src     # 存放主要源代码
mkdir -p utils   # 存放工具和辅助脚本
mkdir -p scripts # 存放启动脚本
mkdir -p config  # 存放配置文件
mkdir -p docs    # 存放文档
mkdir -p backup  # 存放备份文件

# 移动主要源代码文件到src目录
echo "整理主要源代码文件..."
mv main_all_fixed_optimized.py src/main.py
mv mqtt_bridge.py src/
mv mqtt_relay.py src/
mv simple_mqtt_broker.py src/
mv send_test_data.py src/
mv send_video_test.py src/

# 复制配置文件到config目录
echo "整理配置文件..."
cp config.json config/
cp python_config.env config/

# 移动备份和旧版本到backup目录
echo "移动备份文件..."
mv main_all_fixed.py backup/
mv main_all_fixed_new.py backup/
mv main.py backup/

# 移动启动脚本到scripts目录
echo "整理启动脚本..."
for script in start_*.command run_*.command setup_*.sh update_*.sh
do
  if [ -f "$script" ]; then
    mv "$script" scripts/
  fi
done

# 整理文档
echo "整理文档..."
mv README*.md docs/

# 创建更简洁的启动脚本
echo "创建简洁的启动脚本..."
cat <<EOF > start.command
#!/bin/bash

# 简洁的启动脚本
cd "\$(dirname "\$0")"
cd src && python3 main.py
EOF
chmod +x start.command

cat <<EOF > start_test.command
#!/bin/bash

# 带测试数据的启动脚本
cd "\$(dirname "\$0")"
SCRIPT_DIR="\$(pwd)"

# 启动MQTT代理
cd src
python3 simple_mqtt_broker.py &
BROKER_PID=\$!
sleep 1

# 启动传感器测试数据
python3 send_test_data.py --local &
DATA_PID=\$!

# 启动视频测试数据
python3 send_video_test.py --fps 3 &
VIDEO_PID=\$!

# 启动主程序
python3 main.py

# 清理进程
kill \$BROKER_PID \$DATA_PID \$VIDEO_PID 2>/dev/null
EOF
chmod +x start_test.command

echo
echo "项目整理完成！"
echo "现在可以使用:"
echo "- './start.command' 启动基本仪表盘"
echo "- './start_test.command' 启动带测试数据的仪表盘"
echo
