<template>
  <div class="tree-node">
    <div 
      :class="['node-content', { 'is-directory': node.type === 'directory' }]"
      :style="{ paddingLeft: `${level * 20}px` }"
      @click="handleClick"
    >
      <!-- 展开/折叠图标 -->
      <span v-if="node.type === 'directory' && hasChildren" class="toggle-icon">
        {{ isExpanded ? '▼' : '▶' }}
      </span>
      <span v-else class="toggle-icon-placeholder"></span>
      
      <!-- 文件/文件夹图标 -->
      <span class="node-icon">
        {{ node.type === 'directory' ? '📁' : '📄' }}
      </span>
      
      <!-- 名称 -->
      <span class="node-name">{{ node.name }}</span>
      
      <!-- 额外信息 -->
      <span v-if="node.type === 'directory' && node.childCount > 0" class="node-info">
        ({{ node.childCount }} 项)
      </span>
      <span v-if="node.type === 'file' && node.size" class="node-info">
        {{ formatSize(node.size) }}
      </span>
    </div>
    
    <!-- 子节点 -->
    <div v-if="isExpanded && hasChildren" class="node-children">
      <TreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :level="level + 1"
        :expanded-nodes="expandedNodes"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  expandedNodes: {
    type: Set,
    required: true
  }
})

const emit = defineEmits(['toggle'])

const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

const isExpanded = computed(() => {
  return props.expandedNodes.has(props.node.path)
})

const handleClick = () => {
  if (props.node.type === 'directory') {
    emit('toggle', props.node.path)
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.node-content.is-directory {
  cursor: pointer;
}

.node-content.is-directory:hover {
  background-color: rgba(99, 102, 241, 0.1);
}

.toggle-icon {
  width: 16px;
  font-size: 0.75rem;
  color: #6b7280;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.toggle-icon-placeholder {
  width: 16px;
  flex-shrink: 0;
}

.node-icon {
  font-size: 1.125rem;
  flex-shrink: 0;
}

.node-name {
  color: #374151;
  font-weight: 500;
  word-break: break-all;
}

.node-info {
  color: #9ca3af;
  font-size: 0.8rem;
  margin-left: auto;
  flex-shrink: 0;
}

.node-children {
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
