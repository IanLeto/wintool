<template>
  <div class="tool-card" @click="handleClick">
    <div class="tool-icon">{{ tool.icon }}</div>
    <div class="tool-content">
      <h3 class="tool-name">{{ tool.name }}</h3>
      <p class="tool-description">{{ tool.description }}</p>
    </div>
    <div class="tool-arrow">→</div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  tool: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click', props.tool)
}
</script>

<style scoped>
.tool-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tool-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: #6366f1;
}

.tool-card:hover::before {
  opacity: 1;
}

.tool-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  z-index: 1;
}

.tool-content {
  flex: 1;
  z-index: 1;
}

.tool-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.tool-description {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.tool-arrow {
  font-size: 1.5rem;
  color: #9ca3af;
  flex-shrink: 0;
  transition: all 0.3s ease;
  z-index: 1;
}

.tool-card:hover .tool-arrow {
  color: #6366f1;
  transform: translateX(4px);
}
</style>
