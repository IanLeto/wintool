# -*- coding: utf-8 -*-
"""
工具：导出目录结构 — 输入Windows路径，导出AI友好的目录树结构
支持：
1. Windows路径自动转换为WSL路径
2. 树状结构输出（AI友好）
3. 可选递归深度控制
4. 文件/文件夹统计
"""
from __future__ import annotations

import html
import io
import os
import re

from flask import Blueprint, jsonify, request

from .base import BaseTool


class ExportDirStructureTool(BaseTool):
    TOOL_ID = "export_dir_structure"
    TOOL_NAME = "导出目录结构"

    @classmethod
    def get_form_html(cls) -> str:
        return f"""
        <div class="tool-form export-dir-structure" data-export-dir-structure data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="export-dir-lead">
                输入Windows路径（如 <code>C:\\Users\\...</code>）或WSL路径（如 <code>/mnt/c/...</code>），
                生成AI友好的目录树结构，方便后续分析和处理。
            </p>
            <div class="export-dir-layout">
                <section class="export-dir-card export-dir-card-input" aria-labelledby="export-dir-h-input">
                    <div class="export-dir-card-head">
                        <h2 id="export-dir-h-input" class="export-dir-card-title">输入目录</h2>
                        <p class="export-dir-card-sub">支持多行；每行一个路径；支持Windows和WSL路径格式</p>
                    </div>
                    <textarea class="export-dir-textarea" data-export-dirs data-wsl-path-input
                        data-path-mode="append" rows="8" spellcheck="false"
                        placeholder="C:\\Users\\YourName\\Projects&#10;D:\\Media&#10;或&#10;/mnt/c/Users/YourName/Projects"></textarea>
                    
                    <div class="export-dir-options">
                        <label class="export-dir-check">
                            <input type="checkbox" data-export-shallow />
                            <span>仅一级（不递归子目录）</span>
                        </label>
                        <div class="export-dir-depth">
                            <label for="export-depth">递归深度：</label>
                            <input type="number" id="export-depth" data-export-depth 
                                min="1" max="10" value="5" style="width: 60px;" />
                            <span class="export-dir-hint">（1-10层，0=无限制）</span>
                        </label>
                        <label class="export-dir-check">
                            <input type="checkbox" data-export-tree checked />
                            <span>树状结构（推荐，AI更易理解）</span>
                        </label>
                        <label class="export-dir-check">
                            <input type="checkbox" data-export-stats checked />
                            <span>显示统计信息</span>
                        </label>
                    </div>
                    
                    <div class="export-dir-card-actions">
                        <button type="button" class="export-dir-btn export-dir-btn-primary" data-export-preview>生成预览</button>
                        <button type="button" class="export-dir-btn" data-export-copy disabled>复制结果</button>
                    </div>
                </section>
                
                <section class="export-dir-card export-dir-card-output" aria-labelledby="export-dir-h-output">
                    <div class="export-dir-card-head">
                        <h2 id="export-dir-h-output" class="export-dir-card-title">目录结构</h2>
                        <p class="export-dir-card-sub" data-export-meta>等待生成...</p>
                    </div>
                    <pre class="export-dir-pre" data-export-preview-text tabindex="0">点击「生成预览」查看目录结构</pre>
                    <p class="export-dir-msg" data-export-msg role="status"></p>
                </section>
            </div>
            
            <details class="export-dir-details">
                <summary class="export-dir-details-summary">💾 保存到文件（可选）</summary>
                <div class="export-dir-details-body">
                    <label class="export-dir-label" for="export-dir-output-path">输出文件路径</label>
                    <input id="export-dir-output-path" class="export-dir-input" type="text" data-export-output
                        data-wsl-path-input placeholder="/mnt/c/temp/structure.txt 或 C:\\temp\\structure.txt" autocomplete="off" />
                    <button type="button" class="export-dir-btn export-dir-btn-secondary" data-export-save>写入文件</button>
                </div>
            </details>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/preview", methods=["POST"])
        def preview():
            """生成目录结构预览"""
            data = request.get_json() or {}
            dirs_text = (data.get("dirs") or "").strip()
            shallow = data.get("shallow") in ("1", "true", True, "on")
            max_depth = int(data.get("max_depth", 5))
            tree_format = data.get("tree_format") in ("1", "true", True, "on")
            show_stats = data.get("show_stats") in ("1", "true", True, "on")
            
            if not dirs_text:
                return jsonify({"ok": False, "error": "请至少填写一个目录路径"}), 400
            
            # 解析并转换路径
            raw_dirs = [d.strip() for d in dirs_text.splitlines() if d.strip()]
            if not raw_dirs:
                return jsonify({"ok": False, "error": "请至少填写一个目录路径"}), 400
            
            # 转换Windows路径为WSL路径
            converted_dirs = []
            conversion_info = []
            for raw_path in raw_dirs:
                wsl_path = cls._convert_to_wsl_path(raw_path)
                converted_dirs.append(wsl_path)
                if wsl_path != raw_path:
                    conversion_info.append(f"已转换: {raw_path} → {wsl_path}")
            
            # 验证路径
            errors = []
            valid_dirs = []
            for d in converted_dirs:
                if not os.path.exists(d):
                    errors.append(f"路径不存在: {d}")
                elif not os.path.isdir(d):
                    errors.append(f"不是目录: {d}")
                else:
                    valid_dirs.append(d)
            
            if not valid_dirs:
                return jsonify({
                    "ok": False, 
                    "error": "没有有效的目录路径",
                    "details": errors
                }), 400
            
            # 生成结构
            if shallow:
                max_depth = 1
            
            text, stats = cls._build_structure_text(
                valid_dirs, 
                max_depth=max_depth,
                tree_format=tree_format,
                show_stats=show_stats
            )
            
            lines = len(text.splitlines()) if text else 0
            
            result = {
                "ok": True,
                "text": text,
                "lines": lines,
                "stats": stats,
                "errors": errors if errors else None,
                "conversions": conversion_info if conversion_info else None
            }
            
            return jsonify(result)

        @bp.route("/run", methods=["POST"])
        def run():
            """生成并保存到文件"""
            data = request.get_json() or {}
            dirs_text = (data.get("dirs") or "").strip()
            output_path = (data.get("output") or "").strip()
            shallow = data.get("shallow") in ("1", "true", True, "on")
            max_depth = int(data.get("max_depth", 5))
            tree_format = data.get("tree_format") in ("1", "true", True, "on")
            show_stats = data.get("show_stats") in ("1", "true", True, "on")
            
            if not dirs_text:
                return jsonify({"ok": False, "error": "请至少填写一个目录路径"}), 400
            if not output_path:
                return jsonify({"ok": False, "error": "写入文件时请填写输出路径"}), 400
            
            # 转换输出路径
            output_path = cls._convert_to_wsl_path(output_path)
            
            # 解析并转换输入路径
            raw_dirs = [d.strip() for d in dirs_text.splitlines() if d.strip()]
            converted_dirs = [cls._convert_to_wsl_path(d) for d in raw_dirs]
            
            # 验证路径
            errors = []
            valid_dirs = []
            for d in converted_dirs:
                if not os.path.exists(d):
                    errors.append(f"路径不存在: {d}")
                elif not os.path.isdir(d):
                    errors.append(f"不是目录: {d}")
                else:
                    valid_dirs.append(d)
            
            if not valid_dirs:
                return jsonify({
                    "ok": False,
                    "error": "没有有效的目录路径",
                    "details": errors
                }), 400
            
            # 生成结构
            if shallow:
                max_depth = 1
            
            text, stats = cls._build_structure_text(
                valid_dirs,
                max_depth=max_depth,
                tree_format=tree_format,
                show_stats=show_stats
            )
            
            # 写入文件
            try:
                out_dir = os.path.dirname(output_path)
                if out_dir and not os.path.isdir(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                with open(output_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text)
            except OSError as e:
                return jsonify({"ok": False, "error": f"写入文件失败: {e}"}), 500
            
            lines = len(text.splitlines()) if text else 0
            return jsonify({
                "ok": True,
                "output": output_path,
                "lines_written": lines,
                "text": text,
                "stats": stats,
                "errors": errors if errors else None
            })

    @staticmethod
    def _convert_to_wsl_path(path: str) -> str:
        """
        将Windows路径转换为WSL路径
        C:\\Users\\... → /mnt/c/Users/...
        D:\\Data → /mnt/d/Data
        """
        if not path:
            return ""
        
        path = path.strip().strip('"').strip("'")
        
        # 已经是WSL路径
        if path.startswith("/"):
            return path
        
        # 处理反斜杠
        path = path.replace("\\", "/")
        
        # 匹配 C:/ 或 C: 格式
        match = re.match(r'^([a-zA-Z]):(\/.*)?$', path)
        if match:
            drive = match.group(1).lower()
            rest = match.group(2) or ""
            rest = rest.lstrip("/")
            return f"/mnt/{drive}" + (f"/{rest}" if rest else "")
        
        return path

    @staticmethod
    def _build_structure_text(dirs, max_depth=5, tree_format=True, show_stats=True):
        """
        生成目录结构文本
        
        Args:
            dirs: 目录列表
            max_depth: 最大递归深度（0=无限制）
            tree_format: 是否使用树状格式
            show_stats: 是否显示统计信息
        """
        buf = io.StringIO()
        total_dirs = 0
        total_files = 0
        errors = []
        
        for root_path in dirs:
            root_path = os.path.abspath(root_path)
            buf.write(f"\n{'='*80}\n")
            buf.write(f"📁 {root_path}\n")
            buf.write(f"{'='*80}\n\n")
            
            try:
                if tree_format:
                    dir_count, file_count = ExportDirStructureTool._build_tree_format(
                        buf, root_path, max_depth
                    )
                else:
                    dir_count, file_count = ExportDirStructureTool._build_flat_format(
                        buf, root_path, max_depth
                    )
                
                total_dirs += dir_count
                total_files += file_count
                
                if show_stats:
                    buf.write(f"\n📊 统计: {dir_count} 个文件夹, {file_count} 个文件\n")
                
            except Exception as e:
                error_msg = f"处理 {root_path} 时出错: {e}"
                errors.append(error_msg)
                buf.write(f"\n❌ {error_msg}\n")
        
        text = buf.getvalue()
        if text.startswith("\n"):
            text = text[1:]
        
        stats = {
            "total_dirs": total_dirs,
            "total_files": total_files,
            "scanned_roots": len(dirs),
            "errors": errors
        }
        
        return text, stats

    @staticmethod
    def _build_tree_format(buf, root_path, max_depth):
        """构建树状格式（AI友好）"""
        dir_count = 0
        file_count = 0
        
        def walk_tree(path, prefix="", depth=0):
            nonlocal dir_count, file_count
            
            if max_depth > 0 and depth >= max_depth:
                return
            
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                buf.write(f"{prefix}❌ [权限拒绝]\n")
                return
            except Exception as e:
                buf.write(f"{prefix}❌ [错误: {e}]\n")
                return
            
            # 分离文件夹和文件
            dirs = []
            files = []
            for entry in entries:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    dirs.append(entry)
                else:
                    files.append(entry)
            
            # 先显示文件夹
            for i, dirname in enumerate(dirs):
                is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                connector = "└── " if is_last_dir else "├── "
                buf.write(f"{prefix}{connector}📁 {dirname}/\n")
                
                # 递归子目录
                sub_path = os.path.join(path, dirname)
                extension = "    " if is_last_dir else "│   "
                walk_tree(sub_path, prefix + extension, depth + 1)
                dir_count += 1
            
            # 再显示文件
            for i, filename in enumerate(files):
                is_last = i == len(files) - 1
                connector = "└── " if is_last else "├── "
                
                # 获取文件大小
                try:
                    full_path = os.path.join(path, filename)
                    size = os.path.getsize(full_path)
                    size_str = ExportDirStructureTool._format_size(size)
                    buf.write(f"{prefix}{connector}📄 {filename} ({size_str})\n")
                except:
                    buf.write(f"{prefix}{connector}📄 {filename}\n")
                
                file_count += 1
        
        walk_tree(root_path)
        return dir_count, file_count

    @staticmethod
    def _build_flat_format(buf, root_path, max_depth):
        """构建平铺格式"""
        dir_count = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            # 计算当前深度
            rel_path = os.path.relpath(dirpath, root_path)
            if rel_path == ".":
                depth = 0
            else:
                depth = rel_path.count(os.sep) + 1
            
            if max_depth > 0 and depth >= max_depth:
                dirnames.clear()  # 不再递归
                continue
            
            # 显示当前目录
            if rel_path != ".":
                buf.write(f"\n{rel_path}/\n")
            
            # 显示子文件夹
            for dirname in sorted(dirnames):
                rel_dir = os.path.join(rel_path, dirname) if rel_path != "." else dirname
                buf.write(f"  📁 {rel_dir}/\n")
                dir_count += 1
            
            # 显示文件
            for filename in sorted(filenames):
                rel_file = os.path.join(rel_path, filename) if rel_path != "." else filename
                buf.write(f"  📄 {rel_file}\n")
                file_count += 1
        
        return dir_count, file_count

    @staticmethod
    def _format_size(size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
