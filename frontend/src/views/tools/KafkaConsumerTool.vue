<template>
  <div class="kafka-consumer-tool">
    <div class="tool-header">
      <h2>📨 Kafka 消费工具</h2>
      <p class="description">连接内网 Kafka 集群，消费消息数据（支持 SASL 认证）</p>
    </div>

    <!-- 连接配置 -->
    <div class="config-section">
      <h3>🔧 连接配置</h3>
      
      <div class="form-group">
        <label>Broker 地址 *</label>
        <input
          v-model="config.brokers"
          type="text"
          placeholder="例如: 192.168.1.100:9092,192.168.1.101:9092"
          class="input-field"
        />
        <span class="hint">多个 Broker 用逗号分隔</span>
      </div>

      <div class="form-group">
        <label>Topic *</label>
        <input
          v-model="config.topic"
          type="text"
          placeholder="例如: test-topic"
          class="input-field"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="config.username"
            type="text"
            placeholder="SASL 用户名（可选）"
            class="input-field"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="config.password"
            type="password"
            placeholder="SASL 密码（可选）"
            class="input-field"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>消费位置</label>
          <select v-model="config.offset" class="select-field">
            <option value="latest">最新消息（latest）</option>
            <option value="earliest">最早消息（earliest）</option>
          </select>
        </div>

        <div class="form-group">
          <label>消费数量</label>
          <input
            v-model.number="config.limit"
            type="number"
            min="1"
            max="100"
            class="input-field"
          />
        </div>

        <div class="form-group">
          <label>超时时间（秒）</label>
          <input
            v-model.number="config.timeout"
            type="number"
            min="5"
            max="120"
            class="input-field"
          />
        </div>
      </div>

      <div class="button-group">
        <button @click="testConnection" class="btn-test" :disabled="testing || consuming">
          <span v-if="!testing">🔍 测试连接</span>
          <span v-else>⏳ 测试中...</span>
        </button>
        <button @click="consumeMessages" class="btn-consume" :disabled="testing || consuming">
          <span v-if="!consuming">▶️ 开始消费</span>
          <span v-else>⏳ 消费中...</span>
        </button>
      </div>
    </div>

    <!-- 测试结果 -->
    <div v-if="testResult" class="result-section">
      <div class="result-header" :class="{ success: testResult.success, error: !testResult.success }">
        <span v-if="testResult.success">✅ {{ testResult.message }}</span>
        <span v-else>❌ {{ testResult.message }}</span>
      </div>
      <div v-if="testResult.partitions" class="partitions-info">
        <strong>分区列表:</strong> {{ testResult.partitions.join(', ') }}
      </div>
    </div>

    <!-- 消息列表 -->
    <div v-if="messages.length > 0" class="messages-section">
      <div class="section-header">
        <h3>📬 消费的消息（共 {{ messages.length }} 条）</h3>
        <button @click="clearMessages" class="btn-clear">🗑️ 清空</button>
      </div>

      <div class="messages-list">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-card"
        >
          <div class="message-header">
            <span class="message-index">#{{ index + 1 }}</span>
            <span class="message-meta">
              分区: {{ msg._partition }} | 偏移量: {{ msg._offset }}
              <span v-if="msg._timestamp"> | 时间: {{ formatTimestamp(msg._timestamp) }}</span>
            </span>
          </div>
          <div class="message-body">
            <pre>{{ formatMessage(msg) }}</pre>
          </div>
          <div class="message-actions">
            <button @click="copyMessage(msg)" class="btn-copy">📋 复制</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!testing && !consuming && !testResult" class="empty-state">
      <p>📭 还没有消费任何消息</p>
      <p class="hint">配置连接信息后，点击"开始消费"按钮</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 配置
const config = ref({
  brokers: '',
  topic: '',
  username: '',
  password: '',
  offset: 'latest',
  limit: 10,
  timeout: 30
})

// 状态
const testing = ref(false)
const consuming = ref(false)
const testResult = ref(null)
const messages = ref([])

// 测试连接
const testConnection = async () => {
  if (!config.value.brokers || !config.value.topic) {
    alert('❌ 请填写 Broker 地址和 Topic')
    return
  }

  testing.value = true
  testResult.value = null

  try {
    const response = await fetch('/api/kafka/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config.value)
    })

    const data = await response.json()
    testResult.value = data

    if (!data.success) {
      alert(`❌ 连接失败: ${data.message}`)
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: `请求失败: ${error.message}`
    }
    alert(`❌ 请求失败: ${error.message}`)
  } finally {
    testing.value = false
  }
}

// 消费消息
const consumeMessages = async () => {
  if (!config.value.brokers || !config.value.topic) {
    alert('❌ 请填写 Broker 地址和 Topic')
    return
  }

  consuming.value = true

  try {
    const response = await fetch('/api/kafka/consume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config.value)
    })

    const data = await response.json()

    if (data.success) {
      messages.value = data.messages || []
      alert(`✅ ${data.message}`)
    } else {
      alert(`❌ 消费失败: ${data.message}`)
    }
  } catch (error) {
    alert(`❌ 请求失败: ${error.message}`)
  } finally {
    consuming.value = false
  }
}

// 清空消息
const clearMessages = () => {
  if (confirm('确定要清空所有消息吗？')) {
    messages.value = []
  }
}

// 格式化消息
const formatMessage = (msg) => {
  const { _partition, _offset, _timestamp, ...data } = msg
  return JSON.stringify(data, null, 2)
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 复制消息
const copyMessage = async (msg) => {
  try {
    const text = formatMessage(msg)
    await navigator.clipboard.writeText(text)
    alert('✅ 已复制到剪贴板')
  } catch (error) {
    alert('❌ 复制失败')
  }
}
</script>

<style scoped>
.kafka-consumer-tool {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.tool-header {
  margin-bottom: 30px;
}

.tool-header h2 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  font-size: 14px;
}

.config-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.config-section h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.input-field,
.select-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.input-field:focus,
.select-field:focus {
  outline: none;
  border-color: #409eff;
}

.hint {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-test,
.btn-consume {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-test {
  background: #409eff;
  color: white;
}

.btn-test:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-consume {
  background: #67c23a;
  color: white;
}

.btn-consume:hover:not(:disabled) {
  background: #85ce61;
}

.btn-test:disabled,
.btn-consume:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-header {
  padding: 12px;
  border-radius: 4px;
  font-weight: 500;
}

.result-header.success {
  background: #f0f9ff;
  color: #67c23a;
}

.result-header.error {
  background: #fef0f0;
  color: #f56c6c;
}

.partitions-info {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.messages-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  color: #2c3e50;
}

.btn-clear {
  padding: 6px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-clear:hover {
  background: #f78989;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-card {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.message-index {
  font-weight: 600;
  color: #409eff;
}

.message-meta {
  font-size: 12px;
  color: #909399;
}

.message-body {
  padding: 16px;
  background: #fafafa;
}

.message-body pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-actions {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.btn-copy {
  padding: 6px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-copy:hover {
  background: #66b1ff;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 8px;
}

.empty-state .hint {
  font-size: 14px;
  color: #c0c4cc;
}
</style>
