# -*- coding: utf-8 -*-
"""
Kafka 消费者工具 - 极简版
只关注能消费到数据，条件最宽松
"""
from tools.base import BaseTool


class KafkaConsumerTool(BaseTool):
    TOOL_ID = "kafka_consumer"
    TOOL_NAME = "Kafka消费者"

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
            <label>消费位置</label>
            <select name="offset">
                <option value="latest" selected>最新消息（latest）</option>
                <option value="earliest">最早消息（earliest）</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>消费数量限制</label>
            <input type="number" name="limit" value="10" min="1" max="100">
        </div>
        
        <div class="form-group">
            <label>超时时间（秒）</label>
            <input type="number" name="timeout" value="30" min="5" max="120">
        </div>
        
        <button type="button" id="kafka-consumer-test-btn">测试连接</button>
        <button type="submit">开始消费</button>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
        (function() {
            // 等待 DOM 加载完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initKafkaConsumer);
            } else {
                initKafkaConsumer();
            }
            
            function initKafkaConsumer() {
                const testBtn = document.getElementById('kafka-consumer-test-btn');
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
                    
                    fetch('/api/tools/kafka_consumer/test', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            alert('✅ 连接成功！\\n' + (data.partitions ? '分区: ' + data.partitions.join(', ') : ''));
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
            """测试 Kafka 连接并获取分区信息"""
            try:
                data = request.get_json()
                brokers = [b.strip() for b in data.get("brokers", "").split(",") if b.strip()]
                topic = data.get("topic", "").strip()
                
                if not brokers or not topic:
                    return jsonify({"ok": False, "error": "Broker和Topic不能为空"})
                
                from kafka import KafkaConsumer
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
                
                consumer = KafkaConsumer(**config)
                
                # 获取分区信息
                partitions = consumer.partitions_for_topic(topic)
                consumer.close()
                
                if partitions:
                    return jsonify({
                        "ok": True, 
                        "message": f"连接成功，Topic有{len(partitions)}个分区",
                        "partitions": sorted(list(partitions))
                    })
                else:
                    return jsonify({"ok": False, "error": f"Topic '{topic}' 不存在或无分区"})
                
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})

        @bp.route("/consume", methods=["POST"])
        def consume_messages():
            """消费消息 - 极简版，只要能拿到数据"""
            try:
                data = request.get_json()
                brokers = [b.strip() for b in data.get("brokers", "").split(",") if b.strip()]
                topic = data.get("topic", "").strip()
                offset = data.get("offset", "latest")
                limit = int(data.get("limit", 10))
                timeout = int(data.get("timeout", 30))
                
                if not brokers or not topic:
                    return jsonify({"ok": False, "error": "Broker和Topic不能为空"})
                
                from kafka import KafkaConsumer, TopicPartition
                import time
                
                config = {
                    'bootstrap_servers': brokers,
                    'auto_offset_reset': offset,
                    'enable_auto_commit': False,
                    'consumer_timeout_ms': timeout * 1000,
                    'value_deserializer': lambda m: m.decode('utf-8', errors='ignore'),
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
                
                consumer = KafkaConsumer(topic, **config)
                
                messages = []
                start_time = time.time()
                
                try:
                    for message in consumer:
                        # 解析消息
                        try:
                            msg_data = json.loads(message.value)
                        except:
                            msg_data = {"_raw": message.value}
                        
                        # 添加元数据
                        msg_data["_partition"] = message.partition
                        msg_data["_offset"] = message.offset
                        msg_data["_timestamp"] = message.timestamp
                        
                        messages.append(msg_data)
                        
                        # 达到限制或超时
                        if len(messages) >= limit:
                            break
                        
                        if time.time() - start_time > timeout:
                            break
                            
                except StopIteration:
                    pass  # 超时正常退出
                
                consumer.close()
                
                if messages:
                    return jsonify({
                        "ok": True,
                        "message": f"消费成功，共{len(messages)}条消息",
                        "count": len(messages),
                        "messages": messages
                    })
                else:
                    return jsonify({
                        "ok": False,
                        "message": "未消费到任何消息（可能Topic无新数据）",
                        "count": 0,
                        "messages": []
                    })
                
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
