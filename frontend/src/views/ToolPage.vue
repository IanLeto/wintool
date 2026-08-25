<template>
  <div class="tool-page">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <button class="back-button" @click="goBack">
          <span class="back-icon">←</span>
          返回首页
        </button>
        <div v-if="tool" class="tool-header">
          <span class="tool-icon-large">{{ tool.icon }}</span>
          <div class="tool-info">
            <h1 class="tool-title">{{ tool.name }}</h1>
            <p class="tool-desc">{{ tool.description }}</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <div v-if="tool" class="tool-content">
          <!-- Tool Interface Placeholder -->
          <div class="tool-interface">
            <div class="coming-soon">
              <div class="coming-soon-icon">{{ hasImplementation(tool.id) ? '✅' : '🚧' }}</div>
              <h2 class="coming-soon-title">
                {{ hasImplementation(tool.id) ? '功能已实现' : '功能开发中' }}
              </h2>
              <p class="coming-soon-text">
                {{ hasImplementation(tool.id) ? '点击下方按钮开始使用' : tool.name + ' 的具体功能正在开发中，敬请期待！' }}
              </p>
              
              <!-- 启动按钮（如果已实现） -->
              <button v-if="hasImplementation(tool.id)" class="launch-button" @click="goToTool">
                🚀 启动工具
              </button>
              
              <div class="feature-list">
                <h3 class="feature-title">{{ hasImplementation(tool.id) ? '功能特点：' : '计划功能：' }}</h3>
                <ul class="features">
                  <li v-for="feature in getPlannedFeatures(tool.id)" :key="feature">
                    {{ feature }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Tool Not Found -->
        <div v-else class="not-found">
          <div class="not-found-icon">❌</div>
          <h2 class="not-found-title">工具未找到</h2>
          <p class="not-found-text">请返回首页选择其他工具</p>
          <button class="primary-button" @click="goBack">
            返回首页
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToolStore } from '../stores/toolStore'

const router = useRouter()
const route = useRoute()
const toolStore = useToolStore()

const tool = computed(() => {
  return toolStore.getToolById(route.params.id)
})

const goBack = () => {
  router.push({ name: 'Home' })
}

const hasImplementation = (toolId) => {
  // 已实现的工具列表
  const implementedTools = ['export-dir', 'code-snippets', 'k8s-cluster', 'kafka-consumer', 'prototype-viewer', 'timestamp-converter']
  return implementedTools.includes(toolId)
}

const goToTool = () => {
  // 根据工具 ID 跳转到实际的工具页面
  const toolRoutes = {
    'export-dir': '/tools/directory-export',
    'code-snippets': '/tools/code-snippets',
    'k8s-cluster': '/tools/k8s-cluster',
    'kafka-consumer': '/tools/kafka-consumer',
    'prototype-viewer': '/tools/prototype-viewer',
    'timestamp-converter': '/tools/timestamp-converter'
  }
  
  const routePath = toolRoutes[route.params.id]
  if (routePath) {
    router.push(routePath)
  }
}

const getPlannedFeatures = (toolId) => {
  const features = {
    'batch-extract': [
      '支持批量解压 7z 和 zip 文件',
      '自动检测压缩文件编码',
      '支持密码保护的压缩文件',
      '解压进度实时显示'
    ],
    'export-dir': [
      '导出目录树结构',
      '支持多种输出格式（文本、JSON、Markdown）',
      '可配置过滤规则',
      '支持忽略特定文件/文件夹'
    ],
    'flatten-files': [
      '将嵌套目录扁平化',
      '智能处理文件名冲突',
      '支持预览操作结果',
      '可撤销操作'
    ],
    'rename-by-json': [
      '基于 JSON 配置批量重命名',
      '支持正则表达式匹配',
      '预览重命名结果',
      '批量操作日志'
    ],
    'media-shelf': [
      '管理影视收藏',
      '支持多个硬盘/存储设备',
      '快速搜索和筛选',
      '导入导出收藏列表'
    ],
    'prompt-bank': [
      'AI 提示词管理',
      '分类组织提示词',
      '快速复制和使用',
      '支持 Markdown 格式'
    ],
    'password-manager': [
      '安全存储密码',
      '加密保护',
      '快速搜索',
      '一键复制'
    ],
    'command-snippets': [
      '保存常用命令',
      '分类管理',
      '快速搜索',
      '一键执行'
    ],
    'code-snippets': [
      '✅ 卡片式展示代码片段',
      '✅ 支持 Go、Java、Python、SQL 等多种语言',
      '✅ 快速搜索和筛选',
      '✅ 一键复制代码',
      '✅ 本地存储，数据安全'
    ],
    'text-viewer': [
      '查看文本文档',
      '支持大文件',
      '语法高亮',
      '搜索功能'
    ],
    'body-weight': [
      '记录体重数据',
      '可视化图表',
      '趋势分析',
      '目标设定'
    ],
    'provincial-exam': [
      '公务员考试信息查询',
      '多省份支持',
      '实时更新',
      '收藏功能'
    ],
    'k8s-cluster': [
      '✅ 显示所有 K8s 集群',
      '✅ 批量执行 kubectl 命令',
      '✅ 7个预置命令模板',
      '✅ 实时显示执行结果',
      '✅ 成功/失败统计',
      '✅ 一键复制输出',
      '✅ 支持自定义命令',
      '✅ 完全离线部署'
    ],
    'kafka-consumer': [
      '✅ 连接内网 Kafka 集群',
      '✅ 支持 SASL 认证（用户名密码）',
      '✅ 测试连接功能',
      '✅ 消费消息数据',
      '✅ 显示分区和偏移量信息',
      '✅ JSON 格式化显示',
      '✅ 一键复制消息',
      '✅ 完全离线部署',
      '✅ 极简连接，不做多余检查'
    ],
    'prototype-viewer': [
      '✅ 扫描 prototypes/ 目录下的 HTML 文件',
      '✅ 列表展示所有原型文件',
      '✅ 点击预览原型页面',
      '✅ 支持完整的 HTML/CSS/JS',
      '✅ 文件大小和修改时间显示',
      '✅ 响应式设计',
      '✅ 快速访问原型设计'
    ],
    'timestamp-converter': [
      '✅ 支持秒/毫秒/微秒/纳秒时间戳',
      '✅ 自动识别时间戳精度',
      '✅ 支持日期字符串输入',
      '✅ 15+ 种时间格式输出',
      '✅ ISO 8601、RFC 2822 标准格式',
      '✅ 中文、美式日期格式',
      '✅ 一键复制任意格式',
      '✅ 实时转换，无需点击',
      '✅ 完全离线运行'
    ]
  }
  
  return features[toolId] || ['功能规划中...']
}
</script>

<style scoped>
.tool-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Header */
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 1.5rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.back-button:hover {
  background: #f9fafb;
  border-color: #6366f1;
  color: #6366f1;
}

.back-icon {
  font-size: 1.25rem;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.tool-icon-large {
  font-size: 4rem;
  flex-shrink: 0;
}

.tool-info {
  flex: 1;
}

.tool-title {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.tool-desc {
  margin: 0;
  font-size: 1.125rem;
  color: #6b7280;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 3rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.tool-content {
  animation: fadeIn 0.5s ease;
}

.tool-interface {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Coming Soon */
.coming-soon {
  text-align: center;
  padding: 2rem;
}

.coming-soon-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
}

.coming-soon-title {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.coming-soon-text {
  margin: 0 0 2rem 0;
  font-size: 1.125rem;
  color: #6b7280;
}

.feature-list {
  max-width: 600px;
  margin: 0 auto;
  text-align: left;
}

.feature-title {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
}

.features {
  margin: 0;
  padding-left: 1.5rem;
  list-style: none;
}

.features li {
  position: relative;
  padding: 0.5rem 0;
  color: #6b7280;
  font-size: 1rem;
}

.features li::before {
  content: '✓';
  position: absolute;
  left: -1.5rem;
  color: #10b981;
  font-weight: bold;
}

/* Not Found */
.not-found {
  text-align: center;
  padding: 4rem 2rem;
}

.not-found-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
}

.not-found-title {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.not-found-text {
  margin: 0 0 2rem 0;
  font-size: 1.125rem;
  color: #6b7280;
}

.primary-button {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

/* Launch Button */
.launch-button {
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.launch-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

.launch-button:active {
  transform: translateY(-1px);
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .tool-header {
    flex-direction: column;
    text-align: center;
  }
  
  .tool-icon-large {
    font-size: 3rem;
  }
  
  .tool-title {
    font-size: 1.5rem;
  }
  
  .tool-desc {
    font-size: 1rem;
  }
  
  .tool-interface {
    padding: 2rem 1.5rem;
  }
  
  .coming-soon-icon {
    font-size: 4rem;
  }
  
  .coming-soon-title {
    font-size: 1.5rem;
  }
}
</style>
