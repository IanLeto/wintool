#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量双层7z解压工具（增强版）

功能：
1. 自动处理双层压缩（外层.7z -> 分卷.7z.001/.7z.002 -> 最终内容）
2. 递归解压：如果解压后仍是压缩文件，继续解压
3. 自动删除成功解压的原始压缩包
4. 智能跳过已处理的目录
5. 详细的进度显示和错误处理

使用方法：
    python3 batch_extract_7z.py

配置：
    - SOURCE_DIR: 源目录路径
    - PASSWORD: 解压密码
    - DELETE_ORIGINAL: 是否删除原始压缩包（默认True）
    - MAX_DEPTH: 最大递归解压深度（默认3）
"""

import os
import subprocess
import shutil
import glob
from pathlib import Path
from typing import List, Tuple, Optional

# ==================== 配置区 ====================
SOURCE_DIR = "/mnt/y/新建文件夹"
PASSWORD = "erciyuan.org"
DELETE_ORIGINAL = True  # 成功后是否删除原始压缩包
MAX_DEPTH = 3  # 最大递归解压深度，防止无限循环

# 颜色代码
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# ==================== 工具函数 ====================

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.GREEN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}{text}{Colors.NC}")
    print(f"{Colors.GREEN}{'=' * 60}{Colors.NC}\n")

def print_section(text: str):
    """打印分节"""
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")

def print_success(text: str, indent: int = 2):
    """打印成功信息"""
    print(f"{' ' * indent}{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text: str, indent: int = 2):
    """打印错误信息"""
    print(f"{' ' * indent}{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text: str, indent: int = 2):
    """打印警告信息"""
    print(f"{' ' * indent}{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text: str, indent: int = 2):
    """打印信息"""
    print(f"{' ' * indent}{Colors.CYAN}{text}{Colors.NC}")

def is_archive(file_path: str) -> bool:
    """判断是否为压缩文件"""
    archive_extensions = ['.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz']
    file_lower = file_path.lower()
    
    # 检查标准扩展名
    for ext in archive_extensions:
        if ext in file_lower:
            return True
    
    return False

def find_first_volume(directory: str) -> Optional[str]:
    """查找第一个分卷文件"""
    patterns = ['*.7z.001', '*.001', '*.part1.rar', '*.part01.rar']
    for pattern in patterns:
        files = glob.glob(os.path.join(directory, pattern))
        if files:
            return files[0]
    return None

def extract_7z(archive_path: str, output_dir: str, password: str) -> bool:
    """使用7z解压文件"""
    try:
        cmd = ['7z', 'x', f'-p{password}', f'-o{output_dir}', archive_path, '-y']
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print_error(f"解压失败: {e}")
        return False

def get_dir_info(directory: str) -> Tuple[int, str]:
    """获取目录信息（文件数和大小）"""
    try:
        file_count = sum(1 for _ in Path(directory).rglob('*') if _.is_file())
        size = subprocess.check_output(['du', '-sh', directory]).decode().split()[0]
        return file_count, size
    except:
        return 0, "未知"

def has_game_content(directory: str) -> bool:
    """判断目录是否包含游戏内容（非压缩文件）"""
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if not is_archive(file) and not file.startswith('.'):
                    return True
        return False
    except:
        return False

# ==================== 核心处理函数 ====================

def recursive_extract(directory: str, depth: int = 0) -> bool:
    """
    递归解压目录中的所有压缩文件
    
    Args:
        directory: 目标目录
        depth: 当前递归深度
    
    Returns:
        是否成功解压所有文件
    """
    if depth >= MAX_DEPTH:
        print_warning(f"达到最大递归深度 {MAX_DEPTH}，停止解压", indent=4)
        return True
    
    # 查找所有压缩文件
    archives = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_archive(file):
                archives.append(os.path.join(root, file))
    
    if not archives:
        return True
    
    print_info(f"[深度 {depth + 1}] 发现 {len(archives)} 个压缩文件，继续解压...", indent=4)
    
    all_success = True
    for archive in archives:
        archive_name = os.path.basename(archive)
        print_info(f"解压: {archive_name}", indent=6)
        
        # 解压到当前目录
        parent_dir = os.path.dirname(archive)
        if extract_7z(archive, parent_dir, PASSWORD):
            print_success(f"解压成功: {archive_name}", indent=6)
            # 删除已解压的压缩文件
            try:
                os.remove(archive)
                print_info(f"已删除: {archive_name}", indent=6)
            except Exception as e:
                print_warning(f"删除失败: {e}", indent=6)
        else:
            print_error(f"解压失败: {archive_name}", indent=6)
            all_success = False
    
    # 递归处理
    if all_success and depth < MAX_DEPTH - 1:
        return recursive_extract(directory, depth + 1)
    
    return all_success

def process_single_archive(archive_path: str, stats: dict) -> bool:
    """
    处理单个压缩包
    
    Args:
        archive_path: 压缩包路径
        stats: 统计信息字典
    
    Returns:
        是否处理成功
    """
    basename = os.path.splitext(os.path.basename(archive_path))[0]
    final_dir = os.path.join(SOURCE_DIR, basename)
    
    print_section(f"[{stats['total']}] 处理: {basename}")
    
    # 检查目录是否已存在且包含游戏内容
    if os.path.exists(final_dir) and has_game_content(final_dir):
        print_warning(f"目录已存在且包含游戏内容，跳过: {basename}")
        stats['skipped'] += 1
        return True
    
    # 创建目标目录
    os.makedirs(final_dir, exist_ok=True)
    
    # 创建临时目录
    temp_dir = os.path.join(final_dir, f".temp_stage1_{os.getpid()}")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # ========== 阶段1：解压外层.7z ==========
        print_info("[阶段1] 解压外层7z文件...")
        if not extract_7z(archive_path, temp_dir, PASSWORD):
            print_error("第一次解压失败")
            shutil.rmtree(temp_dir, ignore_errors=True)
            stats['failed'] += 1
            return False
        
        print_success("第一次解压成功")
        
        # ========== 阶段2：查找并解压分卷 ==========
        first_volume = find_first_volume(temp_dir)
        
        if first_volume:
            print_info(f"[阶段2] 检测到分卷文件: {os.path.basename(first_volume)}")
            print_info("[阶段2] 解压分卷文件...")
            
            if not extract_7z(first_volume, final_dir, PASSWORD):
                print_error("第二次解压失败")
                shutil.rmtree(temp_dir, ignore_errors=True)
                stats['failed'] += 1
                return False
            
            print_success("第二次解压成功")
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            # 没有分卷，直接移动内容
            print_warning("未检测到分卷文件，直接移动内容")
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(final_dir, item)
                shutil.move(src, dst)
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # ========== 阶段3：递归解压 ==========
        print_info("[阶段3] 检查是否需要继续解压...")
        if recursive_extract(final_dir):
            print_success("递归解压完成")
        else:
            print_warning("部分文件解压失败")
        
        # ========== 统计信息 ==========
        file_count, dir_size = get_dir_info(final_dir)
        print_success("完成！")
        print_info(f"  - 最终目录: {final_dir}", indent=4)
        print_info(f"  - 文件数: {file_count}", indent=4)
        print_info(f"  - 大小: {dir_size}", indent=4)
        
        # ========== 删除原始压缩包 ==========
        if DELETE_ORIGINAL:
            try:
                os.remove(archive_path)
                print_success(f"已删除原始压缩包: {os.path.basename(archive_path)}")
            except Exception as e:
                print_warning(f"删除原始压缩包失败: {e}")
        
        stats['success'] += 1
        return True
        
    except Exception as e:
        print_error(f"处理失败: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        stats['failed'] += 1
        return False

# ==================== 主函数 ====================

def main():
    """主函数"""
    print_header("批量双层7z解压工具（增强版）")
    
    print(f"源目录: {SOURCE_DIR}")
    print(f"密码: {PASSWORD}")
    print(f"删除原始压缩包: {'是' if DELETE_ORIGINAL else '否'}")
    print(f"最大递归深度: {MAX_DEPTH}")
    print(f"目标结构: {SOURCE_DIR}/压缩包名/")
    
    # 检查源目录
    if not os.path.exists(SOURCE_DIR):
        print_error(f"源目录不存在: {SOURCE_DIR}")
        return
    
    # 查找所有.7z文件
    archives = glob.glob(os.path.join(SOURCE_DIR, "*.7z"))
    
    if not archives:
        print_warning("未找到.7z文件")
        return
    
    print(f"\n找到 {len(archives)} 个.7z文件\n")
    
    # 统计信息
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # 处理每个压缩包
    for archive in sorted(archives):
        stats['total'] += 1
        process_single_archive(archive, stats)
        print()  # 空行分隔
    
    # 输出统计
    print_header("解压完成统计")
    print(f"总文件数: {stats['total']}")
    print(f"{Colors.GREEN}成功: {stats['success']}{Colors.NC}")
    if stats['skipped'] > 0:
        print(f"{Colors.YELLOW}跳过: {stats['skipped']}{Colors.NC}")
    if stats['failed'] > 0:
        print(f"{Colors.RED}失败: {stats['failed']}{Colors.NC}")
    
    print("\n最终目录结构示例:")
    print("  /mnt/y/新建文件夹/H2195/")
    print("  /mnt/y/新建文件夹/H2170/")
    print("  ...")

if __name__ == "__main__":
    main()
