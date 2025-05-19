@echo off
:: 智慧校园仪表盘 Windows 启动脚本
:: 此脚本会自动检测并使用正确的Python版本

echo ============================================
echo    烟铺小学智慧校园仪表盘启动程序
echo ============================================
echo.

:: 确定要使用的Python解释器
set PYTHON_CMD=

:: 检查是否有配置文件
if exist python_config.txt (
    echo 尝试加载已保存的Python配置...
    for /f "tokens=1,* delims==" %%a in (python_config.txt) do (
        if "%%a"=="PYTHON_PATH" set PYTHON_CMD=%%b
    )
    
    if defined PYTHON_CMD (
        echo 使用已配置的Python解释器: %PYTHON_CMD%
    ) else (
        echo 无效的Python配置文件，将重新检测Python...
    )
)

:: 如果没有有效配置，尝试找到Python
if not defined PYTHON_CMD (
    :: 尝试python3命令
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3
    ) else (
        :: 尝试python命令并检查版本
        where python >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=python
            
            :: 验证Python版本是否为3.x
            for /f "tokens=2 delims=." %%a in ('python -c "import sys; print(sys.version)" 2^>^&1') do (
                if not "%%a"=="3" (
                    echo 警告: 系统默认的Python版本不是Python 3.x
                    echo 请安装Python 3并确保可以通过'python'命令访问
                    echo.
                    echo 按任意键退出...
                    pause >nul
                    exit /b 1
                )
            )
        ) else (
            echo 错误: 未找到Python.
            echo 请安装Python 3后再试.
            echo 访问 https://www.python.org/downloads/ 下载安装Python 3
            echo.
            echo 按任意键退出...
            pause >nul
            exit /b 1
        )
    )
)

:: 显示Python版本
%PYTHON_CMD% --version
echo.

:: 保存Python路径到配置文件
where %PYTHON_CMD% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%a in ('where %PYTHON_CMD%') do (
        echo PYTHON_PATH=%%a > python_config.txt
        echo # 此文件由启动脚本自动生成 - %DATE% %TIME% >> python_config.txt
    )
)

:: 检查并安装主要依赖
echo 检查依赖项...
set PACKAGES=tkinter paho.mqtt.client matplotlib PIL.Image

for %%p in (%PACKAGES%) do (
    python -c "import %%p" 2>NUL
    if %ERRORLEVEL% NEQ 0 (
        echo 正在安装 %%p...
        python -m pip install %%p
    ) else (
        echo ✓ %%p 已安装
    )
)

:: 设置MQTT默认配置
set MQTT_HOST=192.168.1.129
set MQTT_PORT=1883
set MQTT_USER=siot
set MQTT_PASS=dfrobot

:: 询问用户启动模式
echo.
echo 请选择启动模式:
echo 1) 仅启动仪表盘应用
echo 2) 仅启动测试数据发送器
echo 3) 同时启动仪表盘和测试数据发送器
echo.
set /p choice="请选择 [1-3] (默认: 3): "

if "%choice%"=="" set choice=3

if "%choice%"=="1" (
    echo 启动仪表盘应用...
    python main_all_fixed.py
) else if "%choice%"=="2" (
    echo 启动测试数据发送器...
    python send_test_data.py --host %MQTT_HOST% --port %MQTT_PORT% --username %MQTT_USER% --password %MQTT_PASS%
) else (
    echo 启动仪表盘应用...
    start python main_all_fixed.py

    timeout /t 2 > nul

    echo 启动测试数据发送器...
    start python send_test_data.py --host %MQTT_HOST% --port %MQTT_PORT% --username %MQTT_USER% --password %MQTT_PASS%

    echo 两个程序已成功启动!
    echo 请手动关闭各自程序窗口结束运行。
)

echo.
echo 程序已启动.
pause
