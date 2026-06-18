<template>
  <div class="k8s-cluster-tool">
    <div class="tool-header">
      <h2>🚢 K8s 集群管理</h2>
      <p class="description">管理多个 Kubernetes 集群，批量执行命令</p>
    </div>

    <!-- 集群列表 -->
    <div class="clusters-section">
      <div class="section-header">
        <h3>📋 集群列表</h3>
        <button @click="refreshClusters" class="btn-refresh" :disabled="loading">
          <span v-if="!loading">🔄 刷新</span>
          <span v-else>⏳ 加载中...</span>
        </button>
      </div>

      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <div v-if="clusters.length === 0 && !loading" class="empty-state">
        <p>📭 未找到集群配置</p>
        <p class="hint">请确保 kubeconfig 文件存在且配置正确</p>
      </div>

      <div v-else class="clusters-grid">
        <div
          v-for="cluster in clusters"
          :key="cluster.name"
          class="cluster-card"
          :class="{ 
            'active': cluster.current,
            'selected': selectedClusters.includes(cluster.name)
          }"
          @click="toggleCluster(cluster.name)"
        >
          <div class="cluster-header">
            <input
              type="checkbox"
              :checked="selectedClusters.includes(cluster.name)"
              @click.stop="toggleCluster(cluster.name)"
              class="cluster-checkbox"
            />
            <h4>{{ cluster.name }}</h4>
            <span v-if="cluster.current" class="current-badge">当前</span>
          </div>
          <div class="cluster-info">
            <div class="info-item">
              <span class="label">命名空间:</span>
              <span class="value">{{ cluster.namespace || 'default' }}</span>
            </div>
            <div class="info-item">
              <span class="label">用户:</span>
              <span class="value">{{ cluster.user || '-' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="clusters.length > 0" class="batch-actions">
        <button
          @click="selectAll"
          class="btn-secondary"
          :disabled="loading"
        >
          {{ selectedClusters.length === clusters.length ? '取消全选' : '全选' }}
        </button>
        <span class="selected-count">
          已选择: {{ selectedClusters.length }} / {{ clusters.length }}
        </span>
      </div>
    </div>

    <!-- 命令执行 -->
    <div class="command-section">
      <div class="section-header">
        <h3>⚡ 批量执行命令</h3>
      </div>

      <div class="command-input-group">
        <label>选择命令类型:</label>
        <div class="command-templates">
          <button
            v-for="template in commandTemplates"
            :key="template.name"
            @click="selectTemplate(template)"
            class="btn-template"
            :class="{ 'active': selectedTemplate === template.name }"
          >
            {{ template.icon }} {{ template.name }}
          </button>
        </div>
      </div>

      <div class="command-input-group">
        <label>kubectl 命令:</label>
        <textarea
          v-model="command"
          placeholder="例如: get pods -n default"
          class="command-textarea"
          rows="3"
          :disabled="executing"
        ></textarea>
        <p class="hint">
          💡 提示: 只需输入 kubectl 后面的部分，例如 "get pods" 或 "get nodes"
        </p>
      </div>

      <div class="command-actions">
        <button
          @click="executeCommand"
          class="btn-primary"
          :disabled="!canExecute"
        >
          <span v-if="!executing">🚀 执行命令</span>
          <span v-else>⏳ 执行中... ({{ executionProgress }}/{{ selectedClusters.length }})</span>
        </button>
        <button
          v-if="results.length > 0"
          @click="clearResults"
          class="btn-secondary"
        >
          🗑️ 清空结果
        </button>
      </div>
    </div>

    <!-- 执行结果 -->
    <div v-if="results.length > 0" class="results-section">
      <div class="section-header">
        <h3>📊 执行结果</h3>
        <div class="result-stats">
          <span class="stat success">✅ 成功: {{ successCount }}</span>
          <span class="stat failed">❌ 失败: {{ failedCount }}</span>
        </div>
      </div>

      <div class="results-list">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="result-card"
          :class="{ 'success': result.success, 'failed': !result.success }"
        >
          <div class="result-header">
            <h4>
              <span class="status-icon">{{ result.success ? '✅' : '❌' }}</span>
              {{ result.cluster }}
            </h4>
            <span class="execution-time">{{ result.duration }}ms</span>
          </div>
          
          <div class="result-command">
            <strong>命令:</strong> kubectl {{ result.command }}
          </div>

          <div class="result-output">
            <div class="output-header">
              <strong>{{ result.success ? '输出:' : '错误:' }}</strong>
              <button
                @click="copyOutput(result.output)"
                class="btn-copy"
                title="复制输出"
              >
                📋 复制
              </button>
            </div>
            <pre>{{ result.output || '(无输出)' }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const clusters = ref([])
const selectedClusters = ref([])
const command = ref('')
const results = ref([])
const loading = ref(false)
const executing = ref(false)
const executionProgress = ref(0)
const error = ref('')
const selectedTemplate = ref('')

const commandTemplates = [
  { name: '查看 Pods', icon: '📦', command: 'get pods -A' },
  { name: '查看节点', icon: '🖥️', command: 'get nodes' },
  { name: '查看服务', icon: '🌐', command: 'get svc -A' },
  { name: '查看部署', icon: '🚀', command: 'get deployments -A' },
  { name: '查看命名空间', icon: '📁', command: 'get namespaces' },
  { name: '集群信息', icon: 'ℹ️', command: 'cluster-info' },
  { name: '查看事件', icon: '📋', command: 'get events -A --sort-by=.metadata.creationTimestamp' },
]

const canExecute = computed(() => {
  return selectedClusters.value.length > 0 && 
         command.value.trim() !== '' && 
         !executing.value
})

const successCount = computed(() => {
  return results.value.filter(r => r.success).length
})

const failedCount = computed(() => {
  return results.value.filter(r => !r.success).length
})

// 刷新集群列表
async function refreshClusters() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('/api/k8s/clusters')
    const data = await response.json()
    
    if (data.success) {
      clusters.value = data.data
      // 默认选中当前集群
      const currentCluster = clusters.value.find(c => c.current)
      if (currentCluster && selectedClusters.value.length === 0) {
        selectedClusters.value = [currentCluster.name]
      }
    } else {
      error.value = data.message || '获取集群列表失败'
    }
  } catch (err) {
    error.value = '网络错误: ' + err.message
  } finally {
    loading.value = false
  }
}

// 切换集群选择
function toggleCluster(clusterName) {
  const index = selectedClusters.value.indexOf(clusterName)
  if (index > -1) {
    selectedClusters.value.splice(index, 1)
  } else {
    selectedClusters.value.push(clusterName)
  }
}

// 全选/取消全选
function selectAll() {
  if (selectedClusters.value.length === clusters.value.length) {
    selectedClusters.value = []
  } else {
    selectedClusters.value = clusters.value.map(c => c.name)
  }
}

// 选择命令模板
function selectTemplate(template) {
  selectedTemplate.value = template.name
  command.value = template.command
}

// 执行命令
async function executeCommand() {
  if (!canExecute.value) return

  executing.value = true
  executionProgress.value = 0
  results.value = []

  try {
    const response = await fetch('/api/k8s/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        clusters: selectedClusters.value,
        command: command.value.trim()
      })
    })

    const data = await response.json()

    if (data.success) {
      results.value = data.data
      executionProgress.value = data.data.length
    } else {
      error.value = data.message || '执行命令失败'
    }
  } catch (err) {
    error.value = '网络错误: ' + err.message
  } finally {
    executing.value = false
  }
}

// 清空结果
function clearResults() {
  results.value = []
  executionProgress.value = 0
}

// 复制输出
function copyOutput(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert('✅ 已复制到剪贴板')
  }).catch(() => {
    alert('❌ 复制失败')
  })
}

onMounted(() => {
  refreshClusters()
})
</script>

<style scoped>
.k8s-cluster-tool {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.tool-header {
  margin-bottom: 30px;
}

.tool-header h2 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 20px;
  color: #34495e;
  margin: 0;
}

.btn-refresh {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c33;
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #95a5a6;
}

.empty-state p {
  margin: 10px 0;
}

.hint {
  font-size: 13px;
  color: #95a5a6;
  margin-top: 8px;
}

.clusters-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 24px;
}

.clusters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.cluster-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.cluster-card:hover {
  border-color: #3498db;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
}

.cluster-card.selected {
  border-color: #3498db;
  background: #f0f8ff;
}

.cluster-card.active {
  border-color: #27ae60;
}

.cluster-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.cluster-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.cluster-header h4 {
  flex: 1;
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.current-badge {
  background: #27ae60;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.cluster-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.info-item {
  display: flex;
  gap: 8px;
}

.info-item .label {
  color: #7f8c8d;
  min-width: 70px;
}

.info-item .value {
  color: #2c3e50;
  font-family: 'Courier New', monospace;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.selected-count {
  color: #7f8c8d;
  font-size: 14px;
}

.command-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 24px;
}

.command-input-group {
  margin-bottom: 20px;
}

.command-input-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2c3e50;
}

.command-templates {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-template {
  padding: 8px 16px;
  background: #ecf0f1;
  border: 2px solid #bdc3c7;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-template:hover {
  background: #d5dbdb;
  border-color: #95a5a6;
}

.btn-template.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.command-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.3s;
}

.command-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.command-textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.command-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  padding: 12px 24px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 24px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.results-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.result-stats {
  display: flex;
  gap: 16px;
}

.stat {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.stat.success {
  background: #d5f4e6;
  color: #27ae60;
}

.stat.failed {
  background: #fadbd8;
  color: #e74c3c;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.result-card.success {
  border-color: #27ae60;
  background: #f8fff8;
}

.result-card.failed {
  border-color: #e74c3c;
  background: #fff8f8;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.execution-time {
  color: #95a5a6;
  font-size: 13px;
}

.result-command {
  margin-bottom: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.result-output {
  margin-top: 12px;
}

.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.btn-copy {
  padding: 4px 12px;
  background: #ecf0f1;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.btn-copy:hover {
  background: #d5dbdb;
}

.result-output pre {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}
</style>
