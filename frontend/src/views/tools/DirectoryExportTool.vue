<template>
  <div class="directory-export-tool">
    <!-- 工具头部 -->
    <div class="tool-header">
      <h2 class="tool-title">📁 目录结构导出</h2>
      <p class="tool-description">导出目录树形结构，支持 Windows 路径</p>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <div class="form-group">
        <label class="form-label">
          <span class="label-icon">📂</span>
          目录路径
        </label>
        <input
          v-model="directoryPath"
          type="text"
          class="form-input"
          placeholder="例如: D:\Projects 或 /home/user/projects"
          @keyup.enter="exportDirectory"
        />
        <div class="input-hint">
          💡 支持 Windows 路径（如 D:\folder）和 Linux 路径（如 /home/user）
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">
          <span class="label-icon">📊</span>
          导出深度
        </label>
        <div class="depth-selector">
          <button
            v-for="option in depthOptions"
            :key="option.value"
            :class="['depth-btn', { active: maxDepth === option.value }]"
            @click="maxDepth = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <button
        class="export-btn"
        :disabled="!directoryPath || loading"
        @click="exportDirectory"
      >
        <span v-if="loading" class="loading-spinner"></span>
        <span v-else>🚀</span>
        {{ loading ? '导出中...' : '开始导出' }}
      </button>
    </div>

    <!-- 创建目录结构区域 -->
    <div v-if="treeData" class="create-structure-section">
      <div class="section-header">
        <h3 class="section-title">📂 创建目录结构</h3>
        <p class="section-desc">在目标位置创建相同的空目录结构</p>
      </div>

      <div class="form-group">
        <label class="form-label">
          <span class="label-icon">🎯</span>
          目标路径
        </label>
        <input
          v-model="targetPath"
          type="text"
          class="form-input"
          placeholder="例如: D:\NewProject 或 /home/user/newproject"
          @keyup.enter="createStructure"
        />
        <div class="input-hint">
          💡 将在此路径创建与源目录相同的空文件夹结构
        </div>
      </div>

      <button
        class="create-btn"
        :disabled="!targetPath || creating"
        @click="createStructure"
      >
        <span v-if="creating" class="loading-spinner"></span>
        <span v-else>✨</span>
        {{ creating ? '创建中...' : '创建目录结构' }}
      </button>

      <!-- 创建成功提示 -->
      <div v-if="createSuccess" class="success-message">
        <span class="success-icon">✅</span>
        {{ createSuccess }}
      </div>

      <!-- 创建错误提示 -->
      <div v-if="createError" class="error-message">
        <span class="error-icon">❌</span>
        {{ createError }}
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">❌</span>
      {{ error }}
    </div>

    <!-- 结果展示区域 -->
    <div v-if="treeData" class="result-section">
      <div class="result-header">
        <h3 class="result-title">导出结果</h3>
        <div class="result-actions">
          <button class="action-btn" @click="copyToClipboard">
            📋 复制
          </button>
          <button class="action-btn" @click="expandAll">
            {{ allExpanded ? '📁 全部折叠' : '📂 全部展开' }}
          </button>
        </div>
      </div>

      <div class="path-info">
        <div class="info-item">
          <span class="info-label">原始路径:</span>
          <span class="info-value">{{ originalPath }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">转换路径:</span>
          <span class="info-value">{{ normalizedPath }}</span>
        </div>
      </div>

      <!-- 目录树 -->
      <div class="tree-container">
        <TreeNode
          :node="treeData"
          :level="0"
          :expanded-nodes="expandedNodes"
          @toggle="toggleNode"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TreeNode from '../../components/TreeNode.vue'

const directoryPath = ref('')
const targetPath = ref('')
const maxDepth = ref(null)
const loading = ref(false)
const creating = ref(false)
const error = ref('')
const createError = ref('')
const createSuccess = ref('')
const treeData = ref(null)
const originalPath = ref('')
const normalizedPath = ref('')
const expandedNodes = ref(new Set())
const allExpanded = ref(false)

const depthOptions = [
  { label: '1 级', value: 1 },
  { label: '2 级', value: 2 },
  { label: '3 级', value: 3 },
  { label: '5 级', value: 5 },
  { label: '全部', value: null }
]

// 导出目录
const exportDirectory = async () => {
  if (!directoryPath.value.trim()) {
    error.value = '请输入目录路径'
    return
  }

  loading.value = true
  error.value = ''
  treeData.value = null

  try {
    const response = await fetch('http://localhost:8080/api/directory/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        path: directoryPath.value,
        maxDepth: maxDepth.value
      })
    })

    const result = await response.json()

    if (result.success) {
      treeData.value = result.tree
      originalPath.value = result.originalPath
      normalizedPath.value = result.normalizedPath
      // 默认展开根节点
      expandedNodes.value = new Set([result.tree.path])
    } else {
      error.value = result.message || '导出失败'
    }
  } catch (err) {
    error.value = '网络错误: ' + err.message
  } finally {
    loading.value = false
  }
}

// 切换节点展开/折叠
const toggleNode = (nodePath) => {
  if (expandedNodes.value.has(nodePath)) {
    expandedNodes.value.delete(nodePath)
  } else {
    expandedNodes.value.add(nodePath)
  }
  expandedNodes.value = new Set(expandedNodes.value)
}

// 全部展开/折叠
const expandAll = () => {
  if (allExpanded.value) {
    expandedNodes.value = new Set()
  } else {
    const allPaths = new Set()
    const collectPaths = (node) => {
      if (node.type === 'directory') {
        allPaths.add(node.path)
        if (node.children) {
          node.children.forEach(collectPaths)
        }
      }
    }
    collectPaths(treeData.value)
    expandedNodes.value = allPaths
  }
  allExpanded.value = !allExpanded.value
}

// 复制到剪贴板
const copyToClipboard = () => {
  const text = generateTreeText(treeData.value, 0)
  navigator.clipboard.writeText(text).then(() => {
    alert('已复制到剪贴板！')
  }).catch(() => {
    alert('复制失败，请手动复制')
  })
}

// 生成树形文本
const generateTreeText = (node, level) => {
  const indent = '  '.repeat(level)
  const icon = node.type === 'directory' ? '📁' : '📄'
  let text = `${indent}${icon} ${node.name}\n`
  
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => {
      text += generateTreeText(child, level + 1)
    })
  }
  
  return text
}

// 创建目录结构
const createStructure = async () => {
  if (!targetPath.value.trim()) {
    createError.value = '请输入目标路径'
    return
  }

  creating.value = true
  createError.value = ''
  createSuccess.value = ''

  try {
    const response = await fetch('http://localhost:8080/api/directory/create-structure', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sourcePath: directoryPath.value,
        targetPath: targetPath.value,
        maxDepth: maxDepth.value
      })
    })

    const result = await response.json()

    if (result.success) {
      createSuccess.value = result.message
      // 3秒后清除成功消息
      setTimeout(() => {
        createSuccess.value = ''
      }, 3000)
    } else {
      createError.value = result.message || '创建失败'
    }
  } catch (err) {
    createError.value = '网络错误: ' + err.message
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.directory-export-tool {
  max-width: 1200px;
  margin: 0 auto;
}

/* 工具头部 */
.tool-header {
  margin-bottom: 2rem;
  text-align: center;
}

.tool-title {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.tool-description {
  margin: 0;
  font-size: 1rem;
  color: #6b7280;
}

/* 输入区域 */
.input-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.label-icon {
  font-size: 1.25rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

/* 深度选择器 */
.depth-selector {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.depth-btn {
  padding: 0.625rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.depth-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.depth-btn.active {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

/* 导出按钮 */
.export-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 1.25rem;
  height: 1.25rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误提示 */
.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 1rem;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.error-icon {
  font-size: 1.25rem;
}

/* 结果区域 */
.result-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.result-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.result-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f9fafb;
}

/* 路径信息 */
.path-info {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 600;
  color: #6b7280;
  min-width: 80px;
}

.info-value {
  color: #374151;
  word-break: break-all;
}

/* 树容器 */
.tree-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 1rem;
  max-height: 600px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
}

/* 创建目录结构区域 */
.create-structure-section {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 2px solid #86efac;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.section-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #166534;
}

.section-desc {
  margin: 0;
  font-size: 0.95rem;
  color: #15803d;
}

.create-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.create-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(16, 185, 129, 0.4);
}

.create-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 成功提示 */
.success-message {
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  padding: 1rem;
  color: #166534;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  animation: slideIn 0.3s ease;
}

.success-icon {
  font-size: 1.25rem;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .depth-selector {
    gap: 0.5rem;
  }
  
  .depth-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}
</style>
