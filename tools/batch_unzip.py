# -*- coding: utf-8 -*-
"""
批量解压：在指定路径下查找压缩包，解压到该压缩包所在目录；成功则删除原文件。
可选密码；密码错误则跳过该文件。优先使用 7z（若 PATH 或常见 Windows 路径存在），否则 zip/tar 用标准库。
"""
import os
import shutil
import subprocess
import tarfile
import zipfile

from flask import Blueprint, request, jsonify
from .base import BaseTool


def _is_archive(path: str) -> bool:
    p = path.lower()
    if p.endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
        return True
    for ext in (
        ".zip",
        ".7z",
        ".rar",
        ".tar",
        ".tgz",
        ".tbz2",
        ".txz",
    ):
        if p.endswith(ext):
            return True
    return False


def _only_7z_formats(lower_path: str) -> bool:
    return lower_path.endswith((".7z", ".rar"))


def _is_tar_archive(lower_path: str) -> bool:
    return any(
        lower_path.endswith(s)
        for s in (
            ".tar",
            ".tar.gz",
            ".tgz",
            ".tar.bz2",
            ".tbz2",
            ".tar.xz",
            ".txz",
        )
    )


def _find_7z():
    for name in ("7z", "7za"):
        p = shutil.which(name)
        if p:
            return p
    for win in (
        "/mnt/c/Program Files/7-Zip/7z.exe",
        "/mnt/c/Program Files (x86)/7-Zip/7z.exe",
    ):
        if os.path.isfile(win):
            return win
    return None


def _7z_extract(seven: str, archive: str, out_dir: str, password: str | None):
    out_dir = os.path.abspath(out_dir)
    out_arg = out_dir if out_dir.endswith(os.sep) else out_dir + os.sep
    cmd = [seven, "x", "-y", f"-o{out_arg}", os.path.abspath(archive)]
    if password:
        cmd.insert(-1, f"-p{password}")
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=out_dir,
        )
    except Exception as e:
        return False, str(e)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()[:800]
        return False, err or f"7z 退出码 {r.returncode}"
    return True, ""


def _zip_extract(archive: str, out_dir: str, password: str | None):
    pwd = password.encode("utf-8") if password else None
    try:
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(out_dir, pwd=pwd)
    except RuntimeError as e:
        msg = str(e).lower()
        if "bad password" in msg or "password" in msg:
            return False, "zip 密码错误"
        return False, str(e)
    except zipfile.BadZipFile as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
    return True, ""


def _tar_extractall(t: tarfile.TarFile, out_dir: str):
    try:
        t.extractall(out_dir, filter="data")
    except TypeError:
        t.extractall(out_dir)


def _tar_extract(archive: str, out_dir: str):
    try:
        lower = archive.lower()
        if lower.endswith((".tar.gz", ".tgz")):
            mode = "r:gz"
        elif lower.endswith((".tar.bz2", ".tbz2")):
            mode = "r:bz2"
        elif lower.endswith((".tar.xz", ".txz")):
            mode = "r:xz"
        elif lower.endswith(".tar"):
            mode = "r:"
        else:
            return False, "不支持的 tar 格式"
        with tarfile.open(archive, mode) as t:
            _tar_extractall(t, out_dir)
    except Exception as e:
        return False, str(e)
    return True, ""


def _extract_one(
    archive: str,
    out_dir: str,
    password: str | None,
    seven,
):
    """返回 (成功, 错误信息, 方法标签)"""
    archive = os.path.abspath(archive)
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    lower = archive.lower()

    tried_7z = False
    if seven:
        ok, err = _7z_extract(seven, archive, out_dir, password)
        tried_7z = True
        if ok:
            return True, "", "7z"
        if _only_7z_formats(lower):
            return False, err or "7z 解压失败", "7z"

    if lower.endswith(".zip"):
        ok, err = _zip_extract(archive, out_dir, password)
        if ok:
            return True, "", "zip" if not tried_7z else "zip(回退)"
        if tried_7z:
            return False, err or "zip 解压失败", "zip"
        return False, err or "zip 解压失败", "zip"

    if _is_tar_archive(lower):
        if password:
            return False, "加密 tar 请使用 7z 并填写密码", ""
        ok, err = _tar_extract(archive, out_dir)
        if ok:
            return True, "", "tar" if not tried_7z else "tar(回退)"
        if tried_7z:
            return False, err or "tar 解压失败", "tar"
        return False, err or "tar 解压失败", "tar"

    if tried_7z:
        return False, "7z 仍无法解压此文件", "7z"
    if _only_7z_formats(lower) or lower.endswith(".zip") or _is_tar_archive(lower):
        return False, "未检测到 7z，且标准库无法处理此文件", ""
    return False, "不支持的压缩格式", ""


def _passwordish_reason(err: str) -> bool:
    if not err:
        return False
    low = err.lower()
    if "密码" in err:
        return True
    if "password" in low or "wrong password" in low:
        return True
    if "encrypted" in low and "can not open" in low:
        return True
    return False


def _iter_archives(root: str, recursive: bool):
    root = os.path.abspath(root)
    if os.path.isfile(root):
        if _is_archive(root):
            yield root
        return
    if not os.path.isdir(root):
        return
    if recursive:
        for dp, _, files in os.walk(root):
            for f in files:
                p = os.path.join(dp, f)
                if _is_archive(p):
                    yield p
    else:
        for f in os.listdir(root):
            p = os.path.join(root, f)
            if os.path.isfile(p) and _is_archive(p):
                yield p


class BatchUnzipTool(BaseTool):
    TOOL_ID = "batch_unzip"
    TOOL_NAME = "批量解压"

    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form">
            <p class="desc">指定<strong>目录</strong>或<strong>单个压缩包路径</strong>。匹配的压缩包会解压到<strong>该文件所在目录</strong>；解压成功则删除原压缩包。可选填<strong>解压密码</strong>；密码错误则跳过该文件。支持递归扫描子目录。</p>
            <div class="field">
                <label for="batch_unzip_path">路径（目录或压缩包）：</label>
                <input type="text" id="batch_unzip_path" data-param="path" data-wsl-path-input placeholder="/mnt/c/Users/.../Downloads" />
            </div>
            <div class="field">
                <label for="batch_unzip_password">解压密码（可选）：</label>
                <input type="password" id="batch_unzip_password" data-param="password" placeholder="加密压缩包时填写；留空则按无密码尝试" autocomplete="off" />
            </div>
            <div class="field field-inline">
                <input type="checkbox" id="batch_unzip_recursive" data-param="recursive" value="1" checked />
                <label for="batch_unzip_recursive">包含子目录（递归查找压缩包）</label>
            </div>
            <button type="button" class="btn-run" data-tool="batch_unzip">开始解压</button>
            <div class="result" id="batch_unzip_result"></div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/run", methods=["POST"])
        def run():
            data = request.get_json() or {}
            path = (data.get("path") or "").strip()
            password = (data.get("password") or "").strip() or None
            recursive = data.get("recursive") in ("1", "true", True, "on")

            if not path:
                return jsonify({"ok": False, "error": "请输入路径"})
            if not os.path.exists(path):
                return jsonify({"ok": False, "error": f"路径不存在: {path}"})

            seven = _find_7z()
            archives = list(_iter_archives(path, recursive))
            if not archives:
                return jsonify(
                    {
                        "ok": False,
                        "error": "未找到支持的压缩包（.zip .7z .rar .tar .tar.gz 等）",
                    }
                )

            unzipped = []
            skipped = []
            errors = []

            for arch in archives:
                out_dir = os.path.dirname(os.path.abspath(arch))
                ok, err, method = _extract_one(arch, out_dir, password, seven)
                if ok:
                    try:
                        os.remove(arch)
                        unzipped.append({"file": arch, "method": method})
                    except OSError as e:
                        errors.append(f"{arch}: 已解压但删除原文件失败: {e}")
                else:
                    reason = err or "解压失败"
                    if _passwordish_reason(reason):
                        reason = reason if len(reason) < 200 else reason[:200] + "…"
                    skipped.append({"file": arch, "reason": reason})

            return jsonify(
                {
                    "ok": True,
                    "unzipped": unzipped,
                    "skipped": skipped,
                    "errors": errors,
                    "seven_found": bool(seven),
                }
            )
