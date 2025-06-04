# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading
import json
import logging
import requests
import markdown

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
latest_data = {
    "temperature": 0,
    "humidity": 0,
    "aqi": 0,
    "eco2": 0,
    "tvoc": 0,
    "uv_raw": 0,
    "uv_index": 0,
    "noise": 0,
    "camera": "",
    "suggestion": "Getting suggestions..."
}

MQTT_BROKER = "192.168.1.128"
MQTT_PORT = 1883
MQTT_USERNAME = "siot"
MQTT_PASSWORD = "dfrobot"

DASHSCOPE_API_KEY = "sk-1515ee3c6dc74eaf9e2ba3e2c86aa87e"
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

TOPIC_MAP = {
    "siot/环境温度": "temperature",
    "siot/环境湿度": "humidity",
    "siot/aqi": "aqi",
    "siot/eco2": "eco2",
    "siot/tvoc": "tvoc",
    "siot/紫外线指数": "uv_raw",
    "siot/uv风险等级": "uv_index",
    "siot/噪音": "noise",
    "siot/摄像头": "camera"
}

mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        log.info("MQTT connected successfully")
        for topic in TOPIC_MAP:
            client.subscribe(topic)
            log.info(f"Subscribed to {topic}")
    else:
        mqtt_connected = False
        log.warning(f"MQTT connection failed, rc={rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    log.warning(f"MQTT disconnected, rc={rc}")

def on_message(client, userdata, msg):
    try:
        key = TOPIC_MAP.get(msg.topic)
        if not key:
            return
        payload = msg.payload.decode()
        latest_data[key] = payload
        log.info(f"📡 [{msg.topic}] {payload}")
    except Exception as e:
        log.warning("⚠️ 解析错误：%s", e)

def mqtt_worker():
    log.info("🚀 启动 MQTT 子线程")
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

def start_mqtt_background():
    thread = threading.Thread(target=mqtt_worker)
    thread.daemon = True
    thread.start()

start_mqtt_background()

@app.route("/data")
def get_data():
    return jsonify(latest_data)

@app.route("/api/ai_suggestion", methods=["POST"])
def ai_suggestion():
    try:
        data = request.get_json(force=True)
        # 判断类型，分室内/室外
        ai_type = data.get("type", "indoor")
        if ai_type == "indoor":
            # 只用siot本地传感器数据
            aqi = data.get("aqi", 0)
            uv_index = data.get("uv_index", 0)
            temperature = data.get("temperature", 0)
            humidity = data.get("humidity", 0)
            noise = data.get("noise", 0)
            eco2 = data.get("eco2", 0)
            tvoc = data.get("tvoc", 0)
            prompt = (
                f"请根据以下教室内环境监测数据，面向小学师生生成一段简洁、实用的健康建议，内容为纯文本，不要markdown格式，不要列表，不要分条：\n"
                f"空气质量指数(AQI)：{aqi}\n紫外线指数：{uv_index}\n温度：{temperature}℃\n湿度：{humidity}%\n噪音：{noise}dBA\neCO₂：{eco2}ppm\nTVOC：{tvoc}ppb。\n"
                "要求：1. 建议内容简明、具体、适合校园日常生活，直接输出一段完整建议。"
                "2. 请根据温度数值智能判断：20℃及以上不需要保暖提示，低于15℃才建议保暖或佩戴围巾手套。"
                "3. 不要机械输出保暖建议，需结合实际温度和校园场景。"
            )
        else:
            # 只用外部api获取的天气/pm2.5/风向/温度
            weather = data.get("weather", "-")
            wind_dir = data.get("wind_dir", "-")
            outdoor_temp = data.get("outdoor_temp", "-")
            pm25 = data.get("pm25", "-")
            prompt = (
                f"请根据以下室外环境数据，面向小学师生生成一段简洁、实用的户外活动建议，内容为纯文本，不要markdown格式，不要列表，不要分条：\n"
                f"天气：{weather}\n风向：{wind_dir}\n室外温度：{outdoor_temp}℃\nPM2.5：{pm25}μg/m³。\n"
                "要求：1. 建议内容简明、具体、适合校园日常生活，直接输出一段完整建议。"
                "2. 请根据温度数值智能判断：20℃及以上不需要保暖提示，低于15℃才建议保暖或佩戴围巾手套。"
                "3. 不要机械输出保暖建议，需结合实际温度和校园场景。"
            )
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-turbo",
            "input": {
                "prompt": prompt
            }
        }
        resp = requests.post(DASHSCOPE_API_URL, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            suggestion_md = result.get("output", {}).get("text", "AI建议生成失败（无内容）").strip()
            if suggestion_md.startswith('```markdown'):
                suggestion_md = suggestion_md[len('```markdown'):].lstrip('\n')
            if suggestion_md.endswith('```'):
                suggestion_md = suggestion_md[:-3].rstrip('\n')
            suggestion_md = suggestion_md.strip('`\n')
            print("\n===== AI建议原始内容 =====\n" + suggestion_md + "\n=======================\n")
            suggestion_html = markdown.markdown(suggestion_md)
            return jsonify({"suggestion": suggestion_md, "html": suggestion_html})
        else:
            log.warning(f"通义千问接口调用失败: {resp.status_code} {resp.text}")
            return jsonify({"suggestion": f"AI建议生成失败（通义千问接口异常:{resp.status_code}）"}), 500
    except Exception as e:
        log.warning(f"AI建议生成失败: {e}")
        return jsonify({"suggestion": "AI建议生成失败"}), 500

@app.route("/api/status")
def api_status():
    return jsonify({"mqtt_connected": mqtt_connected})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5052, debug=False, threaded=True)
