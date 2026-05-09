#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 极简打包脚本
# 用途：打包代码 + 依赖源码，内网直接运行，无需安装
# 生成密码保护的压缩包，密码为 123

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="wintool_simple_${TIMESTAMP}.zip"
PASSWORD="123"
TEMP_DIR="${PROJECT_DIR}/temp_simple_package"

cd "$PROJECT_DIR"

echo "========================================="
echo "Wintool 极简打包工具（内网专用）"
echo "========================================="
echo "项目目录: $PROJECT_DIR"
echo "输出文件: $OUTPUT_FILE"
echo "压缩密码: $PASSWORD"
echo ""

# 检查必要命令
if ! command -v zip >/dev/null 2>&1; then
    echo "错误: 未找到 zip 命令"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "使用 Python: $($PYTHON_CMD --version)"
echo ""

# 清理旧的临时目录
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

mkdir -p "$TEMP_DIR/wintool"

echo "步骤 1/3: 从本地环境复制依赖..."
echo "----------------------------------------"

# 创建 lib 目录存放依赖源码
mkdir -p "$TEMP_DIR/wintool/lib"

# 获取本地已安装的包路径（使用 flask 的实际路径）
echo "正在查找本地已安装的依赖..."
SITE_PACKAGES=$($PYTHON_CMD -c "import flask, os; print(os.path.dirname(os.path.dirname(flask.__file__)))")
echo "  本地包路径: $SITE_PACKAGES"

# 需要复制的包列表
PACKAGES=(
    "flask"
    "werkzeug"
    "jinja2"
    "click"
    "itsdangerous"
    "blinker"
    "markupsafe"
    "pymysql"
    "kafka"
)

echo ""
echo "复制依赖包到 lib 目录..."
for pkg in "${PACKAGES[@]}"; do
    if [ -d "$SITE_PACKAGES/$pkg" ]; then
        echo "  ✓ $pkg"
        cp -r "$SITE_PACKAGES/$pkg" "$TEMP_DIR/wintool/lib/"
    else
        echo "  ✗ $pkg (未找到)"
        echo ""
        echo "错误: 本地环境缺少 $pkg"
        echo "请先安装: pip install -r requirements.txt"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
done

# 复制 .dist-info 目录（包含元数据）
echo ""
echo "复制包元数据..."
for pkg in "${PACKAGES[@]}"; do
    # 查找对应的 .dist-info 目录（不区分大小写）
    dist_info=$(find "$SITE_PACKAGES" -maxdepth 1 -type d -iname "${pkg}*.dist-info" 2>/dev/null | head -1)
    if [ -n "$dist_info" ]; then
        echo "  复制: $(basename $dist_info)"
        cp -r "$dist_info" "$TEMP_DIR/wintool/lib/"
    fi
done

# 清理 __pycache__
find "$TEMP_DIR/wintool/lib" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "✓ 依赖包复制完成"

echo ""
echo "步骤 2/3: 复制项目文件..."
echo "----------------------------------------"

cd "$PROJECT_DIR"

# 复制项目文件
rsync -a --exclude='temp_simple_package' \
    --exclude='temp_package' \
    --exclude='data' \
    --exclude='lib' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='*.zip' \
    --exclude='.DS_Store' \
    --exclude='vendor' \
    "$PROJECT_DIR/" "$TEMP_DIR/wintool/"

echo "✓ 项目文件复制完成"

echo ""
echo "步骤 3/3: 创建启动脚本..."
echo "----------------------------------------"

# 创建简单的启动脚本
cat > "$TEMP_DIR/wintool/run_simple.py" << 'RUNSCRIPT'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wintool 简易启动脚本
自动将 lib 目录添加到 Python 路径
"""
import sys
import os
from pathlib import Path

# 获取脚本所在目录
script_dir = Path(__file__).parent.absolute()
lib_dir = script_dir / "lib"

# 将 lib 目录添加到 Python 路径最前面
if lib_dir.exists():
    sys.path.insert(0, str(lib_dir))
    print(f"✓ 已加载依赖库: {lib_dir}")

# 导入并运行 app
try:
    from app import app
    print("=" * 50)
    print("Wintool 启动成功！")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5001")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
except ImportError as e:
    print(f"错误: 无法导入模块 - {e}")
    print("请确保所有依赖都在 lib 目录中")
    sys.exit(1)
RUNSCRIPT

chmod +x "$TEMP_DIR/wintool/run_simple.py"

# 创建 README
cat > "$TEMP_DIR/README.txt" << 'README'
Wintool 极简部署包（内网专用）
================================

本压缩包特点：
- 无需安装任何依赖
- 无需 pip
- 只需要 Python 3.7+
- 解压即用

部署步骤：
----------

1. 解压
   unzip -P 123 wintool_simple_*.zip

2. 进入目录
   cd wintool

3. 运行
   python3 run_simple.py
   
   或
   
   python run_simple.py

4. 访问
   http://127.0.0.1:5001

说明：
------
- 所有依赖已打包在 lib/ 目录
- run_simple.py 会自动加载 lib 中的依赖
- 无需任何安装步骤

解压密码：123
README

echo "✓ 启动脚本创建完成"

echo ""
echo "打包压缩..."
echo "----------------------------------------"

cd "$TEMP_DIR"

# 打包
zip -r -P "$PASSWORD" "$PROJECT_DIR/$OUTPUT_FILE" \
    wintool/ \
    README.txt \
    2>&1 | grep -v "adding:" || true

cd "$PROJECT_DIR"

# 清理
rm -rf "$TEMP_DIR"

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
    echo "内网部署："
    echo "  1. 解压: unzip -P 123 $OUTPUT_FILE"
    echo "  2. 运行: cd wintool && python3 run_simple.py"
    echo "  3. 访问: http://127.0.0.1:5001"
    echo ""
    echo "无需安装，解压即用！"
    echo "========================================="
else
    echo "错误: 打包失败"
    exit 1
fi
