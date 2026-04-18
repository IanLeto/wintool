#!/bin/bash

# 批量双层7z解压脚本（修正版）
# 确保每个压缩包解压到独立的子目录中

SOURCE_DIR="/mnt/y/新建文件夹"
PASSWORD="erciyuan.org"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}批量双层7z解压工具（修正版）${NC}"
echo -e "${GREEN}========================================${NC}"
echo "源目录: $SOURCE_DIR"
echo "密码: $PASSWORD"
echo "目标结构: /mnt/y/新建文件夹/压缩包名/"
echo ""

# 统计
total=0
success=0
failed=0
skipped=0

# 遍历所有.7z文件
for archive in "$SOURCE_DIR"/*.7z; do
    # 检查文件是否存在
    if [ ! -f "$archive" ]; then
        echo -e "${YELLOW}未找到.7z文件${NC}"
        continue
    fi
    
    total=$((total + 1))
    basename=$(basename "$archive" .7z)
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$total] 处理: ${basename}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 创建最终目标目录（以压缩包名命名）
    final_dir="$SOURCE_DIR/$basename"
    
    # 如果目录已存在且非空，跳过
    if [ -d "$final_dir" ] && [ "$(ls -A "$final_dir" 2>/dev/null | grep -v '^\.')" ]; then
        echo -e "${YELLOW}  ⚠ 目录已存在且非空，跳过: $basename${NC}"
        skipped=$((skipped + 1))
        echo ""
        continue
    fi
    
    # 确保目录存在
    mkdir -p "$final_dir"
    
    # 创建临时目录用于第一次解压
    temp_dir="$final_dir/.temp_stage1_$$"
    mkdir -p "$temp_dir"
    
    # ========== 第一次解压：解压外层.7z ==========
    echo -e "  ${YELLOW}[阶段1]${NC} 解压外层7z文件到临时目录..."
    if 7z x -p"$PASSWORD" -o"$temp_dir" "$archive" -y >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ 第一次解压成功${NC}"
        
        # 查找分卷文件（.7z.001 或 .001）
        first_volume=$(find "$temp_dir" -type f \( -name "*.7z.001" -o -name "*.001" \) 2>/dev/null | head -1)
        
        if [ -n "$first_volume" ]; then
            # ========== 第二次解压：解压分卷文件 ==========
            echo -e "  ${YELLOW}[阶段2]${NC} 检测到分卷文件: $(basename "$first_volume")"
            echo -e "  ${YELLOW}[阶段2]${NC} 解压分卷文件到最终目录..."
            
            if 7z x -p"$PASSWORD" -o"$final_dir" "$first_volume" -y >/dev/null 2>&1; then
                echo -e "  ${GREEN}✓ 第二次解压成功${NC}"
                
                # 删除临时目录
                rm -rf "$temp_dir"
                
                # 统计最终文件
                file_count=$(find "$final_dir" -type f 2>/dev/null | wc -l)
                dir_size=$(du -sh "$final_dir" 2>/dev/null | cut -f1)
                
                echo -e "  ${GREEN}✓ 完成！${NC}"
                echo -e "    - 最终目录: $final_dir"
                echo -e "    - 文件数: ${file_count}"
                echo -e "    - 大小: ${dir_size}"
                
                success=$((success + 1))
            else
                echo -e "  ${RED}✗ 第二次解压失败${NC}"
                rm -rf "$temp_dir"
                failed=$((failed + 1))
            fi
        else
            # 没有分卷文件，直接移动内容到最终目录
            echo -e "  ${YELLOW}⚠ 未检测到分卷文件，直接移动内容到最终目录${NC}"
            
            # 移动所有文件到最终目录
            find "$temp_dir" -mindepth 1 -maxdepth 1 -exec mv {} "$final_dir/" \; 2>/dev/null
            rm -rf "$temp_dir"
            
            file_count=$(find "$final_dir" -type f 2>/dev/null | wc -l)
            dir_size=$(du -sh "$final_dir" 2>/dev/null | cut -f1)
            
            echo -e "  ${GREEN}✓ 完成！${NC}"
            echo -e "    - 最终目录: $final_dir"
            echo -e "    - 文件数: ${file_count}"
            echo -e "    - 大小: ${dir_size}"
            
            success=$((success + 1))
        fi
    else
        echo -e "  ${RED}✗ 第一次解压失败（可能密码错误或文件损坏）${NC}"
        rm -rf "$temp_dir"
        rmdir "$final_dir" 2>/dev/null
        failed=$((failed + 1))
    fi
    
    echo ""
done

# 输出统计
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}解压完成统计${NC}"
echo -e "${GREEN}========================================${NC}"
echo "总文件数: $total"
echo -e "${GREEN}成功: $success${NC}"
if [ $skipped -gt 0 ]; then
    echo -e "${YELLOW}跳过: $skipped${NC}"
fi
if [ $failed -gt 0 ]; then
    echo -e "${RED}失败: $failed${NC}"
fi
echo ""
echo "最终目录结构示例:"
echo "  /mnt/y/新建文件夹/H2195/"
echo "  /mnt/y/新建文件夹/H2170/"
echo "  ..."
