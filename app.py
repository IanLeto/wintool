# -*- coding: utf-8 -*-
"""
Wintool - Windows 文件管理工具
Web 界面 + Flask 后端，可插拔工具架构。
"""
import os
from flask import Flask, render_template, request, jsonify
from tools import TOOLS

app = Flask(__name__)


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
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
