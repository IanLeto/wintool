# -*- coding: utf-8 -*-
"""
本机文件夹选择（供浏览器调用）：在 WSL 下优先弹出 Windows 资源管理器式对话框；
否则尝试 zenity / tkinter。路径统一转为 WSL 风格（/mnt/c/...）。

PowerShell  stdout 在管道中常为 UTF-16/系统代码页，直接按 UTF-8 读会乱码，故改为输出 Base64(UTF-8 路径) 再解码。
"""
import base64
import os
import re
import shutil
import subprocess
import sys


def windows_path_to_wsl(win_path: str) -> str:
    """C:\\Users\\a -> /mnt/c/Users/a；\\wsl$ 风格 UNC 尽量转为 Linux 路径。"""
    if not win_path:
        return ""
    s = win_path.strip().strip('"')
    s = s.replace("\\", "/")
    if s.startswith("//wsl"):
        parts = [p for p in s.split("/") if p]
        if len(parts) >= 2 and parts[0].lower().startswith("wsl"):
            rest = "/".join(parts[2:]) if len(parts) > 2 else ""
            return "/" + rest if rest else "/"
    m = re.match(r"^([a-zA-Z]):(/.*)?$", s)
    if m:
        drive = m.group(1).lower()
        rest = (m.group(2) or "").strip("/")
        return f"/mnt/{drive}" + ("/" + rest if rest else "")
    return s


def _powershell_candidates():
    for p in (
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "/mnt/c/Program Files/PowerShell/7/pwsh.exe",
    ):
        if os.path.isfile(p):
            yield p


def _decode_ps_path_line(line: str) -> str | None:
    """解析 PowerShell 输出的一行：优先 Base64(UTF-8 路径)。"""
    line = line.strip()
    if not line:
        return None
    try:
        raw = base64.b64decode(line, validate=True)
        return raw.decode("utf-8")
    except Exception:
        return None


def _run_powershell(ps_exe: str, script: str) -> str | None:
    """执行 PowerShell；路径以 Base64(仅 ASCII) 传回，stdout 按字节读避免乱码。"""
    try:
        r = subprocess.run(
            [
                ps_exe,
                "-NoProfile",
                "-STA",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            timeout=300,
        )
    except Exception:
        return None
    raw = r.stdout or b""
    if not raw.strip():
        return None
    for line in reversed(raw.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            ascii_line = line.decode("ascii", errors="strict").strip()
        except Exception:
            continue
        path = _decode_ps_path_line(ascii_line)
        if path:
            return path
    return None


def pick_folder_powershell() -> str | None:
    """
    优先：Shell.Application COM（BrowseForFolder）。
    其次：WinForms FolderBrowserDialog，[DialogResult]::OK。
    路径经 [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($p)) 输出。
    """
    b64_emit = (
        "[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($p))"
    )
    script_com = (
        "$sh = New-Object -ComObject Shell.Application; "
        "$b = $sh.BrowseForFolder(0, 'Wintool', 0, 0); "
        "if ($null -ne $b) { $p = $b.Self.Path; "
        + b64_emit
        + " }"
    )
    script_forms = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$f.Description = 'Wintool'; "
        "$f.ShowNewFolderButton = $true; "
        "$dr = $f.ShowDialog(); "
        "if ($dr -eq [System.Windows.Forms.DialogResult]::OK) { $p = $f.SelectedPath; "
        + b64_emit
        + " }"
    )

    for ps in _powershell_candidates():
        p = _run_powershell(ps, script_com)
        if p:
            return p
        p = _run_powershell(ps, script_forms)
        if p:
            return p

    return None


def _decode_subprocess_path_bytes(raw: bytes) -> str:
    """终端/子进程原始字节，尽量还原为 str（含中文路径）。"""
    if not raw:
        return ""
    raw = raw.strip()
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le", errors="replace")
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="replace")
    try:
        return raw.decode("utf-8", errors="strict")
    except Exception:
        pass
    if b"\x00" in raw and len(raw) % 2 == 0:
        try:
            return raw.decode("utf-16-le", errors="replace")
        except Exception:
            pass
    try:
        return raw.decode("gbk", errors="replace")
    except Exception:
        pass
    return raw.decode("utf-8", errors="replace")


def pick_folder_zenity() -> str | None:
    z = shutil.which("zenity")
    if not z:
        return None
    try:
        r = subprocess.run(
            [z, "--file-selection", "--directory", "--title=Wintool"],
            capture_output=True,
            timeout=300,
        )
    except Exception:
        return None
    out = _decode_subprocess_path_bytes(r.stdout or b"")
    if r.returncode != 0 or not out.strip():
        return None
    return out.strip()


def pick_folder_tkinter() -> str | None:
    script = (
        "import sys\n"
        "import tkinter as tk\n"
        "from tkinter import filedialog\n"
        "r = tk.Tk()\n"
        "r.withdraw()\n"
        "r.attributes('-topmost', True)\n"
        "p = filedialog.askdirectory(title='Wintool')\n"
        "r.destroy()\n"
        "sys.stdout.buffer.write((p or '').encode('utf-8'))\n"
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            timeout=300,
            env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":0")},
        )
    except Exception:
        return None
    out = _decode_subprocess_path_bytes(r.stdout or b"")
    if not out.strip():
        return None
    return out.strip()


def pick_folder_native() -> str | None:
    """依次尝试：Windows PowerShell 对话框 → zenity → tkinter。"""
    p = pick_folder_powershell()
    if p:
        return windows_path_to_wsl(p)
    p = pick_folder_zenity()
    if p:
        return p
    p = pick_folder_tkinter()
    return p
