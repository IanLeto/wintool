# -*- coding: utf-8 -*-
"""
代码片段管理工具
用于存储和管理内外网传输的代码片段
"""
import os
import json
from datetime import datetime
from pathlib import Path
from flask import request, jsonify
from tools.base import BaseTool


class CodeSnippetsTool(BaseTool):
    TOOL_ID = "code_snippets"
    TOOL_NAME = "代码片段管理"
    
    # 数据存储目录（不会被 git 追踪）
    SNIPPETS_DIR = Path(__file__).parent.parent / "code_snippets"
    
    @classmethod
    def get_form_html(cls):
        return """
        <style>
            .snippet-container {
                display: flex;
                gap: 20px;
                height: calc(100vh - 200px);
            }
            .snippet-list {
                width: 300px;
                border-right: 1px solid #30363d;
                overflow-y: auto;
            }
            .snippet-detail {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .snippet-item {
                padding: 12px;
                border-bottom: 1px solid #30363d;
                cursor: pointer;
                transition: background 0.2s;
            }
            .snippet-item:hover {
                background: #161b22;
            }
            .snippet-item.active {
                background: #1f6feb;
            }
            .snippet-title {
                font-weight: bold;
                margin-bottom: 4px;
            }
            .snippet-meta {
                font-size: 12px;
                color: #8b949e;
            }
            .snippet-editor {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .snippet-editor textarea {
                flex: 1;
                font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 13px;
                padding: 12px;
                background: #0d1117;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 6px;
                resize: none;
            }
            .snippet-actions {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            .snippet-form {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-bottom: 20px;
            }
            .snippet-form input, .snippet-form select {
                padding: 8px;
                background: #0d1117;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            .btn {
                padding: 8px 16px;
                background: #238636;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            .btn:hover {
                background: #2ea043;
            }
            .btn-secondary {
                background: #21262d;
            }
            .btn-secondary:hover {
                background: #30363d;
            }
            .btn-danger {
                background: #da3633;
            }
            .btn-danger:hover {
                background: #f85149;
            }
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #8b949e;
            }
            .search-box {
                padding: 12px;
                border-bottom: 1px solid #30363d;
            }
            .search-box input {
                width: 100%;
                padding: 8px;
                background: #0d1117;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            .tag-badge {
                display: inline-block;
                padding: 2px 8px;
                background: #1f6feb;
                color: white;
                border-radius: 12px;
                font-size: 11px;
                margin-right: 4px;
            }
        </style>
        
        <div class="snippet-container">
            <!-- 左侧列表 -->
            <div class="snippet-list">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="搜索片段..." />
                </div>
                <div id="snippet-list-content"></div>
            </div>
            
            <!-- 右侧详情 -->
            <div class="snippet-detail">
                <div id="snippet-editor" style="display: none;">
                    <div class="snippet-form">
                        <input type="text" id="snippet-title" placeholder="片段标题" />
                        <input type="text" id="snippet-language" placeholder="语言（如: python, bash, sql）" />
                        <input type="text" id="snippet-tags" placeholder="标签（逗号分隔）" />
                        <select id="snippet-direction">
                            <option value="intranet_to_internet">内网 → 外网</option>
                            <option value="internet_to_intranet">外网 → 内网</option>
                            <option value="bidirectional">双向</option>
                        </select>
                    </div>
                    
                    <textarea id="snippet-content" placeholder="粘贴代码片段..."></textarea>
                    
                    <div class="snippet-actions">
                        <button class="btn" onclick="saveSnippet()">保存</button>
                        <button class="btn btn-secondary" onclick="copySnippet()">复制代码</button>
                        <button class="btn btn-danger" onclick="deleteSnippet()">删除</button>
                        <button class="btn btn-secondary" onclick="newSnippet()">新建</button>
                    </div>
                </div>
                
                <div id="empty-state" class="empty-state">
                    <h3>📝 代码片段管理</h3>
                    <p>选择左侧片段查看，或点击下方按钮创建新片段</p>
                    <button class="btn" onclick="newSnippet()">创建新片段</button>
                </div>
            </div>
        </div>
        
        <script>
        let currentSnippet = null;
        let snippets = [];
        
        // 加载片段列表
        async function loadSnippets() {
            try {
                const res = await fetch('/api/tools/code_snippets/list');
                const data = await res.json();
                if (data.ok) {
                    snippets = data.snippets;
                    renderSnippetList();
                }
            } catch (err) {
                console.error('加载失败:', err);
            }
        }
        
        // 渲染片段列表
        function renderSnippetList(filter = '') {
            const container = document.getElementById('snippet-list-content');
            const filtered = snippets.filter(s => 
                s.title.toLowerCase().includes(filter.toLowerCase()) ||
                s.language.toLowerCase().includes(filter.toLowerCase()) ||
                s.tags.some(t => t.toLowerCase().includes(filter.toLowerCase()))
            );
            
            if (filtered.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>暂无片段</p></div>';
                return;
            }
            
            container.innerHTML = filtered.map(s => `
                <div class="snippet-item ${currentSnippet && currentSnippet.id === s.id ? 'active' : ''}" 
                     onclick="loadSnippet('${s.id}')">
                    <div class="snippet-title">${escapeHtml(s.title)}</div>
                    <div class="snippet-meta">
                        ${s.tags.map(t => `<span class="tag-badge">${escapeHtml(t)}</span>`).join('')}
                        <br>${s.language} · ${s.updated_at}
                    </div>
                </div>
            `).join('');
        }
        
        // 加载单个片段
        async function loadSnippet(id) {
            try {
                const res = await fetch(`/api/tools/code_snippets/get/${id}`);
                const data = await res.json();
                if (data.ok) {
                    currentSnippet = data.snippet;
                    showEditor();
                    document.getElementById('snippet-title').value = currentSnippet.title;
                    document.getElementById('snippet-language').value = currentSnippet.language;
                    document.getElementById('snippet-tags').value = currentSnippet.tags.join(', ');
                    document.getElementById('snippet-direction').value = currentSnippet.direction;
                    document.getElementById('snippet-content').value = currentSnippet.content;
                    renderSnippetList();
                }
            } catch (err) {
                console.error('加载失败:', err);
            }
        }
        
        // 保存片段
        async function saveSnippet() {
            const title = document.getElementById('snippet-title').value.trim();
            const language = document.getElementById('snippet-language').value.trim();
            const tags = document.getElementById('snippet-tags').value.split(',').map(t => t.trim()).filter(t => t);
            const direction = document.getElementById('snippet-direction').value;
            const content = document.getElementById('snippet-content').value;
            
            if (!title || !content) {
                alert('请填写标题和内容');
                return;
            }
            
            try {
                const res = await fetch('/api/tools/code_snippets/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        id: currentSnippet ? currentSnippet.id : null,
                        title, language, tags, direction, content
                    })
                });
                
                const data = await res.json();
                if (data.ok) {
                    alert('保存成功');
                    await loadSnippets();
                    if (data.snippet) {
                        await loadSnippet(data.snippet.id);
                    }
                } else {
                    alert('保存失败: ' + data.error);
                }
            } catch (err) {
                alert('保存失败: ' + err.message);
            }
        }
        
        // 复制代码
        function copySnippet() {
            const content = document.getElementById('snippet-content').value;
            navigator.clipboard.writeText(content).then(() => {
                alert('已复制到剪贴板');
            });
        }
        
        // 删除片段
        async function deleteSnippet() {
            if (!currentSnippet) return;
            
            if (!confirm(`确定删除片段"${currentSnippet.title}"？`)) {
                return;
            }
            
            try {
                const res = await fetch(`/api/tools/code_snippets/delete/${currentSnippet.id}`, {
                    method: 'DELETE'
                });
                
                const data = await res.json();
                if (data.ok) {
                    alert('删除成功');
                    currentSnippet = null;
                    hideEditor();
                    await loadSnippets();
                } else {
                    alert('删除失败: ' + data.error);
                }
            } catch (err) {
                alert('删除失败: ' + err.message);
            }
        }
        
        // 新建片段
        function newSnippet() {
            currentSnippet = null;
            showEditor();
            document.getElementById('snippet-title').value = '';
            document.getElementById('snippet-language').value = 'python';
            document.getElementById('snippet-tags').value = '';
            document.getElementById('snippet-direction').value = 'intranet_to_internet';
            document.getElementById('snippet-content').value = '';
            renderSnippetList();
        }
        
        // 显示编辑器
        function showEditor() {
            document.getElementById('snippet-editor').style.display = 'flex';
            document.getElementById('empty-state').style.display = 'none';
        }
        
        // 隐藏编辑器
        function hideEditor() {
            document.getElementById('snippet-editor').style.display = 'none';
            document.getElementById('empty-state').style.display = 'block';
        }
        
        // HTML 转义
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 搜索
        document.getElementById('search-input').addEventListener('input', (e) => {
            renderSnippetList(e.target.value);
        });
        
        // 初始化
        loadSnippets();
        </script>
        """
    
    @classmethod
    def register_routes(cls, bp):
        # 确保数据目录存在
        cls.SNIPPETS_DIR.mkdir(exist_ok=True)
        
        @bp.route("/list", methods=["GET"])
        def list_snippets():
            """获取所有片段列表"""
            try:
                snippets = []
                for file in cls.SNIPPETS_DIR.glob("*.json"):
                    with open(file, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        snippets.append({
                            'id': snippet['id'],
                            'title': snippet['title'],
                            'language': snippet['language'],
                            'tags': snippet['tags'],
                            'direction': snippet['direction'],
                            'updated_at': snippet['updated_at']
                        })
                
                # 按更新时间倒序排序
                snippets.sort(key=lambda x: x['updated_at'], reverse=True)
                
                return jsonify({"ok": True, "snippets": snippets})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/get/<snippet_id>", methods=["GET"])
        def get_snippet(snippet_id):
            """获取单个片段详情"""
            try:
                file_path = cls.SNIPPETS_DIR / f"{snippet_id}.json"
                if not file_path.exists():
                    return jsonify({"ok": False, "error": "片段不存在"})
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    snippet = json.load(f)
                
                return jsonify({"ok": True, "snippet": snippet})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/save", methods=["POST"])
        def save_snippet():
            """保存片段"""
            try:
                data = request.get_json()
                snippet_id = data.get('id')
                
                # 生成 ID
                if not snippet_id:
                    snippet_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                snippet = {
                    'id': snippet_id,
                    'title': data.get('title', ''),
                    'language': data.get('language', 'text'),
                    'tags': data.get('tags', []),
                    'direction': data.get('direction', 'intranet_to_internet'),
                    'content': data.get('content', ''),
                    'created_at': data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                file_path = cls.SNIPPETS_DIR / f"{snippet_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(snippet, f, ensure_ascii=False, indent=2)
                
                return jsonify({"ok": True, "snippet": snippet})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
        
        @bp.route("/delete/<snippet_id>", methods=["DELETE"])
        def delete_snippet(snippet_id):
            """删除片段"""
            try:
                file_path = cls.SNIPPETS_DIR / f"{snippet_id}.json"
                if not file_path.exists():
                    return jsonify({"ok": False, "error": "片段不存在"})
                
                file_path.unlink()
                return jsonify({"ok": True})
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})
