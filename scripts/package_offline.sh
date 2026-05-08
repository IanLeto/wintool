#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 离线打包脚本
# 用途：打包代码 + 所有依赖包，供内网环境部署
# 生成密码保护的压缩包，密码为 123

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="wintool_offline_${TIMESTAMP}.zip"
PASSWORD="123"
TEMP_DIR="${PROJECT_DIR}/temp_package"

cd "$PROJECT_DIR"

echo "========================================="
echo "Wintool 离线打包工具"
echo "========================================="
echo "项目目录: $PROJECT_DIR"
echo "输出文件: $OUTPUT_FILE"
echo "压缩密码: $PASSWORD"
echo ""

# 检查必要命令
if ! command -v zip >/dev/null 2>&1; then
    echo "错误: 未找到 zip 命令"
    echo "请安装: sudo apt-get install zip 或 brew install zip"
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "错误: 未找到 python 命令"
    exit 1
fi

# 确定 Python 命令
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "使用 Python: $($PYTHON_CMD --version)"
echo ""

# 清理旧的临时目录
if [ -d "$TEMP_DIR" ]; then
    echo "清理旧的临时目录..."
    rm -rf "$TEMP_DIR"
fi

mkdir -p "$TEMP_DIR"

echo "步骤 1/4: 下载 Python 依赖包到本地..."
echo "----------------------------------------"

# 创建依赖目录
mkdir -p "$TEMP_DIR/vendor"

# 下载依赖包（使用 pip download）
if [ -f "requirements.txt" ]; then
    echo "正在下载依赖包..."
    $PYTHON_CMD -m pip download -r requirements.txt -d "$TEMP_DIR/vendor" --no-deps 2>&1 || {
        echo "警告: 部分依赖下载失败，尝试使用 --no-binary 选项..."
        $PYTHON_CMD -m pip download -r requirements.txt -d "$TEMP_DIR/vendor" 2>&1 || {
            echo "错误: 依赖下载失败"
            echo "请确保网络连接正常，或手动下载依赖包"
            rm -rf "$TEMP_DIR"
            exit 1
        }
    }
    echo "✓ 依赖包下载完成"
else
    echo "警告: 未找到 requirements.txt"
fi

echo ""
echo "步骤 2/4: 复制项目文件..."
echo "----------------------------------------"

# 复制项目文件到临时目录
rsync -a --exclude='temp_package' \
    --exclude='data' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='*.zip' \
    --exclude='.DS_Store' \
    "$PROJECT_DIR/" "$TEMP_DIR/wintool/"

echo "✓ 项目文件复制完成"

echo ""
echo "步骤 3/4: 创建部署脚本..."
echo "----------------------------------------"

# 创建离线安装脚本
cat > "$TEMP_DIR/install_offline.sh" << 'INSTALL_SCRIPT'
#!/usr/bin/env bash
# Wintool 离线安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENDOR_DIR="$SCRIPT_DIR/vendor"
WINTOOL_DIR="$SCRIPT_DIR/wintool"

echo "========================================="
echo "Wintool 离线安装"
echo "========================================="
echo ""

# 检测 Python
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "错误: 未找到 Python 环境"
    echo "请先安装 Python 3.7+"
    exit 1
fi

echo "检测到 Python: $($PYTHON_CMD --version)"
echo ""

# 检查 pip
if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
    echo "错误: pip 未安装"
    echo "请先安装 pip"
    exit 1
fi

echo "步骤 1/3: 安装依赖包（离线模式）..."
echo "----------------------------------------"

if [ -d "$VENDOR_DIR" ] && [ "$(ls -A $VENDOR_DIR 2>/dev/null)" ]; then
    cd "$VENDOR_DIR"
    for pkg in *.whl *.tar.gz; do
        if [ -f "$pkg" ]; then
            echo "安装: $pkg"
            $PYTHON_CMD -m pip install --no-index --find-links=. "$pkg" || {
                echo "警告: $pkg 安装失败，继续..."
            }
        fi
    done
    echo "✓ 依赖包安装完成"
else
    echo "警告: 未找到依赖包目录，跳过依赖安装"
fi

echo ""
echo "步骤 2/3: 创建数据目录..."
echo "----------------------------------------"

cd "$WINTOOL_DIR"
mkdir -p data/media_collection
mkdir -p data/text_documents
mkdir -p data/prompt_library

# 创建示例配置文件
if [ ! -f "data/common_paths.json" ]; then
    cat > data/common_paths.json << 'EOF'
{
  "presets": [
    {
      "label": "桌面",
      "path": "/Users/你的用户名/Desktop"
    }
  ]
}
EOF
fi

echo "✓ 数据目录创建完成"

echo ""
echo "步骤 3/3: 设置启动脚本权限..."
echo "----------------------------------------"

chmod +x startup/*.sh startup/*.command 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

echo "✓ 权限设置完成"

echo ""
echo "========================================="
echo "安装完成！"
echo "========================================="
echo ""
echo "启动方式："
echo "  方式 1: cd $WINTOOL_DIR && $PYTHON_CMD app.py"
echo "  方式 2: cd $WINTOOL_DIR && ./startup/run.sh"
echo ""
echo "访问地址: http://127.0.0.1:5001"
echo "========================================="
INSTALL_SCRIPT

chmod +x "$TEMP_DIR/install_offline.sh"

# 创建 Windows 批处理安装脚本
cat > "$TEMP_DIR/install_offline.bat" << 'INSTALL_BAT'
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo Wintool 离线安装 (Windows)
echo =========================================
echo.

REM 检测 Python
set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo 错误: 未找到 Python 环境
        echo 请先安装 Python 3.7+
        pause
        exit /b 1
    )
)

echo 检测到 Python: 
%PYTHON_CMD% --version
echo.

REM 检查 pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip 未安装
    pause
    exit /b 1
)

echo 步骤 1/3: 安装依赖包（离线模式）...
echo ----------------------------------------

if exist "vendor\" (
    cd vendor
    for %%f in (*.whl *.tar.gz) do (
        echo 安装: %%f
        %PYTHON_CMD% -m pip install --no-index --find-links=. "%%f" 2>nul || echo 警告: %%f 安装失败
    )
    cd ..
    echo √ 依赖包安装完成
) else (
    echo 警告: 未找到依赖包目录
)

echo.
echo 步骤 2/3: 创建数据目录...
echo ----------------------------------------

cd wintool
if not exist "data\" mkdir data
if not exist "data\media_collection\" mkdir data\media_collection
if not exist "data\text_documents\" mkdir data\text_documents
if not exist "data\prompt_library\" mkdir data\prompt_library

if not exist "data\common_paths.json" (
    echo {"presets": []} > data\common_paths.json
)

echo √ 数据目录创建完成

echo.
echo 步骤 3/3: 完成...
echo ----------------------------------------
echo √ 安装完成

echo.
echo =========================================
echo 安装完成！
echo =========================================
echo.
echo 启动方式: 
echo   cd wintool
echo   %PYTHON_CMD% app.py
echo.
echo 访问地址: http://127.0.0.1:5001
echo =========================================
echo.
pause
INSTALL_BAT

# 创建 README
cat > "$TEMP_DIR/README_OFFLINE.txt" << 'README'
Wintool 离线部署包
==================

本压缩包包含：
1. wintool/ - 完整项目代码
2. vendor/ - Python 依赖包（离线安装用）
3. install_offline.sh - Linux/macOS 安装脚本
4. install_offline.bat - Windows 安装脚本

部署步骤：
----------

### Linux / macOS:
1. 解压: unzip -P 123 wintool_offline_XXXXXX.zip
2. 运行: ./install_offline.sh
3. 启动: cd wintool && python3 app.py

### Windows:
1. 解压压缩包（密码: 123）
2. 双击运行: install_offline.bat
3. 启动: cd wintool && python app.py

环境要求：
----------
- Python 3.7+ （必须）
- pip （必须）
- 无需网络连接

注意事项：
----------
1. 本包不包含 data 目录，首次运行会自动创建
2. 如果依赖安装失败，可能是 Python 版本不兼容
3. 建议使用 Python 3.8 - 3.11

访问地址：
----------
http://127.0.0.1:5001

解压密码：
----------
123
README

echo "✓ 部署脚本创建完成"

echo ""
echo "步骤 4/4: 打包压缩..."
echo "----------------------------------------"

cd "$TEMP_DIR"

# 打包所有文件
zip -r -P "$PASSWORD" "$PROJECT_DIR/$OUTPUT_FILE" \
    wintool/ \
    vendor/ \
    install_offline.sh \
    install_offline.bat \
    README_OFFLINE.txt \
    2>&1 | grep -v "adding:" || true

cd "$PROJECT_DIR"

# 清理临时目录
echo "清理临时文件..."
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
    echo "包含内容:"
    echo "  - 完整项目代码"
    echo "  - Python 依赖包（离线）"
    echo "  - 自动安装脚本"
    echo ""
    echo "解压命令: unzip -P 123 $OUTPUT_FILE"
    echo "========================================="
else
    echo ""
    echo "错误: 打包失败"
    exit 1
fi
