# -*- coding: utf-8 -*-
"""
工具：将多个目录下的文件和文件夹名称写入到指定文件。
"""
import os

from flask import Blueprint, request, jsonify
from .base import BaseTool


class ExportDirStructureTool(BaseTool):
    TOOL_ID = "export_dir_structure"
    TOOL_NAME = "导出目录结构到文件"

    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form">
            <p class="desc">输入多个目录路径（每行一个），将每个目录下的文件和文件夹名称（相对路径）写入到指定文件中。可勾选「仅一级」只导出直接子项，不递归子目录。</p>
            <div class="field">
                <label for="dirs_input">目录路径（每行一个）：</label>
                <textarea id="dirs_input" data-param="dirs" data-wsl-path-input data-path-mode="append" rows="6" placeholder="/mnt/c/Users/xxx&#10;/mnt/d/Projects"></textarea>
            </div>
            <div class="field">
                <label for="output_file">输出文件路径：</label>
                <input type="text" id="output_file" data-param="output" data-wsl-path-input placeholder="/mnt/c/structure.txt" />
            </div>
            <div class="field field-inline">
                <input type="checkbox" id="shallow_export" data-param="shallow" value="1" />
                <label for="shallow_export">仅一级（不递归，只导出直接子文件和子文件夹名称）</label>
            </div>
            <button type="button" class="btn-run" data-tool="export_dir_structure">执行</button>
            <div class="result" id="export_structure_result"></div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/run", methods=["POST"])
        def run():
            data = request.get_json() or {}
            dirs_text = (data.get("dirs") or "").strip()
            output_path = (data.get("output") or "").strip()

            if not dirs_text:
                return jsonify({"ok": False, "error": "请输入至少一个目录路径"})
            if not output_path:
                return jsonify({"ok": False, "error": "请输入输出文件路径"})

            dirs = [d.strip() for d in dirs_text.splitlines() if d.strip()]
            if not dirs:
                return jsonify({"ok": False, "error": "请输入至少一个目录路径"})

            for d in dirs:
                if not os.path.isdir(d):
                    return jsonify({"ok": False, "error": f"路径不存在或不是目录: {d}"})

            shallow = data.get("shallow") in ("1", "true", True, "on")

            try:
                lines, errors = cls._export_structure(dirs, output_path, shallow=shallow)
                return jsonify({
                    "ok": True,
                    "output": output_path,
                    "lines_written": lines,
                    "errors": errors,
                })
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)})

    @staticmethod
    def _export_structure(dirs, output_path, shallow=False):
        """将每个目录的树状结构（相对路径）写入 output_path。shallow=True 时只导出一级。"""
        lines_written = 0
        errors = []
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for root in dirs:
                root = os.path.abspath(root)
                f.write(f"\n# {root}\n")
                lines_written += 1
                try:
                    if shallow:
                        entries = sorted(os.listdir(root))
                        subdirs = [e for e in entries if os.path.isdir(os.path.join(root, e))]
                        files = [e for e in entries if os.path.isfile(os.path.join(root, e))]
                        for d in sorted(subdirs):
                            f.write(d + "/\n")
                            lines_written += 1
                        for name in sorted(files):
                            f.write(name + "\n")
                            lines_written += 1
                    else:
                        for dirpath, dirnames, filenames in os.walk(root):
                            rel_base = os.path.relpath(dirpath, root)
                            if rel_base == ".":
                                rel_base = ""
                            for d in sorted(dirnames):
                                f.write(os.path.join(rel_base, d) + "/\n")
                                lines_written += 1
                            for name in sorted(filenames):
                                f.write(os.path.join(rel_base, name) + "\n")
                                lines_written += 1
                except Exception as e:
                    errors.append(f"{root}: {e}")

        return lines_written, errors
