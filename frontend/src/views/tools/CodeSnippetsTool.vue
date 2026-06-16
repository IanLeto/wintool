<template>
  <div class="code-snippets-container">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="🔍 搜索代码片段（标题、语言、标签）..." 
          class="search-input"
          @input="filterSnippets"
        />
      </div>
      <button class="add-btn" @click="showAddDialog = true">
        ➕ 新建片段
      </button>
    </div>

    <!-- 语言筛选标签 -->
    <div class="language-filter">
      <button 
        v-for="lang in languages" 
        :key="lang"
        :class="['lang-tag', { active: selectedLanguage === lang }]"
        @click="filterByLanguage(lang)"
      >
        {{ lang }}
      </button>
    </div>

    <!-- 代码片段卡片列表 -->
    <div class="snippets-grid">
      <div 
        v-for="snippet in filteredSnippets" 
        :key="snippet.id"
        class="snippet-card"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="card-title">
            <span class="language-badge" :class="snippet.language.toLowerCase()">
              {{ snippet.language }}
            </span>
            <h3>{{ snippet.title }}</h3>
          </div>
          <div class="card-actions">
            <button class="icon-btn" @click="copyCode(snippet.code)" title="复制代码">
              📋
            </button>
            <button class="icon-btn" @click="editSnippet(snippet)" title="编辑">
              ✏️
            </button>
            <button class="icon-btn delete" @click="deleteSnippet(snippet.id)" title="删除">
              🗑️
            </button>
          </div>
        </div>

        <!-- 代码预览 -->
        <div class="code-preview">
          <pre><code>{{ snippet.code }}</code></pre>
        </div>

        <!-- 卡片底部信息 -->
        <div class="card-footer">
          <div class="tags">
            <span v-for="tag in snippet.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
          <div class="meta">
            <span class="date">{{ formatDate(snippet.createdAt) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredSnippets.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p>{{ searchQuery ? '没有找到匹配的代码片段' : '还没有代码片段，点击右上角添加吧！' }}</p>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h2>{{ editingSnippet ? '编辑片段' : '新建片段' }}</h2>
          <button class="close-btn" @click="closeDialog">✕</button>
        </div>
        
        <div class="dialog-body">
          <div class="form-group">
            <label>标题 *</label>
            <input 
              v-model="formData.title" 
              type="text" 
              placeholder="例如：HTTP 请求封装"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>语言 *</label>
            <select v-model="formData.language" class="form-select">
              <option value="Go">Go</option>
              <option value="Java">Java</option>
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript</option>
              <option value="TypeScript">TypeScript</option>
              <option value="SQL">SQL</option>
              <option value="YAML">YAML</option>
              <option value="Shell">Shell</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label>代码 *</label>
            <textarea 
              v-model="formData.code" 
              placeholder="粘贴你的代码片段..."
              class="form-textarea"
              rows="12"
            ></textarea>
          </div>

          <div class="form-group">
            <label>标签（用逗号分隔）</label>
            <input 
              v-model="formData.tagsInput" 
              type="text" 
              placeholder="例如：http, utils, 工具函数"
              class="form-input"
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
          <button class="btn btn-primary" @click="saveSnippet">保存</button>
        </div>
      </div>
    </div>

    <!-- 复制成功提示 -->
    <div v-if="showCopyToast" class="toast">
      ✅ 已复制到剪贴板
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// API 基础地址
const API_BASE_URL = 'http://localhost:8080/api/code-snippets'

// 数据状态
const snippets = ref([])
const searchQuery = ref('')
const selectedLanguage = ref('全部')
const showAddDialog = ref(false)
const showCopyToast = ref(false)
const editingSnippet = ref(null)
const loading = ref(false)

// 表单数据
const formData = ref({
  title: '',
  language: 'Go',
  code: '',
  tagsInput: ''
})

// 语言列表
const languages = computed(() => {
  const langs = new Set(['全部'])
  snippets.value.forEach(s => langs.add(s.language))
  return Array.from(langs)
})

// 过滤后的片段
const filteredSnippets = computed(() => {
  let result = snippets.value

  // 语言筛选
  if (selectedLanguage.value !== '全部') {
    result = result.filter(s => s.language === selectedLanguage.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s => 
      s.title.toLowerCase().includes(query) ||
      s.language.toLowerCase().includes(query) ||
      s.tags.some(tag => tag.toLowerCase().includes(query)) ||
      s.code.toLowerCase().includes(query)
    )
  }

  return result
})

// 加载数据
onMounted(() => {
  loadSnippets()
})

// 从后端加载数据
async function loadSnippets() {
  loading.value = true
  try {
    const response = await axios.get(API_BASE_URL)
    if (response.data.success) {
      snippets.value = response.data.data
    }
  } catch (error) {
    console.error('加载代码片段失败:', error)
    alert('加载代码片段失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

// 语言筛选
function filterByLanguage(lang) {
  selectedLanguage.value = lang
}

// 搜索筛选
function filterSnippets() {
  // 响应式自动处理
}

// 复制代码
async function copyCode(code) {
  try {
    await navigator.clipboard.writeText(code)
    showToast('已复制到剪贴板')
  } catch (err) {
    alert('复制失败，请手动复制')
  }
}

// 显示提示
function showToast(message) {
  showCopyToast.value = true
  // 可以扩展为显示自定义消息
  setTimeout(() => {
    showCopyToast.value = false
  }, 2000)
}

// 编辑片段
function editSnippet(snippet) {
  editingSnippet.value = snippet
  formData.value = {
    title: snippet.title,
    language: snippet.language,
    code: snippet.code,
    tagsInput: snippet.tags.join(', ')
  }
  showAddDialog.value = true
}

// 删除片段
async function deleteSnippet(id) {
  if (!confirm('确定要删除这个代码片段吗？')) {
    return
  }

  loading.value = true
  try {
    const response = await axios.delete(`${API_BASE_URL}/${id}`)
    if (response.data.success) {
      await loadSnippets()
      showToast('删除成功')
    }
  } catch (error) {
    console.error('删除代码片段失败:', error)
    alert('删除失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 保存片段
async function saveSnippet() {
  if (!formData.value.title || !formData.value.code) {
    alert('请填写标题和代码')
    return
  }

  const tags = formData.value.tagsInput
    .split(',')
    .map(t => t.trim())
    .filter(t => t)

  const snippetData = {
    title: formData.value.title,
    language: formData.value.language,
    code: formData.value.code,
    tags
  }

  loading.value = true
  try {
    if (editingSnippet.value) {
      // 更新现有片段
      const response = await axios.put(`${API_BASE_URL}/${editingSnippet.value.id}`, snippetData)
      if (response.data.success) {
        await loadSnippets()
        showToast('更新成功')
      }
    } else {
      // 添加新片段
      const response = await axios.post(API_BASE_URL, snippetData)
      if (response.data.success) {
        await loadSnippets()
        showToast('创建成功')
      }
    }
    closeDialog()
  } catch (error) {
    console.error('保存代码片段失败:', error)
    alert('保存失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 关闭对话框
function closeDialog() {
  showAddDialog.value = false
  editingSnippet.value = null
  formData.value = {
    title: '',
    language: 'Go',
    code: '',
    tagsInput: ''
  }
}

// 格式化日期
function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.code-snippets-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 顶部操作栏 */
.top-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.add-btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 语言筛选 */
.language-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.lang-tag {
  padding: 8px 16px;
  font-size: 14px;
  background: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-tag:hover {
  background: #e5e7eb;
}

.lang-tag.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* 卡片网格 */
.snippets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.snippet-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.2s;
}

.snippet-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-title {
  flex: 1;
}

.language-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  margin-bottom: 8px;
}

.language-badge.go {
  background: #e0f2fe;
  color: #0369a1;
}

.language-badge.java {
  background: #fef3c7;
  color: #92400e;
}

.language-badge.python {
  background: #dbeafe;
  color: #1e40af;
}

.language-badge.javascript,
.language-badge.typescript {
  background: #fef9c3;
  color: #854d0e;
}

.language-badge.sql {
  background: #f3e8ff;
  color: #6b21a8;
}

.language-badge.yaml,
.language-badge.shell {
  background: #f0fdf4;
  color: #166534;
}

.card-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}

.icon-btn:hover {
  background: #e5e7eb;
}

.icon-btn.delete:hover {
  background: #fee2e2;
}

/* 代码预览 */
.code-preview {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  max-height: 200px;
  overflow: auto;
}

.code-preview pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #374151;
}

.code-preview code {
  white-space: pre;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  font-size: 12px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
}

.meta .date {
  font-size: 13px;
  color: #9ca3af;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #6b7280;
}

.close-btn:hover {
  background: #e5e7eb;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-textarea {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  resize: vertical;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

/* Toast 提示 */
.toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  padding: 16px 24px;
  background: #10b981;
  color: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  font-weight: 600;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .snippets-grid {
    grid-template-columns: 1fr;
  }
  
  .top-bar {
    flex-direction: column;
  }
}
</style>
