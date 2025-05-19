#!/bin/bash
# 保存Python解释器路径的配置文件

# 检查系统上Python 3的路径
PYTHON_PATH=$(which python3)

if [ -z "$PYTHON_PATH" ]; then
    # 如果找不到python3，尝试查找python
    PYTHON_PATH=$(which python)
    
    if [ -z "$PYTHON_PATH" ]; then
        echo "ERROR: 无法找到Python解释器!"
        exit 1
    fi
    
    # 验证是否为Python 3
    PY_VERSION=$($PYTHON_PATH -c "import sys; print(sys.version_info[0])")
    if [ "$PY_VERSION" != "3" ]; then
        echo "ERROR: 找到的Python不是Python 3！请安装Python 3。"
        exit 1
    fi
fi

# 保存Python路径到配置文件
echo "PYTHON_INTERPRETER=\"$PYTHON_PATH\"" > ./python_config.env
echo "# 此文件由setup_python.sh自动生成 - $(date)" >> ./python_config.env
echo "# 包含智慧校园仪表盘应用程序使用的Python解释器路径" >> ./python_config.env

echo "已成功配置Python解释器路径: $PYTHON_PATH"
echo "配置已保存到: python_config.env"
