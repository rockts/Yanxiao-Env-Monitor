@echo off
:: 智慧校园仪表盘依赖项更新脚本（Windows版）
:: 此脚本用于更新/安装所有应用程序需要的依赖库

echo ============================================
echo    烟铺小学智慧校园仪表盘 - 依赖项更新
echo ============================================
echo.

:: 检查Python是否安装
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到Python.
    echo 请安装Python 3后再试.
    echo 访问 https://www.python.org/downloads/ 下载安装Python 3
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

:: 检查Python版本
python --version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYVER=%%I
echo 使用Python版本: %PYVER%
echo.

:: 确保pip已安装
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 正在安装pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

:: 更新pip本身
echo 更新pip...
python -m pip install --upgrade pip
echo.

:: 安装/更新所有依赖项
echo 安装/更新依赖项...
echo.

echo 安装/更新: paho-mqtt
python -m pip install --upgrade paho-mqtt>=1.6.1
echo.

echo 安装/更新: Pillow
python -m pip install --upgrade Pillow>=8.4.0
echo.

echo 安装/更新: matplotlib
python -m pip install --upgrade matplotlib>=3.5.1
echo.

echo 安装/更新: requests
python -m pip install --upgrade requests>=2.27.1
echo.

echo 安装/更新: numpy
python -m pip install --upgrade numpy>=1.22.0
echo.

echo 依赖项更新完成!
echo.

:: 记录所有已安装的包
echo 已安装的依赖项:
python -m pip list
echo.

echo 处理完成.
echo 按任意键退出...
pause >nul