#!/usr/bin/env python3
"""
解压所有 wheel 文件到 libs 目录
用于内网环境，无法使用 pip
"""

import zipfile
import os
import sys
from pathlib import Path

def extract_wheel(whl_file, target_dir):
    """解压单个 wheel 文件"""
    print(f"解压: {whl_file.name}")
    try:
        with zipfile.ZipFile(whl_file, 'r') as zip_ref:
            # 解压所有文件
            for member in zip_ref.namelist():
                # 跳过 .dist-info 目录（元数据）
                if '.dist-info/' in member:
                    continue
                # 跳过 __pycache__
                if '__pycache__' in member:
                    continue
                
                # 解压文件
                zip_ref.extract(member, target_dir)
        return True
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    # 当前目录
    current_dir = Path.cwd()
    
    # 查找 python-packages 目录
    packages_dir = current_dir / "python-packages"
    if not packages_dir.exists():
        print(f"错误: 未找到 python-packages 目录")
        sys.exit(1)
    
    # 创建 libs 目录
    libs_dir = current_dir / "libs"
    libs_dir.mkdir(exist_ok=True)
    
    print(f"解压目录: {packages_dir}")
    print(f"目标目录: {libs_dir}")
    print()
    
    # 解压所有 wheel 文件
    whl_files = list(packages_dir.glob("*.whl"))
    if not whl_files:
        print("错误: 未找到 wheel 文件")
        sys.exit(1)
    
    print(f"找到 {len(whl_files)} 个 wheel 文件")
    print()
    
    success_count = 0
    for whl_file in whl_files:
        if extract_wheel(whl_file, libs_dir):
            success_count += 1
    
    print()
    print(f"完成: {success_count}/{len(whl_files)} 个文件解压成功")
    
    if success_count == len(whl_files):
        print("✅ 所有依赖已解压到 libs 目录")
        sys.exit(0)
    else:
        print("⚠️  部分文件解压失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
