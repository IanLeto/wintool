# -*- coding: utf-8 -*-
"""
工具：关键时间节点 — 从 data/milestones.json 读取并展示时间线，仅展示、无通知。
"""
import html
import json
import os
from datetime import date, datetime

from .base import BaseTool

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "milestones.json"
)

_WEEKDAYS = "一二三四五六日"


def _parse_item_date(row: dict) -> date | None:
    ds = row.get("date") or row.get("日期")
    if not ds:
        return None
    ds = str(ds).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(ds, fmt).date()
        except ValueError:
            continue
    return None


def _fmt_cn_date(d: date) -> str:
    return f"{d.year} 年 {d.month} 月 {d.day} 日 · 周{_WEEKDAYS[d.weekday()]}"


def _relative_badge(d: date, today: date):
    """返回 (文案, css 修饰类后缀 upcoming|today|past)"""
    delta = (d - today).days
    if delta > 0:
        if delta <= 7:
            return (f"还有 {delta} 天", "upcoming-soon")
        return (f"还有 {delta} 天", "upcoming")
    if delta == 0:
        return ("就是今天", "today")
    return (f"已过 {abs(delta)} 天", "past")


def _render_html(obj: dict) -> str:
    today = date.today()
    subtitle = obj.get("subtitle") or obj.get("副标题")
    raw_items = obj.get("items") or obj.get("节点") or []

    rows = []
    if isinstance(raw_items, list):
        for row in raw_items:
            if not isinstance(row, dict):
                continue
            title = row.get("title") or row.get("标题") or row.get("name")
            if title is None:
                continue
            title = str(title).strip()
            if not title:
                continue
            d = _parse_item_date(row)
            if d is None:
                continue
            note = row.get("note") or row.get("说明") or row.get("备注")
            if note is not None:
                note = str(note).strip() or None
            time_s = row.get("time") or row.get("时刻")
            if time_s is not None:
                time_s = str(time_s).strip() or None
            rows.append(
                {
                    "title": title,
                    "date": d,
                    "note": note,
                    "time": time_s,
                    "sort_key": d,
                }
            )

    rows.sort(key=lambda x: x["sort_key"])

    parts = [
        '<div class="tool-form milestone-page">',
        '<p class="milestone-hint">数据文件 <code>data/milestones.json</code></p>',
    ]
    if subtitle:
        parts.append(f'<p class="milestone-subtitle">{html.escape(subtitle)}</p>')

    if not rows:
        parts.append('<p class="milestone-empty">暂无节点，请在 JSON 的 <code>items</code> 中添加。</p>')
        parts.append("</div>")
        return "".join(parts)

    parts.append('<ol class="milestone-timeline" role="list">')

    for item in rows:
        d = item["date"]
        badge_text, rel_class = _relative_badge(d, today)
        if (d - today).days < 0:
            state = "past"
        elif (d - today).days == 0:
            state = "today"
        else:
            state = "future"

        date_line = _fmt_cn_date(d)
        if item["time"]:
            date_line += f" · {html.escape(item['time'])}"

        parts.append(f'<li class="milestone-item milestone-item--{state} milestone-rel--{rel_class}">')
        parts.append('<span class="milestone-axis" aria-hidden="true"><span class="milestone-dot"></span></span>')
        parts.append('<div class="milestone-body">')
        parts.append(f'<div class="milestone-badge milestone-badge--{state}">{html.escape(badge_text)}</div>')
        parts.append(f'<h2 class="milestone-title">{html.escape(item["title"])}</h2>')
        parts.append(f'<p class="milestone-date">{date_line}</p>')
        if item["note"]:
            parts.append(f'<p class="milestone-note">{html.escape(item["note"])}</p>')
        parts.append("</div></li>")

    parts.append("</ol></div>")
    return "".join(parts)


class MilestonesTool(BaseTool):
    TOOL_ID = "milestones"
    TOOL_NAME = "关键时间节点"

    @classmethod
    def get_form_html(cls) -> str:
        try:
            with open(_DATA_PATH, encoding="utf-8") as f:
                obj = json.load(f)
        except FileNotFoundError:
            return (
                '<div class="tool-form milestone-page">'
                f'<p class="error-text">未找到：{html.escape(_DATA_PATH)}</p></div>'
            )
        except json.JSONDecodeError as e:
            return (
                '<div class="tool-form milestone-page">'
                f'<p class="error-text">JSON 解析失败：{html.escape(str(e))}</p></div>'
            )
        if not isinstance(obj, dict):
            return '<div class="tool-form milestone-page"><p class="error-text">数据格式错误</p></div>'
        return _render_html(obj)
