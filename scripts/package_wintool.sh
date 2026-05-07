#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# 打包 Wintool 工具（仅代码，不包含 data 目录）
# 生成密码保护的压缩包，密码为 123

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="wintool_${TIMESTAMP}.zip"
PASSWORD="123"

cd "$PROJECT_DIR"

echo "========================================="
echo "Wintool 打包工具"
echo "========================================="
echo "项目目录: $PROJECT_DIR"
echo "输出文件: $OUTPUT_FILE"
echo "压缩密码: $PASSWORD"
echo ""

# 检查 zip 命令是否存在
if ! command -v zip >/dev/null 2>&1; then
    echo "错误: 未找到 zip 命令"
    echo "请安装: sudo apt-get install zip"
    exit 1
fi

echo "正在打包代码文件..."

# 打包（排除 data 目录、__pycache__、.git 等）
zip -r -P "$PASSWORD" "$OUTPUT_FILE" \
    app.py \
    requirements.txt \
    README.md \
    README_REFACTOR.md \
    .gitignore \
    tools/ \
    templates/ \
    static/ \
    scripts/ \
    startup/ \
    windows/ \
    docs/ \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.git*" \
    -x "data/*" \
    -x "*.log" \
    -x ".venv/*" \
    -x "venv/*" \
    2>&1 | grep -v "adding:" || true

if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo "========================================="
    echo "打包完成！"
    echo "========================================="
    echo "文件: $OUTPUT_FILE"
    echo "大小: $FILE_SIZE"
    echo "密码: $PASSWORD"
    echo ""
    echo "解压命令: unzip -P 123 $OUTPUT_FILE"
    echo "========================================="
else
    echo ""
    echo "错误: 打包失败"
    exit 1
fi
