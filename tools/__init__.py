# -*- coding: utf-8 -*-
"""
可插拔工具注册：自动发现 tools 目录下所有继承 BaseTool 的类（排除 base 本身）。
"""
import importlib
import pkgutil
from . import base

# 所有已注册的工具类
TOOLS = []


def _discover_tools():
    """扫描当前包下所有模块，收集 BaseTool 子类。"""
    global TOOLS
    TOOLS = []
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        if modname == "base":
            continue
        try:
            mod = importlib.import_module(f".{modname}", package=__name__)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, base.BaseTool)
                    and attr is not base.BaseTool
                ):
                    TOOLS.append(attr)
        except Exception:
            continue


_discover_tools()
