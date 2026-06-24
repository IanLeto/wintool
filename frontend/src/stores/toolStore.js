import { defineStore } from 'pinia'

export const useToolStore = defineStore('tool', {
  state: () => ({
    tools: [
      {
        id: 'batch-extract',
        name: '批量解压工具',
        description: '批量解压 7z 和 zip 文件',
        icon: '📦',
        category: '文件处理'
      },
      {
        id: 'export-dir',
        name: '目录结构导出',
        description: '导出目录结构为文本或 JSON',
        icon: '📁',
        category: '文件处理'
      },
      {
        id: 'flatten-files',
        name: '文件扁平化',
        description: '将嵌套目录中的文件移到同一层级',
        icon: '📄',
        category: '文件处理'
      },
      {
        id: 'rename-by-json',
        name: 'JSON 批量重命名',
        description: '根据 JSON 配置批量重命名文件',
        icon: '✏️',
        category: '文件处理'
      },
      {
        id: 'media-shelf',
        name: '影视收藏管理',
        description: '管理和浏览影视收藏',
        icon: '🎬',
        category: '数据管理'
      },
      {
        id: 'prompt-bank',
        name: 'AI 提示词库',
        description: '管理和使用 AI 提示词',
        icon: '💡',
        category: '数据管理'
      },
      {
        id: 'password-manager',
        name: '密码管理器',
        description: '安全存储和管理密码',
        icon: '🔐',
        category: '数据管理'
      },
      {
        id: 'command-snippets',
        name: '命令片段库',
        description: '保存和快速使用常用命令',
        icon: '⌨️',
        category: '开发工具'
      },
      {
        id: 'code-snippets',
        name: '代码片段库',
        description: '保存和管理代码片段',
        icon: '💻',
        category: '开发工具'
      },
      {
        id: 'k8s-cluster',
        name: 'K8s 集群管理',
        description: '管理多个 Kubernetes 集群，批量执行命令',
        icon: '🚢',
        category: '开发工具'
      },
      {
        id: 'kafka-consumer',
        name: 'Kafka 消费工具',
        description: '连接内网 Kafka 集群，消费消息数据（支持 SASL 认证）',
        icon: '📨',
        category: '开发工具'
      },
      {
        id: 'text-viewer',
        name: '文本查看器',
        description: '查看和编辑文本文档',
        icon: '📝',
        category: '工具'
      },
      {
        id: 'body-weight',
        name: '体重记录',
        description: '记录和追踪体重变化',
        icon: '⚖️',
        category: '生活'
      },
      {
        id: 'provincial-exam',
        name: '省考信息查询',
        description: '查询公务员考试信息',
        icon: '📚',
        category: '信息查询'
      }
    ],
    currentTool: null
  }),

  getters: {
    // 按分类分组工具
    toolsByCategory: (state) => {
      const grouped = {}
      state.tools.forEach(tool => {
        if (!grouped[tool.category]) {
          grouped[tool.category] = []
        }
        grouped[tool.category].push(tool)
      })
      return grouped
    },

    // 获取所有分类
    categories: (state) => {
      return [...new Set(state.tools.map(tool => tool.category))]
    },

    // 根据 ID 获取工具
    getToolById: (state) => (id) => {
      return state.tools.find(tool => tool.id === id)
    }
  },

  actions: {
    setCurrentTool(toolId) {
      this.currentTool = this.getToolById(toolId)
    }
  }
})
