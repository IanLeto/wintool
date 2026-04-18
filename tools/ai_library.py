# -*- coding: utf-8 -*-
"""
工具：AI 内容库
浏览项目根目录下 ai回答 / ai语料 两个目录中的文本文件。
"""
from __future__ import annotations

import html
import os

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

_DIR_MAP = {
    "answers": {
        "label": "AI回答",
        "path": os.path.join(_PROJECT_ROOT, "ai回答"),
    },
    "corpus": {
        "label": "AI语料",
        "path": os.path.join(_PROJECT_ROOT, "ai语料"),
    },
}

_ALLOWED_SUFFIXES = {".txt", ".md", ".markdown", ".json", ".csv", ".log"}


def _get_group_info(group: str) -> dict | None:
    return _DIR_MAP.get((group or "").strip())


def _list_group_files(group: str) -> list[str]:
    info = _get_group_info(group)
    if not info:
        return []
    root = info["path"]
    if not os.path.isdir(root):
        return []

    out = []
    try:
        for base, _, files in os.walk(root):
            for name in files:
                suf = os.path.splitext(name)[1].lower()
                if suf not in _ALLOWED_SUFFIXES:
                    continue
                abs_path = os.path.join(base, name)
                rel = os.path.relpath(abs_path, root)
                out.append(rel.replace(os.sep, "/"))
    except OSError:
        return []

    out.sort(key=lambda x: x.lower())
    return out


def _safe_file_path(group: str, rel_path: str) -> str | None:
    info = _get_group_info(group)
    if not info:
        return None
    root = os.path.realpath(info["path"])
    if not os.path.isdir(root):
        return None

    rel = (rel_path or "").strip().replace("\\", "/").lstrip("/")
    if not rel or rel in (".", ".."):
        return None
    if "/../" in f"/{rel}/":
        return None

    abs_path = os.path.realpath(os.path.join(root, rel))
    if not abs_path.startswith(root + os.sep):
        return None
    if not os.path.isfile(abs_path):
        return None
    if os.path.splitext(abs_path)[1].lower() not in _ALLOWED_SUFFIXES:
        return None
    return abs_path


class AILibraryTool(BaseTool):
    TOOL_ID = "ai_library"
    TOOL_NAME = "AI内容库"

    @classmethod
    def get_form_html(cls) -> str:
        exts = "、".join(sorted(s.replace(".", "") for s in _ALLOWED_SUFFIXES))
        dir_desc = "；".join(
            f"{html.escape(v['label'])}: <code>{html.escape(v['path'])}</code>"
            for v in _DIR_MAP.values()
        )
        return f"""
        <div class="tool-form ai-library-form" data-ai-library data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">
                在一个页面里查看常用 AI 文档目录内容。支持目录切换、文件名筛选与正文预览。
                支持后缀：{html.escape(exts)}。<br/>
                {dir_desc}
            </p>
            <div class="ai-library-toolbar">
                <button type="button" class="ai-library-refresh">刷新列表</button>
                <select class="ai-library-group" aria-label="目录切换">
                    <option value="answers">AI回答</option>
                    <option value="corpus">AI语料</option>
                </select>
                <input type="search" class="ai-library-filter" placeholder="按文件名筛选…" autocomplete="off" />
            </div>
            <div class="ai-library-meta"></div>
            <div class="ai-library-layout">
                <aside class="ai-library-sidebar">
                    <div class="ai-library-filelist" role="tablist" aria-label="文件列表"></div>
                </aside>
                <section class="ai-library-main" role="tabpanel" aria-live="polite">
                    <p class="ai-library-placeholder">正在加载列表…</p>
                </section>
            </div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/list", methods=["GET"])
        def list_files():
            group = (request.args.get("group") or "answers").strip()
            info = _get_group_info(group)
            if not info:
                return jsonify({"ok": False, "error": "未知目录分组"}), 400

            files = _list_group_files(group)
            hint = None
            if not os.path.isdir(info["path"]):
                hint = "目录不存在，先在项目根目录创建对应目录。"
            elif not files:
                hint = "目录存在，但暂时没有可展示的文本文件。"
            return jsonify(
                {
                    "ok": True,
                    "group": group,
                    "group_label": info["label"],
                    "dir": info["path"],
                    "files": files,
                    "hint": hint,
                }
            )

        @bp.route("/content", methods=["GET"])
        def content():
            group = (request.args.get("group") or "answers").strip()
            rel_path = (request.args.get("file") or "").strip()
            path = _safe_file_path(group, rel_path)
            if not path:
                return jsonify({"ok": False, "error": "文件不存在或不允许访问"}), 400
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    raw = f.read()
            except OSError as e:
                return jsonify({"ok": False, "error": str(e)}), 500
            info = _get_group_info(group) or {}
            root = info.get("path", "")
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            return jsonify(
                {
                    "ok": True,
                    "group": group,
                    "file": rel,
                    "content": raw,
                }
            )
