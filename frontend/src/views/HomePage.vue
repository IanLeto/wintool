<template>
  <div class="home-page">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <h1 class="title">
          <span class="title-icon">🛠️</span>
          Wintool
        </h1>
        <p class="subtitle">强大的文件处理工具集合</p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <!-- Search Bar -->
        <div class="search-section">
          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索工具..."
              class="search-input"
            />
          </div>
        </div>

        <!-- Tools by Category -->
        <div class="categories-container">
          <CategorySection
            v-for="category in filteredCategories"
            :key="category"
            :category="category"
            :tools="getToolsByCategory(category)"
            @tool-click="navigateToTool"
          />
        </div>

        <!-- Empty State -->
        <div v-if="filteredCategories.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <p class="empty-text">未找到匹配的工具</p>
          <p class="empty-hint">试试其他关键词</p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p class="footer-text">
        Made with ❤️ by Wintool Team
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToolStore } from '../stores/toolStore'
import CategorySection from '../components/CategorySection.vue'

const router = useRouter()
const toolStore = useToolStore()

const searchQuery = ref('')

// 过滤后的分类
const filteredCategories = computed(() => {
  if (!searchQuery.value.trim()) {
    return toolStore.categories
  }
  
  const query = searchQuery.value.toLowerCase()
  const matchedTools = toolStore.tools.filter(tool =>
    tool.name.toLowerCase().includes(query) ||
    tool.description.toLowerCase().includes(query)
  )
  
  return [...new Set(matchedTools.map(tool => tool.category))]
})

// 获取分类下的工具（考虑搜索过滤）
const getToolsByCategory = (category) => {
  let tools = toolStore.toolsByCategory[category] || []
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    tools = tools.filter(tool =>
      tool.name.toLowerCase().includes(query) ||
      tool.description.toLowerCase().includes(query)
    )
  }
  
  return tools
}

// 导航到工具页面
const navigateToTool = (tool) => {
  toolStore.setCurrentTool(tool.id)
  router.push({ name: 'Tool', params: { id: tool.id } })
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Header */
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 2rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  font-size: 2.5rem;
}

.subtitle {
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

/* Search Section */
.search-section {
  margin-bottom: 3rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.search-box:focus-within {
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
  transform: translateY(-2px);
}

.search-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
  color: #1f2937;
}

.search-input::placeholder {
  color: #9ca3af;
}

/* Categories Container */
.categories-container {
  animation: fadeIn 0.5s ease;
}

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

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
}

.empty-hint {
  margin: 0;
  font-size: 1rem;
  color: #6b7280;
}

/* Footer */
.footer {
  background: white;
  padding: 2rem 0;
  text-align: center;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.footer-text {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    padding: 1.5rem 0;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .title-icon {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .main-content {
    padding: 2rem 0;
  }
  
  .container {
    padding: 0 1rem;
  }
  
  .search-section {
    margin-bottom: 2rem;
  }
}
</style>
