# -*- coding: utf-8 -*-
"""
工具：媒体收藏 — 读取 data/media_shelf/ 下多个JSON文件，统一展示影视和游戏作品。
支持电影/电视剧/动漫/游戏等分类，以及「看过/玩过/未看/未玩」状态标注。
只需将同结构的JSON文件放入目录，即可自动聚合展示。
"""
from __future__ import annotations

import csv
import html
import json
import os
from collections import defaultdict

from flask import Blueprint, jsonify, request

from .base import BaseTool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "media_shelf")
_ALLOWED_SUFFIXES = {".txt", ".md", ".markdown", ".csv", ".json"}

_CATEGORY_ALIASES = {
    "电影": "movie",
    "movie": "movie",
    "movies": "movie",
    "电视剧": "tv",
    "剧集": "tv",
    "连续剧": "tv",
    "tv": "tv",
    "series": "tv",
    "动漫": "anime",
    "动画": "anime",
    "anime": "anime",
    "游戏": "game",
    "game": "game",
    "games": "game",
    "电子游戏": "game",
    "书籍": "book",
    "book": "book",
    "books": "book",
    "图书": "book",
}

_STATUS_ALIASES = {
    "看过": "watched",
    "已看": "watched",
    "看完": "watched",
    "watched": "watched",
    "done": "watched",
    "完成": "watched",
    "玩过": "watched",
    "已玩": "watched",
    "通关": "watched",
    "读过": "watched",
    "已读": "watched",
    "没看过": "unwatched",
    "没看": "unwatched",
    "未看": "unwatched",
    "想看": "unwatched",
    "待看": "unwatched",
    "unwatched": "unwatched",
    "todo": "unwatched",
    "未玩": "unwatched",
    "想玩": "unwatched",
    "待玩": "unwatched",
    "未读": "unwatched",
    "想读": "unwatched",
}

_CATEGORY_LABEL = {
    "movie": "电影",
    "tv": "电视剧",
    "anime": "动漫",
    "game": "游戏",
    "book": "书籍"
}
_STATUS_LABEL = {
    "watched": "已完成",
    "unwatched": "未完成"
}


def _normalize_category(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = str(raw).strip().lower()
    return _CATEGORY_ALIASES.get(key)


def _normalize_status(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = str(raw).strip().lower()
    return _STATUS_ALIASES.get(key)


def _safe_path_in_data(filename: str) -> str | None:
    base = os.path.realpath(_DATA_DIR)
    name = os.path.basename(filename or "")
    if not name or name in (".", ".."):
        return None
    path = os.path.realpath(os.path.join(_DATA_DIR, name))
    if not path.startswith(base + os.sep):
        return None
    if not os.path.isfile(path):
        return None
    return path


def _list_files():
    if not os.path.isdir(_DATA_DIR):
        return []
    out = []
    try:
        for ent in os.scandir(_DATA_DIR):
            if not ent.is_file():
                continue
            suf = os.path.splitext(ent.name)[1].lower()
            if suf in _ALLOWED_SUFFIXES:
                out.append(ent.name)
    except OSError:
        return []
    out.sort(key=lambda x: x.lower())
    return out


def _make_item(title: str, category: str | None, status: str | None, source: str, note: str = "") -> dict:
    return {
        "title": title.strip(),
        "category": category,
        "status": status,
        "source": source,
        "note": note.strip(),
    }


def _parse_json_file(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    out = []
    for row in data:
        if not isinstance(row, dict):
            continue
        title = (row.get("title") or row.get("名称") or row.get("name") or "").strip()
        if not title:
            continue
        category = _normalize_category(row.get("category") or row.get("分类") or row.get("type"))
        watched = row.get("watched")
        status = _normalize_status(row.get("status") or row.get("状态"))
        if status is None and isinstance(watched, bool):
            status = "watched" if watched else "unwatched"
        note = str(row.get("note") or row.get("备注") or "").strip()
        out.append(_make_item(title, category, status, source, note))
    return out


def _parse_csv_file(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        out = []
        for row in reader:
            if not isinstance(row, dict):
                continue
            title = (row.get("title") or row.get("名称") or row.get("name") or "").strip()
            if not title:
                continue
            category = _normalize_category(row.get("category") or row.get("分类") or row.get("type"))
            status = _normalize_status(row.get("status") or row.get("状态"))
            note = str(row.get("note") or row.get("备注") or "").strip()
            out.append(_make_item(title, category, status, source, note))
    return out


def _parse_text_file(path: str, source: str) -> list[dict]:
    """
    支持三种简化写法：
    1) 分类|状态|名称|备注（备注可省略）
    2) # 电影 / ## 电视剧 / ### 动漫（章节设置当前分类）
    3) - [x] 名称 或 - [ ] 名称（看过/没看过）
    """
    out = []
    current_category = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                head = line.lstrip("#").strip()
                c = _normalize_category(head)
                if c:
                    current_category = c
                continue

            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    c = _normalize_category(parts[0]) or current_category
                    s = _normalize_status(parts[1])
                    title = parts[2]
                    note = parts[3] if len(parts) >= 4 else ""
                    if title:
                        out.append(_make_item(title, c, s, source, note))
                    continue

            status = None
            title = line
            if line.startswith("- [x]") or line.startswith("* [x]"):
                status = "watched"
                title = line[5:].strip()
            elif line.startswith("- [ ]") or line.startswith("* [ ]"):
                status = "unwatched"
                title = line[5:].strip()
            elif line.startswith("- "):
                title = line[2:].strip()
            elif line.startswith("* "):
                title = line[2:].strip()

            if title:
                out.append(_make_item(title, current_category, status, source))
    return out


def _parse_file(path: str, source: str) -> list[dict]:
    ext = os.path.splitext(source)[1].lower()
    if ext == ".json":
        return _parse_json_file(path, source)
    if ext == ".csv":
        return _parse_csv_file(path, source)
    return _parse_text_file(path, source)


def _stats(items: list[dict]) -> dict:
    total = len(items)
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    for x in items:
        by_category[x.get("category") or "unknown"] += 1
        by_status[x.get("status") or "unknown"] += 1
    return {
        "total": total,
        "movie": by_category["movie"],
        "tv": by_category["tv"],
        "anime": by_category["anime"],
        "game": by_category["game"],
        "book": by_category["book"],
        "watched": by_status["watched"],
        "unwatched": by_status["unwatched"],
    }


class MediaShelfTool(BaseTool):
    TOOL_ID = "media_shelf"
    TOOL_NAME = "媒体收藏"

    @classmethod
    def get_form_html(cls) -> str:
        return f"""
        <div class="tool-form media-shelf-form" data-media-shelf data-tool-id="{html.escape(cls.TOOL_ID)}">
            <p class="desc">
                将多个JSON文件放入 <code>{html.escape(_DATA_DIR)}</code>，点击刷新后自动聚合展示。
                <br>支持影视、游戏、书籍等多种媒体类型。只需将同结构的JSON文件放入目录即可。
            </p>
            <div class="media-shelf-toolbar">
                <button type="button" class="media-shelf-refresh">刷新列表</button>
                <input type="search" class="media-shelf-search" placeholder="按名称/备注搜索…" autocomplete="off" />
                <select class="media-shelf-filter-category" aria-label="分类筛选">
                    <option value="all">全部分类</option>
                    <option value="movie">电影</option>
                    <option value="tv">电视剧</option>
                    <option value="anime">动漫</option>
                    <option value="game">游戏</option>
                    <option value="book">书籍</option>
                </select>
                <select class="media-shelf-filter-status" aria-label="状态筛选">
                    <option value="all">全部状态</option>
                    <option value="watched">已完成</option>
                    <option value="unwatched">未完成</option>
                </select>
                <select class="media-shelf-filter-source" aria-label="来源文件筛选">
                    <option value="all">全部文件</option>
                </select>
            </div>
            <div class="media-shelf-summary"></div>
            <div class="media-shelf-list-wrap">
                <p class="media-shelf-placeholder">正在加载媒体列表…</p>
            </div>
        </div>
        """

    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/items", methods=["GET"])
        def items():
            if not os.path.isdir(_DATA_DIR):
                return jsonify(
                    {
                        "ok": True,
                        "dir": _DATA_DIR,
                        "files": [],
                        "items": [],
                        "stats": _stats([]),
                        "hint": "目录不存在，先创建 data/media_shelf/ 并放入清单文件。",
                    }
                )

            source = (request.args.get("source") or "").strip()
            files = _list_files()
            target_files = files
            if source:
                if source not in files:
                    return jsonify({"ok": False, "error": "指定来源文件不存在"}), 400
                target_files = [source]

            all_items = []
            parse_errors = []
            for name in target_files:
                path = _safe_path_in_data(name)
                if not path:
                    continue
                try:
                    all_items.extend(_parse_file(path, name))
                except Exception as e:
                    parse_errors.append(f"{name}: {e}")

            all_items = [x for x in all_items if x.get("title")]
            all_items.sort(key=lambda x: (x["title"].lower(), x["source"].lower()))
            return jsonify(
                {
                    "ok": True,
                    "dir": _DATA_DIR,
                    "files": files,
                    "items": all_items,
                    "stats": _stats(all_items),
                    "errors": parse_errors,
                }
            )
