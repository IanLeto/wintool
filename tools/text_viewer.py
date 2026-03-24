# -*- coding: utf-8 -*-
"""
工具：文本阅览 — 读取 data/text_viewer/ 下的纯文本文件，前端以页签切换展示。
将 .txt / .md 等文件放入该目录后，在页面点击「刷新列表」或重新打开工具即可。
"""
import html
import os

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_TEXT_DIR = os.path.join(_PROJECT_ROOT, "data", "text_viewer")
_ALLOWED_SUFFIXES = {".txt", ".md", ".markdown", ".log", ".csv"}


def _realpath_under_data(filename: str) -> str | None:
    """仅允许读取 text_viewer 目录内的普通文件，防止路径穿越。"""
    base = os.path.realpath(_TEXT_DIR)
    name = os.path.basename(filename or "")
    if not name or name in (".", ".."):
        return None
    path = os.path.realpath(os.path.join(_TEXT_DIR, name))
    if not path.startswith(base + os.sep):
        return None
    if not os.path.isfile(path):
        return None
    return path


def _list_text_files():
    if not os.path.isdir(_TEXT_DIR):
        return []
    out = []
    try:
        for ent in os.scandir(_TEXT_DIR):
            if not ent.is_file():
                continue
            suf = os.path.splitext(ent.name)[1].lower()
            if suf not in _ALLOWED_SUFFIXES:
                continue
            out.append(ent.name)
    except OSError:
        return []
    out.sort(key=lambda n: n.lower())
    return out


class TextViewerTool(BaseTool):
    TOOL_ID = "text_viewer"
    TOOL_NAME = "文本阅览"

    @classmethod
    def get_form_html(cls) -> str:
        exts = "、".join(sorted(s.replace(".", "") for s in _ALLOWED_SUFFIXES))
        hint = (
            f"将需要展示的文本文件放入服务器上的目录 "
            f"<code>{html.escape(_TEXT_DIR)}</code>。"
            f"支持后缀：{html.escape(exts)}。"
            "保存文件后点击下方「刷新列表」即可看到新页签。"
        )
        return f"""
        <div class="tool-form text-viewer-form" data-text-viewer data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">{hint}</p>
            <div class="text-viewer-toolbar">
                <button type="button" class="text-viewer-refresh">刷新列表</button>
                <label class="text-viewer-filter-label">
                    <span class="text-viewer-filter-hint">筛选</span>
                    <input type="search" class="text-viewer-filter" placeholder="按文件名筛选…" autocomplete="off" />
                </label>
            </div>
            <div class="text-viewer-tabs-wrap" role="tablist" aria-label="文本文件"></div>
            <div class="text-viewer-panel" role="tabpanel" aria-live="polite">
                <p class="text-viewer-placeholder">正在加载列表…</p>
            </div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/list", methods=["GET"])
        def list_files():
            if not os.path.isdir(_TEXT_DIR):
                return jsonify(
                    {
                        "ok": True,
                        "dir": _TEXT_DIR,
                        "files": [],
                        "hint": "目录不存在，已自动视为空。可在服务器上创建该目录并放入文本文件。",
                    }
                )
            names = _list_text_files()
            return jsonify({"ok": True, "dir": _TEXT_DIR, "files": names})

        @bp.route("/content", methods=["GET"])
        def content():
            name = (request.args.get("file") or "").strip()
            path = _realpath_under_data(name)
            if not path:
                return jsonify({"ok": False, "error": "文件不存在或不允许访问"}), 400
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    raw = f.read()
            except OSError as e:
                return jsonify({"ok": False, "error": str(e)}), 500
            return jsonify({"ok": True, "file": os.path.basename(path), "content": raw})
