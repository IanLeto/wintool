# -*- coding: utf-8 -*-
"""
Kafka 生产者工具 - 极简版
只关注能发送消息，不做复杂校验
"""
from tools.base import BaseTool


class KafkaProducerTool(BaseTool):
    TOOL_ID = "kafka_producer"
    TOOL_NAME = "Kafka生产者"

    @classmethod
    def get_form_html(cls):
        return """
        <div class="form-group">
            <label>Broker地址（多个用逗号分隔）</label>
            <input type="text" name="brokers" placeholder="例如: 192.168.1.100:9092,192.168.1.101:9092" required>
        </div>
        
        <div class="form-group">
            <label>Topic</label>
            <input type="text" name="topic" placeholder="例如: test-topic" required>
        </div>
        
        <div class="form-group">
            <label>认证方式</label>
            <select name="auth_type">
                <option value="none">无认证</option>
                <option value="sasl" selected>SASL (用户名密码)</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>用户名（可选，默认: tolc）</label>
            <input type="text" name="username" placeholder="tolc">
        </div>
        
        <div class="form-group">
            <label>密码（可选，默认: O7F6FA6IDS_i）</label>
            <input type="password" name="password" placeholder="O7F6FA6IDS_i">
        </div>
        
        <div class="form-group">
            <label>消息内容（JSON格式）</label>
            <textarea name="message" rows="8" placeholder='{"key": "value"}'>{}</textarea>
        </div>
        
        <div class="form-group">
            <label>发送数量</label>
            <input type="number" name="count" value="1" min="1">
        </div>
        
        <button type="button" id="kafka-producer-test-btn">测试连接</button>
        <button type="submit">发送消息</button>
        
        <script>
        (function() {
            // 等待 DOM 加载完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initKafkaProducer);
            } else {
                initKafkaProducer();
            }
            
            function initKafkaProducer() {
                const testBtn = document.getElementById('kafka-producer-test-btn');
                if (!testBtn) {
                    console.error('找不到测试按钮');
                    return;
                }
                
                testBtn.addEventListener('click', function() {
                    const toolBody = document.querySelector('.tool-body');
                    if (!toolBody) {
                        alert('❌ 找不到表单容器');
                        return;
                    }
                    
                    const brokersInput = toolBody.querySelector('[name="brokers"]');
                    const topicInput = toolBody.querySelector('[name="topic"]');
                    const authTypeInput = toolBody.querySelector('[name="auth_type"]');
                    const usernameInput = toolBody.querySelector('[name="username"]');
                    const passwordInput = toolBody.querySelector('[name="password"]');
                    
                    const data = {
                        brokers: brokersInput ? brokersInput.value : '',
                        topic: topicInput ? topicInput.value : '',
                        auth_type: authTypeInput ? authTypeInput.value : 'sasl',
                        username: usernameInput ? usernameInput.value : '',
                        password: passwordInput ? passwordInput.value : ''
                    };
                    
                    fetch('/api/tools/kafka_producer/test', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            alert('✅ 连接成功！');
                        } else {
                            alert('❌ 连接失败：' + data.error);
                        }
                    })
                    .catch(err => {
                        alert('❌ 请求失败：' + err.message);
                    });
                });
            }
        })();
        </script>
        """

    @classmethod
    def register_routes(cls, bp):
        from flask import request, jsonify
        import json

        @bp.route("/test", methods=["POST"])
        def test_connection():
            """测试 Kafka 连接"""
            try:
                data = request.get_json()
                brokers = [b.strip() for b in data.get("brokers", "").split(",") if b.strip()]
                
                if not brokers:
                    return jsonify({"ok": False, "error": "Broker地址不能为空"})
                
                # 尝试连接
                from kafka import KafkaProducer
                from kafka.errors import KafkaError
                
                config = {
                    'bootstrap_servers': brokers,
                    'request_timeout_ms': 5000,
                    'api_version_auto_timeout_ms': 3000,
                }
                
                # 配置认证
                auth_type = data.get("auth_type", "sasl")
                if auth_type == "sasl":
                    username = data.get("username") or "tolc"
                    password = data.get("password") or "O7F6FA6IDS_i"
                    config.update({
                        'security_protocol': 'SASL_PLAINTEXT',
                        'sasl_mechanism': 'PLAIN',
                        'sasl_plain_username': username,
                        'sasl_plain_password': password,
                    })
                
                producer = KafkaProducer(**config)
                producer.close()
                
                return jsonify({"ok": True, "message": "连接成功"})
                
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})

        @bp.route("/send", methods=["POST"])
        def send_message():
            """发送消息"""
            try:
                data = request.get_json()
                brokers = [b.strip() for b in data.get("brokers", "").split(",") if b.strip()]
                topic = data.get("topic", "").strip()
                message_str = data.get("message", "{}")
                count = int(data.get("count", 1))
                
                if not brokers or not topic:
                    return jsonify({"ok": False, "error": "Broker和Topic不能为空"})
                
                # 解析消息
                try:
                    message = json.loads(message_str)
                except:
                    message = {"data": message_str}
                
                # 创建生产者
                from kafka import KafkaProducer
                
                config = {
                    'bootstrap_servers': brokers,
                    'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                    'request_timeout_ms': 10000,
                }
                
                # 配置认证
                auth_type = data.get("auth_type", "sasl")
                if auth_type == "sasl":
                    username = data.get("username") or "tolc"
                    password = data.get("password") or "O7F6FA6IDS_i"
                    config.update({
                        'security_protocol': 'SASL_PLAINTEXT',
                        'sasl_mechanism': 'PLAIN',
                        'sasl_plain_username': username,
                        'sasl_plain_password': password,
                    })
                
                producer = KafkaProducer(**config)
                
                # 发送消息
                sent = 0
                failed = 0
                results = []
                
                for i in range(count):
                    try:
                        future = producer.send(topic, message)
                        record = future.get(timeout=10)
                        sent += 1
                        results.append({
                            "index": i + 1,
                            "status": "success",
                            "partition": record.partition,
                            "offset": record.offset
                        })
                    except Exception as e:
                        failed += 1
                        results.append({
                            "index": i + 1,
                            "status": "failed",
                            "error": str(e)
                        })
                
                producer.close()
                
                return jsonify({
                    "ok": True,
                    "message": f"发送完成：成功 {sent}/{count}",
                    "sent": sent,
                    "failed": failed,
                    "results": results
                })
                
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
