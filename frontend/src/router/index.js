import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/tool/:id',
    name: 'Tool',
    component: () => import('../views/ToolPage.vue'),
    props: true
  },
  {
    path: '/tools/directory-export',
    name: 'DirectoryExport',
    component: () => import('../views/tools/DirectoryExportTool.vue')
  },
  {
    path: '/tools/code-snippets',
    name: 'CodeSnippets',
    component: () => import('../views/tools/CodeSnippetsTool.vue')
  },
  {
    path: '/tools/k8s-cluster',
    name: 'K8sCluster',
    component: () => import('../views/tools/K8sClusterTool.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
