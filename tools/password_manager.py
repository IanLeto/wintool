# -*- coding: utf-8 -*-
"""
工具：密码管理器 — 简单的内网账号密码管理
存储账号、密码和对应的链接，方便内网环境使用
"""
from __future__ import annotations

import html
import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_FILE = os.path.join(_PROJECT_ROOT, "data", "passwords.json")


def _ensure_data():
    """确保数据文件存在"""
    if not os.path.exists(_DATA_FILE):
        default_data = {
            "accounts": [
                {
                    "id": "example",
                    "title": "示例账号",
                    "url": "https://example.com",
                    "username": "admin",
                    "password": "password123",
                    "note": "这是一个示例",
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


def _load_accounts():
    """加载所有账号"""
    _ensure_data()
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("accounts", [])
    except (OSError, json.JSONDecodeError):
        return []


def _save_accounts(accounts):
    """保存账号"""
    try:
        with open(_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"accounts": accounts}, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


class PasswordManagerTool(BaseTool):
    TOOL_ID = "password_manager"
    TOOL_NAME = "密码管理"

    @classmethod
    def get_form_html(cls) -> str:
        return f"""
        <div class="tool-form password-manager-form" data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">
                内网账号密码管理器。数据本地存储，请妥善保管。
            </p>
            
            <div class="pwd-toolbar">
                <button type="button" class="pwd-add-btn">+ 新建账号</button>
                <input type="search" class="pwd-search" placeholder="搜索标题、用户名或备注..." autocomplete="off" />
            </div>

            <div class="pwd-container">
                <div class="pwd-list">
                    <p class="pwd-loading">加载中...</p>
                </div>
            </div>

            <!-- 新建/编辑对话框 -->
            <div class="pwd-modal" style="display:none;">
                <div class="pwd-modal-content">
                    <h3 class="pwd-modal-title">新建账号</h3>
                    <form class="pwd-form">
                        <input type="hidden" class="pwd-id" />
                        
                        <label>
                            标题 <span style="color:red">*</span>
                            <input type="text" class="pwd-title" placeholder="例如：公司OA系统" required />
                        </label>

                        <label>
                            链接
                            <input type="text" class="pwd-url" placeholder="https://..." />
                        </label>

                        <label>
                            用户名 <span style="color:red">*</span>
                            <input type="text" class="pwd-username" placeholder="用户名或邮箱" required />
                        </label>

                        <label>
                            密码 <span style="color:red">*</span>
                            <input type="password" class="pwd-password" placeholder="密码" required />
                        </label>

                        <label>
                            备注
                            <textarea class="pwd-note" rows="3" placeholder="其他说明..."></textarea>
                        </label>

                        <div class="pwd-modal-actions">
                            <button type="submit" class="pwd-save-btn">保存</button>
                            <button type="button" class="pwd-cancel-btn">取消</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <style>
        .password-manager-form {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .pwd-toolbar {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .pwd-add-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .pwd-search {{
            flex: 1;
            min-width: 200px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .pwd-container {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
        }}
        .pwd-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}
        .pwd-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            transition: box-shadow 0.2s;
        }}
        .pwd-card:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .pwd-card-title {{
            font-weight: bold;
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
        }}
        .pwd-field {{
            margin-bottom: 8px;
            font-size: 13px;
        }}
        .pwd-field-label {{
            color: #666;
            font-weight: 500;
            margin-right: 5px;
        }}
        .pwd-field-value {{
            color: #333;
        }}
        .pwd-password-hidden {{
            color: #999;
            font-family: monospace;
        }}
        .pwd-url-link {{
            color: #2196F3;
            text-decoration: none;
        }}
        .pwd-url-link:hover {{
            text-decoration: underline;
        }}
        .pwd-note {{
            background: #f9f9f9;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 8px;
            color: #666;
        }}
        .pwd-actions {{
            display: flex;
            gap: 8px;
            justify-content: flex-end;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #eee;
        }}
        .pwd-btn {{
            padding: 4px 12px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }}
        .pwd-copy-username {{
            background: #2196F3;
            color: white;
        }}
        .pwd-copy-password {{
            background: #4CAF50;
            color: white;
        }}
        .pwd-show-password {{
            background: #FF9800;
            color: white;
        }}
        .pwd-edit {{
            background: #9C27B0;
            color: white;
        }}
        .pwd-delete {{
            background: #f44336;
            color: white;
        }}
        .pwd-modal {{
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
        .pwd-modal-content {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .pwd-modal-title {{
            margin-top: 0;
            margin-bottom: 20px;
        }}
        .pwd-form label {{
            display: block;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        .pwd-form input[type="text"],
        .pwd-form input[type="password"],
        .pwd-form textarea {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 5px;
            box-sizing: border-box;
        }}
        .pwd-form textarea {{
            resize: vertical;
        }}
        .pwd-modal-actions {{
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }}
        .pwd-save-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .pwd-cancel-btn {{
            background: #9E9E9E;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .pwd-loading {{
            text-align: center;
            color: #666;
        }}
        </style>

        <script>
        (function() {{
            const toolId = '{html.escape(cls.TOOL_ID)}';
            let accounts = [];
            let currentFilter = '';
            let shownPasswords = new Set();

            function loadAccounts() {{
                fetch(`/api/tools/${{toolId}}/list`)
                    .then(r => r.json())
                    .then(data => {{
                        if (data.ok) {{
                            accounts = data.accounts;
                            renderAccounts();
                        }}
                    }});
            }}

            function renderAccounts() {{
                const container = document.querySelector('.pwd-list');
                let filtered = accounts;

                if (currentFilter) {{
                    const search = currentFilter.toLowerCase();
                    filtered = filtered.filter(a => 
                        a.title.toLowerCase().includes(search) ||
                        a.username.toLowerCase().includes(search) ||
                        (a.note && a.note.toLowerCase().includes(search))
                    );
                }}

                if (filtered.length === 0) {{
                    container.innerHTML = '<p class="pwd-loading">暂无账号</p>';
                    return;
                }}

                container.innerHTML = filtered.map(a => `
                    <div class="pwd-card" data-id="${{a.id}}">
                        <div class="pwd-card-title">${{escapeHtml(a.title)}}</div>
                        ${{a.url ? `
                            <div class="pwd-field">
                                <span class="pwd-field-label">链接:</span>
                                <a href="${{escapeHtml(a.url)}}" target="_blank" class="pwd-url-link">${{escapeHtml(a.url)}}</a>
                            </div>
                        ` : ''}}
                        <div class="pwd-field">
                            <span class="pwd-field-label">用户名:</span>
                            <span class="pwd-field-value">${{escapeHtml(a.username)}}</span>
                        </div>
                        <div class="pwd-field">
                            <span class="pwd-field-label">密码:</span>
                            <span class="pwd-field-value pwd-password-${{a.id}}">
                                ${{shownPasswords.has(a.id) ? escapeHtml(a.password) : '••••••••'}}
                            </span>
                        </div>
                        ${{a.note ? `<div class="pwd-note">${{escapeHtml(a.note)}}</div>` : ''}}
                        <div class="pwd-actions">
                            <button class="pwd-btn pwd-copy-username" onclick="copyUsername('${{a.id}}')">复制用户名</button>
                            <button class="pwd-btn pwd-copy-password" onclick="copyPassword('${{a.id}}')">复制密码</button>
                            <button class="pwd-btn pwd-show-password" onclick="togglePassword('${{a.id}}')">
                                ${{shownPasswords.has(a.id) ? '隐藏' : '显示'}}
                            </button>
                            <button class="pwd-btn pwd-edit" onclick="editAccount('${{a.id}}')">编辑</button>
                            <button class="pwd-btn pwd-delete" onclick="deleteAccount('${{a.id}}')">删除</button>
                        </div>
                    </div>
                `).join('');
            }}

            function escapeHtml(text) {{
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }}

            window.copyUsername = function(id) {{
                const account = accounts.find(a => a.id === id);
                if (account) {{
                    navigator.clipboard.writeText(account.username).then(() => {{
                        alert('用户名已复制！');
                    }});
                }}
            }};

            window.copyPassword = function(id) {{
                const account = accounts.find(a => a.id === id);
                if (account) {{
                    navigator.clipboard.writeText(account.password).then(() => {{
                        alert('密码已复制！');
                    }});
                }}
            }};

            window.togglePassword = function(id) {{
                if (shownPasswords.has(id)) {{
                    shownPasswords.delete(id);
                }} else {{
                    shownPasswords.add(id);
                }}
                renderAccounts();
            }};

            window.editAccount = function(id) {{
                const account = accounts.find(a => a.id === id);
                if (account) {{
                    document.querySelector('.pwd-id').value = account.id;
                    document.querySelector('.pwd-title').value = account.title;
                    document.querySelector('.pwd-url').value = account.url || '';
                    document.querySelector('.pwd-username').value = account.username;
                    document.querySelector('.pwd-password').value = account.password;
                    document.querySelector('.pwd-note').value = account.note || '';
                    document.querySelector('.pwd-modal-title').textContent = '编辑账号';
                    document.querySelector('.pwd-modal').style.display = 'flex';
                }}
            }};

            window.deleteAccount = function(id) {{
                if (confirm('确定要删除这个账号吗？')) {{
                    fetch(`/api/tools/${{toolId}}/delete`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ id }})
                    }})
                    .then(r => r.json())
                    .then(data => {{
                        if (data.ok) {{
                            shownPasswords.delete(id);
                            loadAccounts();
                        }} else {{
                            alert('删除失败：' + data.error);
                        }}
                    }});
                }}
            }};

            document.querySelector('.pwd-add-btn').addEventListener('click', () => {{
                document.querySelector('.pwd-form').reset();
                document.querySelector('.pwd-id').value = '';
                document.querySelector('.pwd-modal-title').textContent = '新建账号';
                document.querySelector('.pwd-modal').style.display = 'flex';
            }});

            document.querySelector('.pwd-cancel-btn').addEventListener('click', () => {{
                document.querySelector('.pwd-modal').style.display = 'none';
            }});

            document.querySelector('.pwd-form').addEventListener('submit', (e) => {{
                e.preventDefault();
                const id = document.querySelector('.pwd-id').value;
                const title = document.querySelector('.pwd-title').value;
                const url = document.querySelector('.pwd-url').value;
                const username = document.querySelector('.pwd-username').value;
                const password = document.querySelector('.pwd-password').value;
                const note = document.querySelector('.pwd-note').value;

                fetch(`/api/tools/${{toolId}}/save`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ id, title, url, username, password, note }})
                }})
                .then(r => r.json())
                .then(data => {{
                    if (data.ok) {{
                        document.querySelector('.pwd-modal').style.display = 'none';
                        loadAccounts();
                    }} else {{
                        alert('保存失败：' + data.error);
                    }}
                }});
            }});

            document.querySelector('.pwd-search').addEventListener('input', (e) => {{
                currentFilter = e.target.value;
                renderAccounts();
            }});

            loadAccounts();
        }})();
        </script>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/list", methods=["GET"])
        def list_accounts():
            accounts = _load_accounts()
            return jsonify({"ok": True, "accounts": accounts})

        @bp.route("/save", methods=["POST"])
        def save_account():
            data = request.get_json(silent=True) or {}
            account_id = data.get("id", "").strip()
            title = data.get("title", "").strip()
            url = data.get("url", "").strip()
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            note = data.get("note", "").strip()

            if not title or not username or not password:
                return jsonify({"ok": False, "error": "标题、用户名和密码不能为空"}), 400

            accounts = _load_accounts()

            if account_id:
                # 更新现有账号
                for a in accounts:
                    if a["id"] == account_id:
                        a["title"] = title
                        a["url"] = url
                        a["username"] = username
                        a["password"] = password
                        a["note"] = note
                        a["updated_at"] = datetime.now().isoformat()
                        break
            else:
                # 新建账号
                new_id = f"account_{int(datetime.now().timestamp() * 1000)}"
                accounts.append({
                    "id": new_id,
                    "title": title,
                    "url": url,
                    "username": username,
                    "password": password,
                    "note": note,
                    "created_at": datetime.now().isoformat()
                })

            if _save_accounts(accounts):
                return jsonify({"ok": True})
            else:
                return jsonify({"ok": False, "error": "保存失败"}), 500

        @bp.route("/delete", methods=["POST"])
        def delete_account():
            data = request.get_json(silent=True) or {}
            account_id = data.get("id", "").strip()

            if not account_id:
                return jsonify({"ok": False, "error": "ID不能为空"}), 400

            accounts = _load_accounts()
            accounts = [a for a in accounts if a["id"] != account_id]

            if _save_accounts(accounts):
                return jsonify({"ok": True})
            else:
                return jsonify({"ok": False, "error": "删除失败"}), 500
