#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT连接诊断工具
用于诊断生产环境MQTT连接问题
"""

import paho.mqtt.client as mqtt
import time
import sys
import socket
from datetime import datetime

# 生产环境配置
MQTT_BROKER = "lot.lekee.cc"
MQTT_PORT = 1883
MQTT_USERNAME = "siot"
MQTT_PASSWORD = "dfrobot"

class MQTTDiagnostic:
    def __init__(self):
        self.connected = False
        self.connection_result = None
        self.subscribed_topics = []
        self.messages_received = []
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        """连接回调"""
        self.connection_result = reason_code
        if reason_code == 0:
            self.connected = True
            print(f"✅ MQTT连接成功! 连接到 {MQTT_BROKER}:{MQTT_PORT}")
            print(f"   客户端ID: {client._client_id}")
            print(f"   会话恢复: {'是' if flags['session present'] else '否'}")
            
            # 订阅测试主题
            test_topics = [
                "siot/环境温度",
                "siot/环境湿度", 
                "siot/aqi",
                "siot/eco2",
                "siot/tvoc",
                "siot/紫外线指数",
                "siot/uv风险等级",
                "siot/噪音",
                "siot/摄像头"
            ]
            
            for topic in test_topics:
                result = client.subscribe(topic)
                print(f"   订阅主题: {topic} (result: {result})")
                
        else:
            self.connected = False
            error_messages = {
                1: "协议版本不正确",
                2: "客户端ID无效",
                3: "服务器不可用",
                4: "用户名或密码错误",
                5: "未授权"
            }
            error_msg = error_messages.get(reason_code, f"未知错误 (代码: {reason_code})")
            print(f"❌ MQTT连接失败: {error_msg}")
    
    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        """断开连接回调"""
        self.connected = False
        if reason_code != 0:
            print(f"⚠️  意外断开连接 (代码: {reason_code})")
        else:
            print("📴 正常断开连接")
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """订阅回调"""
        print(f"✅ 订阅确认 (消息ID: {mid}, QoS: {granted_qos})")
        
    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            payload = msg.payload.decode('utf-8')
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"📨 [{timestamp}] {msg.topic}: {payload}")
            self.messages_received.append({
                'topic': msg.topic,
                'payload': payload,
                'timestamp': timestamp
            })
        except Exception as e:
            print(f"❌ 消息解码错误: {e}")
    
    def test_network_connectivity(self):
        """测试网络连通性"""
        print("\n🔍 网络连通性测试:")
        
        # 测试DNS解析
        try:
            import socket
            ip = socket.gethostbyname(MQTT_BROKER)
            print(f"✅ DNS解析成功: {MQTT_BROKER} -> {ip}")
        except Exception as e:
            print(f"❌ DNS解析失败: {e}")
            return False
        
        # 测试端口连接
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((MQTT_BROKER, MQTT_PORT))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口连接成功: {MQTT_BROKER}:{MQTT_PORT}")
                return True
            else:
                print(f"❌ 端口连接失败: {MQTT_BROKER}:{MQTT_PORT}")
                return False
        except Exception as e:
            print(f"❌ 网络连接错误: {e}")
            return False
    
    def test_mqtt_connection(self):
        """测试MQTT连接"""
        print(f"\n🔌 MQTT连接测试:")
        print(f"   服务器: {MQTT_BROKER}")
        print(f"   端口: {MQTT_PORT}")
        print(f"   用户名: {MQTT_USERNAME}")
        print(f"   密码: {'*' * len(MQTT_PASSWORD)}")
        
        # 创建客户端
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # 设置回调
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
        
        try:
            # 尝试连接
            print("⏳ 正在连接...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            # 非阻塞循环，等待连接结果
            for i in range(10):  # 等待10秒
                client.loop(timeout=1)
                if self.connection_result is not None:
                    break
                time.sleep(1)
                print(f"   等待连接... ({i+1}/10)")
            
            if self.connected:
                print("\n📡 监听消息 (30秒)...")
                print("   按 Ctrl+C 提前停止")
                
                start_time = time.time()
                try:
                    while time.time() - start_time < 30:
                        client.loop(timeout=1)
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\n⏹️  用户中断")
                
                # 断开连接
                client.disconnect()
                client.loop(timeout=1)
                
            return self.connected
            
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def generate_report(self):
        """生成诊断报告"""
        print("\n" + "="*60)
        print("📋 MQTT连接诊断报告")
        print("="*60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标服务器: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"连接状态: {'✅ 成功' if self.connected else '❌ 失败'}")
        
        if self.connection_result is not None:
            print(f"连接代码: {self.connection_result}")
        
        print(f"接收消息数量: {len(self.messages_received)}")
        
        if self.messages_received:
            print("\n最近接收的消息:")
            for msg in self.messages_received[-5:]:  # 显示最近5条
                print(f"  [{msg['timestamp']}] {msg['topic']}: {msg['payload']}")
        
        print("\n💡 建议:")
        if not self.connected:
            if self.connection_result == 4:
                print("  • 检查MQTT用户名和密码是否正确")
                print("  • 确认账户是否已激活且有权限")
            elif self.connection_result == 3:
                print("  • MQTT服务器可能暂时不可用")
                print("  • 稍后重试或联系服务提供商")
            elif self.connection_result is None:
                print("  • 检查网络连接")
                print("  • 检查防火墙设置")
                print("  • 确认服务器地址和端口正确")
            else:
                print("  • 检查MQTT客户端配置")
                print("  • 查看服务器日志获取更多信息")
        else:
            if len(self.messages_received) == 0:
                print("  • MQTT连接正常，但没有接收到消息")
                print("  • 检查数据源是否正在发送数据")
                print("  • 确认订阅的主题是否正确")
            else:
                print("  • MQTT连接和数据接收都正常")
                print("  • 系统运行良好")

def main():
    print("🚀 MQTT连接诊断工具启动")
    print(f"目标: {MQTT_BROKER}:{MQTT_PORT}")
    
    diagnostic = MQTTDiagnostic()
    
    # 1. 测试网络连通性
    if not diagnostic.test_network_connectivity():
        print("❌ 网络连通性测试失败，无法继续")
        return
    
    # 2. 测试MQTT连接
    diagnostic.test_mqtt_connection()
    
    # 3. 生成报告
    diagnostic.generate_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 诊断被用户中断")
    except Exception as e:
        print(f"\n💥 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
