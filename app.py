# -*- coding: utf-8 -*-
"""
Wintool - Windows 文件管理工具
Web 界面 + Flask 后端，可插拔工具架构。
"""
import json
import os

from flask import Flask, render_template, request, jsonify
from tools import TOOLS

app = Flask(__name__)


def _is_localhost():
    a = request.remote_addr or ""
    return a in ("127.0.0.1", "::1", "localhost") or a.startswith("127.")


@app.route("/api/pick-folder", methods=["POST"])
def api_pick_folder():
    """仅本机：弹出系统文件夹选择，返回 WSL 风格路径。"""
    if not _is_localhost():
        return jsonify({"ok": False, "error": "仅本机可打开文件夹选择"}), 403
    from scripts.path_picker import pick_folder_native

    p = pick_folder_native()
    if not p:
        return jsonify(
            {
                "ok": False,
                "error": "未选择文件夹，或当前环境无法弹出对话框（可改用粘贴路径）",
            }
        )
    return jsonify({"ok": True, "path": p})


@app.route("/api/path-presets", methods=["GET"])
def api_path_presets():
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "data", "common_paths.json")
    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"presets": []}
    if not isinstance(data.get("presets"), list):
        data = {"presets": []}
    return jsonify(data)


def _tool_by_id(tool_id):
    for t in TOOLS:
        if t.TOOL_ID == tool_id:
            return t
    return None


@app.route("/")
def index():
    tools_data = [{"id": t.TOOL_ID, "name": t.TOOL_NAME} for t in TOOLS]
    return render_template("index.html", tools=tools_data)


@app.route("/tools/<tool_id>")
def tool_page(tool_id):
    tool_cls = _tool_by_id(tool_id)
    if not tool_cls:
        from flask import abort
        abort(404)
    return render_template(
        "tool.html",
        tool_id=tool_cls.TOOL_ID,
        tool_name=tool_cls.TOOL_NAME,
        form_html=tool_cls.get_form_html(),
    )


def _register_tool_routes():
    """为每个工具注册 /api/tools/<tool_id>/... 路由。"""
    from flask import Blueprint

    for tool_cls in TOOLS:
        bp = Blueprint(f"tool_{tool_cls.TOOL_ID}", __name__, url_prefix=f"/api/tools/{tool_cls.TOOL_ID}")
        tool_cls.register_routes(bp)
        app.register_blueprint(bp)


_register_tool_routes()


def main():
    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    main()
