<template>
  <div class="category-section">
    <h2 class="category-title">
      <span class="category-icon">{{ getCategoryIcon(category) }}</span>
      {{ category }}
    </h2>
    <div class="tools-grid">
      <ToolCard
        v-for="tool in tools"
        :key="tool.id"
        :tool="tool"
        @click="handleToolClick"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import ToolCard from './ToolCard.vue'

const props = defineProps({
  category: {
    type: String,
    required: true
  },
  tools: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['tool-click'])

const getCategoryIcon = (category) => {
  const icons = {
    '文件处理': '📂',
    '数据管理': '💾',
    '开发工具': '🛠️',
    '工具': '🔧',
    '生活': '🏠',
    '信息查询': '🔍'
  }
  return icons[category] || '📌'
}

const handleToolClick = (tool) => {
  emit('tool-click', tool)
}
</script>

<style scoped>
.category-section {
  margin-bottom: 3rem;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.category-icon {
  font-size: 1.75rem;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .category-title {
    font-size: 1.25rem;
  }
}
</style>
