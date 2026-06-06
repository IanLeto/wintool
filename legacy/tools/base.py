# -*- coding: utf-8 -*-
"""
工具基类：所有可插拔工具需实现此接口。
- TOOL_ID: 唯一标识，用于路由
- TOOL_NAME: 显示在界面上的名称
- get_form_html(): 返回该工具的表单 HTML
- register_routes(bp): 向 blueprint 注册 API 路由
"""
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """可插拔工具的基类。新工具继承此类并放到 tools/ 目录即可被主程序加载。"""

    TOOL_ID = "unknown"
    TOOL_NAME = "未命名工具"

    @classmethod
    @abstractmethod
    def get_form_html(cls) -> str:
        """返回该工具的表单 HTML 片段。"""
        pass

    @classmethod
    def register_routes(cls, bp):
        """向 Blueprint 注册 API 路由。子类可覆盖以实现具体接口。"""
        pass
