<template>
  <div class="timestamp-converter">
    <div class="tool-header">
      <h1 class="tool-title">⏰ 时间戳转换工具</h1>
      <p class="tool-description">输入任意时间格式，自动转换为多种时间格式</p>
    </div>

    <div class="converter-container">
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-group">
          <label class="input-label">输入时间</label>
          <input
            v-model="inputValue"
            @input="handleInput"
            type="text"
            class="input-field"
            placeholder="例如: 1724587200 或 2024-08-25 19:00:00"
          />
          <div class="input-hint">
            支持：时间戳（秒/毫秒/微秒/纳秒）、日期字符串
          </div>
        </div>

        <button @click="convertNow" class="btn-now">
          🕐 使用当前时间
        </button>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <!-- 转换结果 -->
      <div v-if="result" class="results-grid">
        <!-- 时间戳格式 -->
        <div class="result-section">
          <h3 class="section-title">📊 时间戳格式</h3>
          <div class="result-items">
            <div class="result-item">
              <label>秒级时间戳</label>
              <input
                v-model="editableFormats.timestamp_second"
                @input="handleFormatEdit('timestamp_second')"
                @focus="selectAll"
                type="text"
                class="editable-value"
                placeholder="秒级时间戳"
              />
              <button @click="copyToClipboard(editableFormats.timestamp_second)" class="copy-btn">📋</button>
            </div>
            <div class="result-item">
              <label>毫秒级时间戳</label>
              <input
                v-model="editableFormats.timestamp_millisecond"
                @input="handleFormatEdit('timestamp_millisecond')"
                @focus="selectAll"
                type="text"
                class="editable-value"
                placeholder="毫秒级时间戳"
              />
              <button @click="copyToClipboard(editableFormats.timestamp_millisecond)" class="copy-btn">📋</button>
            </div>
            <div class="result-item">
              <label>微秒级时间戳</label>
              <input
                v-model="editableFormats.timestamp_microsecond"
                @input="handleFormatEdit('timestamp_microsecond')"
                @focus="selectAll"
                type="text"
                class="editable-value"
                placeholder="微秒级时间戳"
              />
              <button @click="copyToClipboard(editableFormats.timestamp_microsecond)" class="copy-btn">📋</button>
            </div>
            <div class="result-item">
              <label>纳秒级时间戳</label>
              <input
                v-model="editableFormats.timestamp_nanosecond"
                @input="handleFormatEdit('timestamp_nanosecond')"
                @focus="selectAll"
                type="text"
                class="editable-value"
                placeholder="纳秒级时间戳"
              />
              <button @click="copyToClipboard(editableFormats.timestamp_nanosecond)" class="copy-btn">📋</button>
            </div>
          </div>
        </div>

        <!-- 标准格式 -->
        <div class="result-section">
          <h3 class="section-title">📅 标准格式</h3>
          <div class="result-items">
            <div class="result-item">
              <label>ISO 8601</label>
              <div class="result-value" @click="copyToClipboard(result.formats.iso8601)">
                {{ result.formats.iso8601 }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>ISO 8601 UTC</label>
              <div class="result-value" @click="copyToClipboard(result.formats.iso8601_utc)">
                {{ result.formats.iso8601_utc }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>RFC 2822</label>
              <div class="result-value" @click="copyToClipboard(result.formats.rfc2822)">
                {{ result.formats.rfc2822 }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>标准日期</label>
              <div class="result-value" @click="copyToClipboard(result.formats.date_standard)">
                {{ result.formats.date_standard }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>标准日期时间</label>
              <div class="result-value" @click="copyToClipboard(result.formats.datetime_standard)">
                {{ result.formats.datetime_standard }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 中文格式 -->
        <div class="result-section">
          <h3 class="section-title">🇨🇳 中文格式</h3>
          <div class="result-items">
            <div class="result-item">
              <label>中文日期</label>
              <div class="result-value" @click="copyToClipboard(result.formats.date_cn)">
                {{ result.formats.date_cn }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>中文日期时间</label>
              <div class="result-value" @click="copyToClipboard(result.formats.datetime_cn)">
                {{ result.formats.datetime_cn }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>星期（中文）</label>
              <div class="result-value" @click="copyToClipboard(result.formats.weekday_cn)">
                {{ result.formats.weekday_cn }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 美式格式 -->
        <div class="result-section">
          <h3 class="section-title">🇺🇸 美式格式</h3>
          <div class="result-items">
            <div class="result-item">
              <label>美式日期</label>
              <div class="result-value" @click="copyToClipboard(result.formats.date_us)">
                {{ result.formats.date_us }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>美式日期时间</label>
              <div class="result-value" @click="copyToClipboard(result.formats.datetime_us)">
                {{ result.formats.datetime_us }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>星期（英文）</label>
              <div class="result-value" @click="copyToClipboard(result.formats.weekday_en)">
                {{ result.formats.weekday_en }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 其他格式 -->
        <div class="result-section">
          <h3 class="section-title">🔧 其他格式</h3>
          <div class="result-items">
            <div class="result-item">
              <label>仅时间</label>
              <div class="result-value" @click="copyToClipboard(result.formats.time_only)">
                {{ result.formats.time_only }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
            <div class="result-item">
              <label>年月</label>
              <div class="result-value" @click="copyToClipboard(result.formats.year_month)">
                {{ result.formats.year_month }}
                <span class="copy-icon">📋</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const inputValue = ref('')
const result = ref(null)
const error = ref('')
const loading = ref(false)

// 处理输入
const handleInput = async () => {
  if (!inputValue.value.trim()) {
    result.value = null
    error.value = ''
    return
  }

  await convertTimestamp()
}

// 转换时间戳
const convertTimestamp = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await axios.post('/api/timestamp/convert', {
      value: inputValue.value.trim()
    })
    
    if (response.data.success) {
      result.value = response.data
      error.value = ''
    } else {
      error.value = response.data.message || '转换失败'
      result.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.message || '转换失败，请检查输入格式'
    result.value = null
  } finally {
    loading.value = false
  }
}

// 使用当前时间
const convertNow = () => {
  inputValue.value = Math.floor(Date.now() / 1000).toString()
  convertTimestamp()
}

// 复制到剪贴板
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text.toString())
    // 简单的视觉反馈
    const event = new CustomEvent('show-toast', { 
      detail: { message: '已复制到剪贴板', type: 'success' } 
    })
    window.dispatchEvent(event)
  } catch (err) {
    alert('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.timestamp-converter {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.tool-header {
  text-align: center;
  margin-bottom: 3rem;
}

.tool-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tool-description {
  font-size: 1.125rem;
  color: #6b7280;
  margin: 0;
}

.converter-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.input-section {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.input-group {
  flex: 1;
}

.input-label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.input-field {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #9ca3af;
}

.btn-now {
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-now:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
}

.error-message {
  padding: 1rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  margin-bottom: 2rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.result-section {
  background: #f9fafb;
  border-radius: 12px;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.result-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-item label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.result-value {
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.95rem;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-value:hover {
  background: #f3f4f6;
  border-color: #667eea;
  transform: translateX(2px);
}

.copy-icon {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.result-value:hover .copy-icon {
  opacity: 1;
}

@media (max-width: 768px) {
  .timestamp-converter {
    padding: 1rem;
  }

  .tool-title {
    font-size: 2rem;
  }

  .input-section {
    flex-direction: column;
    align-items: stretch;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
