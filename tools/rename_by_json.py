# -*- coding: utf-8 -*-
"""
工具：根据 JSON 映射重命名目录下的文件，保留原文件后缀。
JSON 格式：{ "原文件名": "新名称", ... }，新名称会自动加上原文件的扩展名。
"""
import json
import os

from flask import Blueprint, request, jsonify
from .base import BaseTool


class RenameByJsonTool(BaseTool):
    TOOL_ID = "rename_by_json"
    TOOL_NAME = "按 JSON 重命名文件"

    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form">
            <p class="desc">粘贴一个 JSON 对象，key 为当前文件名，value 为新名称（不含后缀）。指定目录下匹配到的文件会被重命名，并保留原扩展名。</p>
            <div class="field">
                <label for="rename_json">JSON 映射（每行一个 "原文件名": "新名称"）：</label>
                <textarea id="rename_json" data-param="json" rows="12" placeholder='{"file.mkv": "新名字", ...}'></textarea>
            </div>
            <div class="field">
                <label for="rename_dir">目录路径：</label>
                <input type="text" id="rename_dir" data-param="path" placeholder="/mnt/c/Users/.../Movies" />
            </div>
            <button type="button" class="btn-run" data-tool="rename_by_json">执行</button>
            <div class="result" id="rename_result"></div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/run", methods=["POST"])
        def run():
            data = request.get_json() or {}
            json_str = (data.get("json") or "").strip()
            path = (data.get("path") or "").strip()

            if not json_str:
                return jsonify({"ok": False, "error": "请输入 JSON"})
            if not path:
                return jsonify({"ok": False, "error": "请输入目录路径"})
            if not os.path.isdir(path):
                return jsonify({"ok": False, "error": f"路径不存在或不是目录: {path}"})

            try:
                mapping = json.loads(json_str)
            except json.JSONDecodeError as e:
                return jsonify({"ok": False, "error": f"JSON 格式错误: {e}"})

            if not isinstance(mapping, dict):
                return jsonify({"ok": False, "error": "JSON 必须是对象（key-value）"})

            try:
                renamed, skipped, errors = cls._rename_by_mapping(path, mapping)
                return jsonify({
                    "ok": True,
                    "renamed": renamed,
                    "skipped": skipped,
                    "errors": errors,
                })
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})

    @staticmethod
    def _rename_by_mapping(dir_path, mapping):
        """
        根据 mapping 重命名目录下的文件，保留原扩展名。
        mapping: { "原文件名": "新名称", ... }
        返回 (renamed_list, skipped_list, errors_list)
        """
        dir_path = os.path.abspath(dir_path)
        renamed = []
        skipped = []
        errors = []

        for old_name, new_name in mapping.items():
            if not isinstance(old_name, str) or not isinstance(new_name, str):
                errors.append(f"跳过非字符串项: {old_name!r} -> {new_name!r}")
                continue
            old_path = os.path.join(dir_path, old_name)
            if not os.path.isfile(old_path):
                skipped.append(old_name)
                continue
            _, ext = os.path.splitext(old_name)
            new_base = new_name.strip()
            if new_base.endswith(ext):
                new_base = new_base[: -len(ext)]
            new_file_name = new_base + ext
            new_path = os.path.join(dir_path, new_file_name)
            if os.path.abspath(old_path) == os.path.abspath(new_path):
                continue
            if os.path.exists(new_path):
                errors.append(f"目标已存在，跳过: {old_name} -> {new_file_name}")
                continue
            try:
                os.rename(old_path, new_path)
                renamed.append((old_name, new_file_name))
            except Exception as e:
                errors.append(f"{old_name}: {e}")

        return renamed, skipped, errors
