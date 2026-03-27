#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
体重管理数据库初始化脚本
运行此脚本来创建数据库表
"""
from tools.body_weight_db import init_tables

if __name__ == "__main__":
    print("正在初始化体重管理数据库表...")
    try:
        init_tables()
        print("✓ 数据库表初始化成功！")
        print("\n已创建以下表：")
        print("  - user_profile (用户配置)")
        print("  - daily_logs (每日记录)")
        print("  - strategy_versions (策略版本)")
        print("  - weekly_reviews (周报)")
        print("\n现在可以启动应用并使用体重管理工具了。")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        print("\n请检查：")
        print("  1. 数据库连接信息是否正确")
        print("  2. 数据库服务是否正常运行")
        print("  3. 用户是否有创建表的权限")
