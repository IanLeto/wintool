# -*- coding: utf-8 -*-
"""
工具：命令片段管理 — 管理常用的SQL、PromQL、Shell等命令片段
简单易用，专注于快速查找和复制常用命令
"""
from __future__ import annotations

import html
import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_FILE = os.path.join(_PROJECT_ROOT, "data", "command_snippets.json")


def _ensure_data():
    """确保数据文件存在"""
    if not os.path.exists(_DATA_FILE):
        default_data = {
            "snippets": [
                {
                    "id": "example_sql",
                    "title": "示例SQL查询",
                    "type": "sql",
                    "content": "SELECT * FROM users WHERE created_at > '2024-01-01' LIMIT 10;",
                    "tags": ["查询", "用户"],
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        try:
            os.makedirs(os.path.dirname(_DATA_FILE), exist_ok=True)
            with open(_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass


def _load_snippets():
    """加载所有命令片段"""
    _ensure_data()
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("snippets", [])
    except (OSError, json.JSONDecodeError):
        return []


def _save_snippets(snippets):
    """保存命令片段"""
    try:
        with open(_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"snippets": snippets}, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


class CommandSnippetsTool(BaseTool):
    TOOL_ID = "command_snippets"
    TOOL_NAME = "命令片段"

    @classmethod
    def get_form_html(cls) -> str:
        return f"""
        <div class="tool-form command-snippets-form" data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">
                管理常用的SQL、PromQL、Shell等命令片段。快速保存和复制常用命令。
            </p>
            
            <div class="snippets-toolbar">
                <button type="button" class="snippets-add-btn">+ 新建片段</button>
                <input type="search" class="snippets-search" placeholder="搜索标题、标签或内容..." autocomplete="off" />
                <select class="snippets-filter-type">
                    <option value="">全部类型</option>
                    <option value="sql">SQL</option>
                    <option value="promql">PromQL</option>
                    <option value="shell">Shell</option>
                    <option value="other">其他</option>
                </select>
            </div>

            <div class="snippets-container">
                <div class="snippets-list">
                    <p class="snippets-loading">加载中...</p>
                </div>
            </div>

            <!-- 新建/编辑对话框 -->
            <div class="snippets-modal" style="display:none;">
                <div class="snippets-modal-content">
                    <h3 class="snippets-modal-title">新建命令片段</h3>
                    <form class="snippets-form">
                        <input type="hidden" class="snippets-id" />
                        
                        <label>
                            标题 <span style="color:red">*</span>
                            <input type="text" class="snippets-title" placeholder="例如：查询用户列表" required />
                        </label>

                        <label>
                            类型
                            <select class="snippets-type">
                                <option value="sql">SQL</option>
                                <option value="promql">PromQL</option>
                                <option value="shell">Shell</option>
                                <option value="other">其他</option>
                            </select>
                        </label>

                        <label>
                            命令内容 <span style="color:red">*</span>
                            <textarea class="snippets-content" rows="8" placeholder="粘贴你的命令..." required></textarea>
                        </label>

                        <label>
                            标签 <small>(用逗号分隔)</small>
                            <input type="text" class="snippets-tags" placeholder="例如：查询,用户,生产环境" />
                        </label>

                        <div class="snippets-modal-actions">
                            <button type="submit" class="snippets-save-btn">保存</button>
                            <button type="button" class="snippets-cancel-btn">取消</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <style>
        .command-snippets-form {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .snippets-toolbar {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .snippets-add-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .snippets-search {{
            flex: 1;
            min-width: 200px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .snippets-filter-type {{
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .snippets-container {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
        }}
        .snippets-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}
        .snippet-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            transition: box-shadow 0.2s;
        }}
        .snippet-card:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .snippet-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        .snippet-title {{
            font-weight: bold;
            font-size: 14px;
            color: #333;
        }}
        .snippet-type {{
            background: #2196F3;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .snippet-type.sql {{ background: #2196F3; }}
        .snippet-type.promql {{ background: #FF9800; }}
        .snippet-type.shell {{ background: #4CAF50; }}
        .snippet-type.other {{ background: #9E9E9E; }}
        .snippet-content {{
            background: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 100px;
            overflow: hidden;
            margin-bottom: 10px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .snippet-tags {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}
        .snippet-tag {{
            background: #E3F2FD;
            color: #1976D2;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }}
        .snippet-actions {{
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }}
        .snippet-btn {{
            padding: 4px 12px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }}
        .snippet-copy {{
            background: #4CAF50;
            color: white;
        }}
        .snippet-edit {{
            background: #2196F3;
            color: white;
        }}
        .snippet-delete {{
            background: #f44336;
            color: white;
        }}
        .snippets-modal {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .snippets-modal-content {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .snippets-modal-title {{
            margin-top: 0;
            margin-bottom: 20px;
        }}
        .snippets-form label {{
            display: block;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        .snippets-form input[type="text"],
        .snippets-form select,
        .snippets-form textarea {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 5px;
            box-sizing: border-box;
        }}
        .snippets-form textarea {{
            font-family: 'Courier New', monospace;
            resize: vertical;
        }}
        .snippets-modal-actions {{
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }}
        .snippets-save-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .snippets-cancel-btn {{
            background: #9E9E9E;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .snippets-loading {{
            text-align: center;
            color: #666;
        }}
        </style>

        <script>
        (function() {{
            const toolId = '{html.escape(cls.TOOL_ID)}';
            let snippets = [];
            let currentFilter = '';
            let currentType = '';

            function loadSnippets() {{
                fetch(`/api/tools/${{toolId}}/list`)
                    .then(r => r.json())
                    .then(data => {{
                        if (data.ok) {{
                            snippets = data.snippets;
                            renderSnippets();
                        }}
                    }});
            }}

            function renderSnippets() {{
                const container = document.querySelector('.snippets-list');
                let filtered = snippets;

                if (currentFilter) {{
                    const search = currentFilter.toLowerCase();
                    filtered = filtered.filter(s => 
                        s.title.toLowerCase().includes(search) ||
                        s.content.toLowerCase().includes(search) ||
                        (s.tags && s.tags.some(t => t.toLowerCase().includes(search)))
                    );
                }}

                if (currentType) {{
                    filtered = filtered.filter(s => s.type === currentType);
                }}

                if (filtered.length === 0) {{
                    container.innerHTML = '<p class="snippets-loading">暂无命令片段</p>';
                    return;
                }}

                container.innerHTML = filtered.map(s => `
                    <div class="snippet-card" data-id="${{s.id}}">
                        <div class="snippet-header">
                            <div class="snippet-title">${{escapeHtml(s.title)}}</div>
                            <div class="snippet-type ${{s.type}}">${{s.type}}</div>
                        </div>
                        <div class="snippet-content">${{escapeHtml(s.content)}}</div>
                        ${{s.tags && s.tags.length ? `
                            <div class="snippet-tags">
                                ${{s.tags.map(t => `<span class="snippet-tag">${{escapeHtml(t)}}</span>`).join('')}}
                            </div>
                        ` : ''}}
                        <div class="snippet-actions">
                            <button class="snippet-btn snippet-copy" onclick="copySnippet('${{s.id}}')">复制</button>
                            <button class="snippet-btn snippet-edit" onclick="editSnippet('${{s.id}}')">编辑</button>
                            <button class="snippet-btn snippet-delete" onclick="deleteSnippet('${{s.id}}')">删除</button>
                        </div>
                    </div>
                `).join('');
            }}

            function escapeHtml(text) {{
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }}

            window.copySnippet = function(id) {{
                const snippet = snippets.find(s => s.id === id);
                if (snippet) {{
                    navigator.clipboard.writeText(snippet.content).then(() => {{
                        alert('已复制到剪贴板！');
                    }});
                }}
            }};

            window.editSnippet = function(id) {{
                const snippet = snippets.find(s => s.id === id);
                if (snippet) {{
                    document.querySelector('.snippets-id').value = snippet.id;
                    document.querySelector('.snippets-title').value = snippet.title;
                    document.querySelector('.snippets-type').value = snippet.type;
                    document.querySelector('.snippets-content').value = snippet.content;
                    document.querySelector('.snippets-tags').value = snippet.tags ? snippet.tags.join(', ') : '';
                    document.querySelector('.snippets-modal-title').textContent = '编辑命令片段';
                    document.querySelector('.snippets-modal').style.display = 'flex';
                }}
            }};

            window.deleteSnippet = function(id) {{
                if (confirm('确定要删除这个命令片段吗？')) {{
                    fetch(`/api/tools/${{toolId}}/delete`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ id }})
                    }})
                    .then(r => r.json())
                    .then(data => {{
                        if (data.ok) {{
                            loadSnippets();
                        }} else {{
                            alert('删除失败：' + data.error);
                        }}
                    }});
                }}
            }};

            document.querySelector('.snippets-add-btn').addEventListener('click', () => {{
                document.querySelector('.snippets-form').reset();
                document.querySelector('.snippets-id').value = '';
                document.querySelector('.snippets-modal-title').textContent = '新建命令片段';
                document.querySelector('.snippets-modal').style.display = 'flex';
            }});

            document.querySelector('.snippets-cancel-btn').addEventListener('click', () => {{
                document.querySelector('.snippets-modal').style.display = 'none';
            }});

            document.querySelector('.snippets-form').addEventListener('submit', (e) => {{
                e.preventDefault();
                const id = document.querySelector('.snippets-id').value;
                const title = document.querySelector('.snippets-title').value;
                const type = document.querySelector('.snippets-type').value;
                const content = document.querySelector('.snippets-content').value;
                const tagsStr = document.querySelector('.snippets-tags').value;
                const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(t => t) : [];

                fetch(`/api/tools/${{toolId}}/save`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ id, title, type, content, tags }})
                }})
                .then(r => r.json())
                .then(data => {{
                    if (data.ok) {{
                        document.querySelector('.snippets-modal').style.display = 'none';
                        loadSnippets();
                    }} else {{
                        alert('保存失败：' + data.error);
                    }}
                }});
            }});

            document.querySelector('.snippets-search').addEventListener('input', (e) => {{
                currentFilter = e.target.value;
                renderSnippets();
            }});

            document.querySelector('.snippets-filter-type').addEventListener('change', (e) => {{
                currentType = e.target.value;
                renderSnippets();
            }});

            loadSnippets();
        }})();
        </script>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/list", methods=["GET"])
        def list_snippets():
            snippets = _load_snippets()
            return jsonify({"ok": True, "snippets": snippets})

        @bp.route("/save", methods=["POST"])
        def save_snippet():
            data = request.get_json(silent=True) or {}
            snippet_id = data.get("id", "").strip()
            title = data.get("title", "").strip()
            snippet_type = data.get("type", "other").strip()
            content = data.get("content", "").strip()
            tags = data.get("tags", [])

            if not title or not content:
                return jsonify({"ok": False, "error": "标题和内容不能为空"}), 400

            snippets = _load_snippets()

            if snippet_id:
                # 更新现有片段
                for s in snippets:
                    if s["id"] == snippet_id:
                        s["title"] = title
                        s["type"] = snippet_type
                        s["content"] = content
                        s["tags"] = tags
                        s["updated_at"] = datetime.now().isoformat()
                        break
            else:
                # 新建片段
                new_id = f"snippet_{int(datetime.now().timestamp() * 1000)}"
                snippets.append({
                    "id": new_id,
                    "title": title,
                    "type": snippet_type,
                    "content": content,
                    "tags": tags,
                    "created_at": datetime.now().isoformat()
                })

            if _save_snippets(snippets):
                return jsonify({"ok": True})
            else:
                return jsonify({"ok": False, "error": "保存失败"}), 500

        @bp.route("/delete", methods=["POST"])
        def delete_snippet():
            data = request.get_json(silent=True) or {}
            snippet_id = data.get("id", "").strip()

            if not snippet_id:
                return jsonify({"ok": False, "error": "ID不能为空"}), 400

            snippets = _load_snippets()
            snippets = [s for s in snippets if s["id"] != snippet_id]

            if _save_snippets(snippets):
                return jsonify({"ok": True})
            else:
                return jsonify({"ok": False, "error": "删除失败"}), 500
