# -*- coding: utf-8 -*-
"""
工具：省考公告入口 — 根据 data/provincial_exam.json 渲染。
支持「官网」为单个字符串或 URL 数组；可选「说明」；多链接时尽量用说明里按顿号拆分的短标题。
"""
from __future__ import annotations

import html
import json
import os
import re
from urllib.parse import urlparse

from .base import BaseTool

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "exam_announcement_sites.json"
)


def _is_safe_http_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    try:
        p = urlparse(url.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _normalize_urls(raw) -> list:
    """官网 字段：string -> [url]，list -> 过滤后的 url 列表。"""
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = raw.strip()
        return [raw] if _is_safe_http_url(raw) else []
    if isinstance(raw, list):
        out = []
        for u in raw:
            if isinstance(u, str) and _is_safe_http_url(u):
                out.append(u.strip())
        return out
    return []


def _labels_for_links(desc: str | None, n: int) -> list:
    """
    多链接时：尝试把「说明」按顿号/逗号拆成 n 段作为按钮文案；
    段数与链接数不一致时用「入口 1」「入口 2」…
    """
    if n <= 0:
        return []
    if n == 1:
        return ["官网"]
    if not desc:
        return [f"入口 {i + 1}" for i in range(n)]
    parts = re.split(r"[、，,;；]", desc)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) == n:
        return parts
    return [f"入口 {i + 1}" for i in range(n)]


def _render_region_card(region: str, urls: list, desc: str | None) -> str:
    parts = ['<article class="shore-region-card">']
    parts.append(f'<header class="shore-region-head"><span class="shore-region-name">{html.escape(region)}</span></header>')
    if desc:
        parts.append(f'<p class="shore-region-note">{html.escape(desc)}</p>')
    parts.append('<div class="shore-region-links">')
    n = len(urls)
    if n == 1:
        u = urls[0]
        parts.append(
            "<a"
            f' href="{html.escape(u, quote=True)}"'
            ' class="shore-link-inline shore-link-primary"'
            ' target="_blank" rel="noopener noreferrer">打开官网</a>'
        )
    else:
        labels = _labels_for_links(desc, n)
        for i, u in enumerate(urls):
            label = labels[i] if i < len(labels) else f"入口 {i + 1}"
            parts.append(
                "<a"
                f' href="{html.escape(u, quote=True)}"'
                ' class="shore-link-inline"'
                ' target="_blank" rel="noopener noreferrer">'
                f"{html.escape(label)}</a>"
            )
    parts.append("</div></article>")
    return "".join(parts)


def _render_html(obj: dict) -> str:
    parts = [
        '<div class="tool-form shore-tool-form provincial-tool-form">',
        '<p class="desc">各省公务员考试公告相关入口。数据来自 <code>data/exam_announcement_sites.json</code>；同一地区多个链接时，按钮文案尽量与「说明」中顿号分隔的条目对应。</p>',
    ]
    if obj.get("更新时间") is not None:
        parts.append(
            f'<p class="shore-meta">更新时间：{html.escape(str(obj["更新时间"]))}</p>'
        )
    if obj.get("数据说明") is not None:
        parts.append(
            f'<p class="shore-desc">{html.escape(str(obj["数据说明"]))}</p>'
        )

    rows = obj.get("官网列表")
    if not isinstance(rows, list) or not rows:
        parts.append('<p class="error-text">官网列表为空</p></div>')
        return "".join(parts)

    parts.append('<h3 class="shore-section-title">官网列表</h3>')
    parts.append('<div class="shore-region-grid">')

    for row in rows:
        if not isinstance(row, dict):
            continue
        region = row.get("地区") or row.get("region")
        if region is None:
            continue
        region = str(region).strip()
        if not region:
            continue
        urls = _normalize_urls(row.get("官网"))
        if not urls:
            continue
        desc = row.get("说明")
        if desc is not None:
            desc = str(desc).strip() or None
        parts.append(_render_region_card(region, urls, desc))

    parts.append("</div></div>")
    return "".join(parts)


class ProvincialExamTool(BaseTool):
    TOOL_ID = "provincial_exam"
    TOOL_NAME = "省考公告入口"

    @classmethod
    def get_form_html(cls) -> str:
        try:
            with open(_DATA_PATH, encoding="utf-8") as f:
                obj = json.load(f)
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
