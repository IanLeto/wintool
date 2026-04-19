# -*- coding: utf-8 -*-
"""
工具：提示词收纳 — 在 data/prompt_bank/ 下用本地文件保存、浏览、编辑内容。
偏「好用」：文件名只做路径安全处理，不限制后缀；无后缀时默认 .md。
"""
from __future__ import annotations

import html
import os

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "prompt_bank")
_MAX_BYTES = 2 * 1024 * 1024
_MAX_NAME_LEN = 240
# 跨平台容易出问题的字符：替换为下划线，尽量不拦用户输入
_WIN_BAD = '<>:"/\\|?*'


def _ensure_dir():
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
    except OSError:
        pass


def _realpath_under_data(filename: str) -> str | None:
    """仅允许 data/prompt_bank 下的 basename，不校验后缀。"""
    base = os.path.realpath(_DATA_DIR)
    name = os.path.basename((filename or "").strip())
    if not name or name in (".", ".."):
        return None
    path = os.path.realpath(os.path.join(_DATA_DIR, name))
    if not path.startswith(base + os.sep):
        return None
    return path


def _list_files():
    if not os.path.isdir(_DATA_DIR):
        return []
    out = []
    try:
        for ent in os.scandir(_DATA_DIR):
            if not ent.is_file():
                continue
            out.append(ent.name)
    except OSError:
        return []
    out.sort(key=lambda n: n.lower())
    return out


def _loosen_filename_input(raw: str) -> tuple[str | None, str | None]:
    """
    把用户输入收成安全文件名：取首行、去引号、只保留最后一段路径、
    替换 Windows 非法字符；无「.后缀」时补 .md；过长则截断保留扩展名。
    返回 (文件名, None) 或 (None, 错误码)。
    """
    if not (raw or "").strip():
        return None, "empty"
    s = raw.strip().splitlines()[0].strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    s = s.replace("\\", "/")
    parts = [p for p in s.split("/") if p]
    s = parts[-1] if parts else ""
    s = os.path.basename(s)
    if not s or s in (".", ".."):
        return None, "bad_basename"
    s = "".join(c for c in s if c != "\x00")
    for ch in _WIN_BAD:
        s = s.replace(ch, "_")
    s = s.strip(" .")
    if not s:
        return None, "bad_basename"
    if "." not in s:
        s = f"{s}.md"
    root, _, ext = s.rpartition(".")
    ext = ext.strip()
    root = root.strip(" .")
    if not ext:
        s = f"{(root or 'untitled')}.md"
    elif not root:
        s = f"untitled.{ext}"
    else:
        s = f"{root}.{ext}"
    if len(s) > _MAX_NAME_LEN:
        root2, _, ext2 = s.rpartition(".")
        ext2 = ext2 or "md"
        keep = _MAX_NAME_LEN - len(ext2) - 2
        if keep < 1:
            s = f"untitled.{ext2}"[:_MAX_NAME_LEN]
        else:
            s = f"{root2[:keep]}.{ext2}"
    return s, None


class PromptBankTool(BaseTool):
    TOOL_ID = "prompt_bank"
    TOOL_NAME = "提示词收纳"

    @classmethod
    def get_form_html(cls) -> str:
        _ensure_dir()
        return f"""
        <div class="tool-form prompt-bank-form" data-prompt-bank data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">
                文件保存在 <code>{html.escape(_DATA_DIR)}</code>。
                随便起名即可：支持 .md、.txt、.bat、.py 等；不写后缀会默认 <code>.md</code>。
                若误粘了整段路径，会自动取最后一段并把 <code>\\ / : * ?</code> 等替换成下划线。
            </p>
            <div class="prompt-bank-toolbar">
                <button type="button" class="prompt-bank-refresh">刷新列表</button>
                <input type="search" class="prompt-bank-filter" placeholder="按文件名筛选…" autocomplete="off" />
                <span class="prompt-bank-status" aria-live="polite"></span>
            </div>
            <div class="prompt-bank-layout">
                <aside class="prompt-bank-sidebar" aria-label="文件列表">
                    <div class="prompt-bank-list-wrap"></div>
                    <div class="prompt-bank-new-row">
                        <input type="text" class="prompt-bank-new-name"
                            placeholder="文件名，随意；点「新建」可自动生成" autocomplete="off" />
                        <button type="button" class="prompt-bank-new">新建</button>
                    </div>
                </aside>
                <main class="prompt-bank-main">
                    <label class="prompt-bank-label">当前文件</label>
                    <div class="prompt-bank-current" data-prompt-current>（未选择）</div>
                    <textarea class="prompt-bank-body" rows="22" spellcheck="false"
                        placeholder="选择左侧文件或新建后在此编辑…"></textarea>
                    <div class="prompt-bank-actions">
                        <button type="button" class="prompt-bank-save">保存</button>
                        <button type="button" class="prompt-bank-delete">删除当前文件</button>
                    </div>
                </main>
            </div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/list", methods=["GET"])
        def list_files():
            _ensure_dir()
            names = _list_files()
            return jsonify({"ok": True, "dir": _DATA_DIR, "files": names})

        @bp.route("/content", methods=["GET"])
        def content():
            name = (request.args.get("file") or "").strip()
            path = _realpath_under_data(name)
            if not path or not os.path.isfile(path):
                return jsonify({"ok": False, "error": "文件不存在或不允许访问"}), 400
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    raw = f.read()
            except OSError as e:
                return jsonify({"ok": False, "error": str(e)}), 500
            return jsonify({"ok": True, "file": os.path.basename(path), "content": raw})

        @bp.route("/save", methods=["POST"])
        def save():
            body = request.get_json(silent=True) or {}
            name, verr = _loosen_filename_input(str(body.get("file") or ""))
            content = body.get("content")
            if content is not None and not isinstance(content, str):
                return jsonify({"ok": False, "error": "content 须为字符串"}), 400
            if content is None:
                content = ""
            encoded = content.encode("utf-8")
            if len(encoded) > _MAX_BYTES:
                return jsonify({"ok": False, "error": f"内容过长（约 { _MAX_BYTES // 1024 } KB 上限）"}), 400
            if not name:
                msgs = {
                    "empty": "文件名为空。点「新建」或随便起个名字即可。",
                    "bad_basename": "文件名无效，请换一个简单的名字试试。",
                }
                return jsonify({"ok": False, "error": msgs.get(verr or "", "保存失败。")}), 400
            _ensure_dir()
            path = _realpath_under_data(name)
            if path is None:
                return jsonify({"ok": False, "error": "路径校验失败"}), 400
            try:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
            except OSError as e:
                return jsonify({"ok": False, "error": str(e)}), 500
            return jsonify({"ok": True, "file": name})

        @bp.route("/delete", methods=["POST"])
        def delete():
            body = request.get_json(silent=True) or {}
            name = (str(body.get("file") or "")).strip()
            path = _realpath_under_data(name)
            if not path or not os.path.isfile(path):
                return jsonify({"ok": False, "error": "文件不存在或不允许访问"}), 400
            try:
                os.remove(path)
            except OSError as e:
                return jsonify({"ok": False, "error": str(e)}), 500
            return jsonify({"ok": True, "file": name})
