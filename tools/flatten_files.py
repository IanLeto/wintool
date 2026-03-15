# -*- coding: utf-8 -*-
"""
工具：递归将目录下所有文件提取到当前目录，重名则自动重命名。
"""
import os
import shutil
from pathlib import Path

from flask import Blueprint, request, jsonify
from .base import BaseTool


class FlattenFilesTool(BaseTool):
    TOOL_ID = "flatten_files"
    TOOL_NAME = "递归展平目录"

    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form">
            <p class="desc">将指定目录及其所有子目录中的文件，递归移动到该目录根下。重名文件会自动重命名（如 file.txt → file_1.txt）。</p>
            <div class="field">
                <label for="flatten_path">目标目录路径：</label>
                <input type="text" id="flatten_path" data-param="path" placeholder="/mnt/c/Users/..." value="/mnt/c" />
            </div>
            <button type="button" class="btn-run" data-tool="flatten_files">执行</button>
            <div class="result" id="flatten_result"></div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/run", methods=["POST"])
        def run():
            data = request.get_json() or {}
            path = (data.get("path") or "").strip()
            if not path:
                return jsonify({"ok": False, "error": "请输入目录路径"})
            if not os.path.isdir(path):
                return jsonify({"ok": False, "error": f"路径不存在或不是目录: {path}"})
            try:
                moved, renamed, errors = cls._flatten(path)
                return jsonify({
                    "ok": True,
                    "moved": moved,
                    "renamed": renamed,
                    "errors": errors,
                })
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})

    @staticmethod
    def _flatten(root: str):
        """将 root 下所有文件递归移动到 root，重名则重命名。"""
        root = os.path.abspath(root)
        moved = []
        renamed = []
        errors = []
        used = {f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))}

        files_to_move = []
        for dirpath, _, filenames in os.walk(root, topdown=False):
            if dirpath == root:
                continue
            for f in filenames:
                src = os.path.join(dirpath, f)
                if os.path.isfile(src):
                    files_to_move.append((src, f))

        for src, f in files_to_move:
            dst_name = f
            if dst_name in used:
                stem, ext = os.path.splitext(f)
                n = 1
                while f"{stem}_{n}{ext}" in used:
                    n += 1
                dst_name = f"{stem}_{n}{ext}"
                renamed.append((f, dst_name))
            used.add(dst_name)
            dst = os.path.join(root, dst_name)
            try:
                shutil.move(src, dst)
                moved.append(dst_name)
            except Exception as e:
                errors.append(f"{src}: {e}")

        for dirpath, dirnames, filenames in os.walk(root, topdown=False):
            if dirpath != root and not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                except Exception:
                    pass

        return moved, renamed, errors
