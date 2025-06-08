#!/bin/bash

echo "🔧 验证MQTT状态修复..."
echo "========================================"

# 检查API端点
echo "1. 测试API端点..."
api_response=$(curl -s "http://iot.lekee.cc:3000/api/status")
echo "API响应: $api_response"

if echo "$api_response" | grep -q '"mqtt_connected":true'; then
    echo "✅ API端点正常，MQTT显示为已连接"
else
    echo "❌ API端点异常或MQTT未连接"
fi

echo ""

# 检查主页面是否包含正确的代码
echo "2. 检查主页面代码..."
if grep -q "checkMqttStatus();" "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/index.html"; then
    echo "✅ 主页面包含立即执行MQTT检测的代码"
else
    echo "❌ 主页面缺少立即执行MQTT检测的代码"
fi

if grep -q "setInterval(checkMqttStatus, 3000);" "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/index.html"; then
    echo "✅ 主页面包含定时MQTT检测的代码"
else
    echo "❌ 主页面缺少定时MQTT检测的代码"
fi

echo ""

# 检查端口检测逻辑
echo "3. 检查端口检测逻辑..."
if grep -q "if (currentPort === '3000')" "/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/index.html"; then
    echo "✅ 端口检测逻辑正确"
else
    echo "❌ 端口检测逻辑有误"
fi

echo ""

echo "4. 建议的验证步骤："
echo "   📱 1. 在浏览器中打开: http://iot.lekee.cc:3000/"
echo "   📱 2. 按F12打开开发者工具查看Console日志"
echo "   📱 3. 查看MQTT状态是否显示为'已连接'"
echo "   📱 4. 检查Console中的调试信息:"
echo "      - 端口检测信息"
echo "      - MQTT状态检测请求"
echo "      - API响应数据"

echo ""
echo "🎯 预期结果："
echo "   - MQTT状态应该显示'已连接'"
echo "   - Console中应该看到成功的API请求和响应"
echo "   - 端口检测应该使用3000端口"
