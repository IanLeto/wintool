<template>
  <div class="prototype-viewer">
    <div class="header">
      <h1>🎨 原型预览</h1>
      <p>点击下方链接查看原型文件</p>
    </div>

    <div class="content">
      <div class="link-list">
        <a href="/prototypes/example.html" target="_blank" class="link-item">
          📄 example.html - 示例原型
        </a>
        
        <!-- 在这里添加更多原型链接 -->
        <!-- <a href="/prototypes/your-prototype.html" target="_blank" class="link-item">
          📄 your-prototype.html - 你的原型描述
        </a> -->
      </div>

      <div class="help">
        <h3>� 使用说明</h3>
        <ul>
          <li>将 HTML 文件放入 <code>prototypes/</code> 目录</li>
          <li>在上方列表中添加对应的链接</li>
          <li>点击链接即可在新标签页打开</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prototype-viewer {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.header p {
  font-size: 1.125rem;
  color: #6b7280;
  margin: 0;
}

.content {
  max-width: 800px;
  margin: 0 auto;
}

.link-list {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.link-item {
  display: block;
  padding: 1.25rem 1.5rem;
  margin-bottom: 0.75rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  color: #1f2937;
  text-decoration: none;
  font-size: 1.125rem;
  transition: all 0.2s;
}

.link-item:last-child {
  margin-bottom: 0;
}

.link-item:hover {
  background: white;
  border-color: #6366f1;
  color: #6366f1;
  transform: translateX(8px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
}

.help {
  background: #fef3c7;
  border: 2px solid #fbbf24;
  border-radius: 1rem;
  padding: 1.5rem;
}

.help h3 {
  margin: 0 0 1rem 0;
  color: #92400e;
  font-size: 1.125rem;
}

.help ul {
  margin: 0;
  padding-left: 1.5rem;
  color: #78350f;
}

.help li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.help code {
  background: #fde68a;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .prototype-viewer {
    padding: 1rem;
  }

  .header h1 {
    font-size: 2rem;
  }

  .link-list {
    padding: 1rem;
  }

  .link-item {
    font-size: 1rem;
    padding: 1rem;
  }
}
</style>
