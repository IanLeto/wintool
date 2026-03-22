# -*- coding: utf-8 -*-
"""
工具：上岸信息渠道 — 根据内置 data/shore_info.json 渲染可点击跳转的表单。
更新数据时直接编辑 JSON 文件即可，无需在网页上传。
"""
import html
import json
import os
from urllib.parse import urlparse

from .base import BaseTool

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "shore_info.json")


def _is_safe_http_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    try:
        p = urlparse(url.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _load_data():
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _rows_to_items(rows):
    items = []
    if not isinstance(rows, list):
        return items
    for row in rows:
        if not isinstance(row, dict):
            continue
        region = row.get("地区") or row.get("region") or row.get("名称")
        url = row.get("官网") or row.get("url") or row.get("链接")
        if region is None or url is None:
            continue
        region = str(region).strip()
        url = str(url).strip()
        if not region or not _is_safe_http_url(url):
            continue
        items.append((region, url))
    return items


def _render_html(obj):
    parts = [
        '<div class="tool-form shore-tool-form">',
        '<p class="desc">点击下方地区名称，在新标签页打开对应官网。数据来自项目内 <code>data/shore_info.json</code>，修改该文件后刷新页面即可。</p>',
    ]
    if "更新时间" in obj and obj["更新时间"] is not None:
        parts.append(
            f'<p class="shore-meta">更新时间：{html.escape(str(obj["更新时间"]))}</p>'
        )
    if "数据说明" in obj and obj["数据说明"] is not None:
        parts.append(
            f'<p class="shore-desc">{html.escape(str(obj["数据说明"]))}</p>'
        )

    for title, key in (
        ("官网列表", "官网列表"),
        ("人事考试网补充入口", "人事考试网补充入口"),
    ):
        if key not in obj:
            continue
        items = _rows_to_items(obj[key])
        if not items:
            continue
        parts.append(f'<h3 class="shore-section-title">{html.escape(title)}</h3>')
        parts.append('<div class="shore-links-grid">')
        for region, url in items:
            parts.append(
                "<a"
                f' href="{html.escape(url, quote=True)}"'
                ' class="shore-link-card"'
                ' target="_blank" rel="noopener noreferrer">'
                f"{html.escape(region)}</a>"
            )
        parts.append("</div>")

    parts.append("</div>")
    return "".join(parts)


class ShoreInfoTool(BaseTool):
    TOOL_ID = "shore_info"
    TOOL_NAME = "上岸信息渠道"

    @classmethod
    def get_form_html(cls) -> str:
        try:
            obj = _load_data()
        except FileNotFoundError:
            return (
                '<div class="tool-form"><p class="desc error-text">'
                f"未找到数据文件：{_DATA_PATH}</p></div>"
            )
        except json.JSONDecodeError as e:
            return (
                f'<div class="tool-form"><p class="desc error-text">'
                f"JSON 解析失败：{html.escape(str(e))}</p></div>"
            )
        if not isinstance(obj, dict):
            return '<div class="tool-form"><p class="desc error-text">数据格式错误</p></div>'
        return _render_html(obj)
