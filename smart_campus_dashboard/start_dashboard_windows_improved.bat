@echo off
:: 烟铺小学智慧校园仪表盘启动脚本（改进版）
:: 此脚本提供了更多的配置选项和错误处理功能

setlocal EnableDelayedExpansion

:: 设置标题和颜色
title 烟铺小学智慧校园仪表盘
color 0A

:: 清屏
cls
echo ============================================
echo    烟铺小学智慧校园仪表盘启动程序
echo ============================================
echo.

:: 定义配置文件
set CONFIG_FILE=dashboard_config.ini
set MAIN_APP=main_all_fixed.py
set TEST_DATA_APP=send_test_data.py

:: 默认配置
set MQTT_HOST=192.168.1.129
set MQTT_PORT=1883
set MQTT_USER=siot
set MQTT_PASS=dfrobot

:: 如果配置文件存在，则读取配置
if exist %CONFIG_FILE% (
    echo 读取配置文件...
    for /f "tokens=1,2 delims==" %%a in (%CONFIG_FILE%) do (
        if "%%a"=="MQTT_HOST" set MQTT_HOST=%%b
        if "%%a"=="MQTT_PORT" set MQTT_PORT=%%b
        if "%%a"=="MQTT_USER" set MQTT_USER=%%b
        if "%%a"=="MQTT_PASS" set MQTT_PASS=%%b
    )
)

:: 检查Python是否安装
echo 检查Python环境...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到Python。请安装Python 3后再试。
    echo 访问 https://www.python.org/downloads/ 下载安装Python 3
    goto end
)

:: 检查Python版本
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYVER=%%I
for /f "tokens=1 delims=." %%I in ('echo %PYVER%') do set PYMAJOR=%%I
if not "%PYMAJOR%"=="3" (
    echo [警告] 检测到Python %PYMAJOR%，不是Python 3
    echo 继续运行可能导致程序不正常工作
    echo.
    set /p CONTINUE="是否继续? (Y/N): "
    if /i not "!CONTINUE!"=="Y" goto end
)

:: 显示Python版本
echo 使用Python版本: %PYVER%
echo.

:: 检查主程序是否存在
if not exist %MAIN_APP% (
    echo [错误] 找不到主程序: %MAIN_APP%
    echo 请确保文件存在并且您在正确的目录中。
    goto end
)

:: 检查测试数据程序是否存在
if not exist %TEST_DATA_APP% (
    echo [警告] 找不到测试数据程序: %TEST_DATA_APP%
    echo 仅启动仪表盘模式可用。
    set NO_TEST=1
)

:: 检查并安装主要依赖
echo 检查依赖项...
set DEPS_OK=1
set PACKAGES=paho.mqtt.client matplotlib PIL.Image

for %%p in (%PACKAGES%) do (
    python -c "import %%p" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [警告] 缺少依赖: %%p
        set DEPS_OK=0
    ) else (
        echo ✓ %%p 已安装
    )
)

if %DEPS_OK%==0 (
    echo.
    echo 部分依赖项缺失。建议运行 update_dependencies.bat 安装依赖项。
    echo.
    set /p UPDATE="是否立即安装依赖? (Y/N): "
    if /i "!UPDATE!"=="Y" (
        call update_dependencies.bat
    )
)

:: 显示当前配置
echo.
echo 当前MQTT配置:
echo   服务器: %MQTT_HOST%
echo   端口:   %MQTT_PORT%
echo   用户名: %MQTT_USER%
echo.

:: 是否修改配置
set /p CONFIG="是否修改MQTT配置? (Y/N): "
if /i "%CONFIG%"=="Y" (
    set /p MQTT_HOST="MQTT服务器地址 [%MQTT_HOST%]: "
    set /p MQTT_PORT="MQTT端口 [%MQTT_PORT%]: "
    set /p MQTT_USER="MQTT用户名 [%MQTT_USER%]: "
    set /p MQTT_PASS="MQTT密码 [%MQTT_PASS%]: "
    
    :: 保存新配置
    echo 保存配置...
    echo MQTT_HOST=%MQTT_HOST%> %CONFIG_FILE%
    echo MQTT_PORT=%MQTT_PORT%>> %CONFIG_FILE%
    echo MQTT_USER=%MQTT_USER%>> %CONFIG_FILE%
    echo MQTT_PASS=%MQTT_PASS%>> %CONFIG_FILE%
)

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
    start "智慧校园仪表盘" /B python %MAIN_APP%
) else if "%choice%"=="2" (
    if defined NO_TEST (
        echo [错误] 找不到测试数据程序: %TEST_DATA_APP%
        goto end
    )
    echo 启动测试数据发送器...
    start "测试数据发送器" /B python %TEST_DATA_APP% --host %MQTT_HOST% --port %MQTT_PORT% --username %MQTT_USER% --password %MQTT_PASS%
) else (
    echo 启动仪表盘应用...
    start "智慧校园仪表盘" /B python %MAIN_APP%

    timeout /t 2 > nul

    if not defined NO_TEST (
        echo 启动测试数据发送器...
        start "测试数据发送器" /B python %TEST_DATA_APP% --host %MQTT_HOST% --port %MQTT_PORT% --username %MQTT_USER% --password %MQTT_PASS%
        echo 两个程序已成功启动!
    ) else (
        echo [警告] 仪表盘已启动，但找不到测试数据程序: %TEST_DATA_APP%
    )
)

echo.
echo 程序已启动，可以关闭此窗口。
echo 如果要结束程序，请关闭打开的应用程序窗口。

:end
echo.
pause