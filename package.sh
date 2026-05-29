#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 打包脚本 - 创建可独立部署的包
# 用途：将项目打包成可在无网络环境下部署的压缩包

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }

# 配置
VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="wintool_${VERSION}"
BUILD_DIR="build/${PACKAGE_NAME}"
ARCHIVE_NAME="${PACKAGE_NAME}.tar.gz"

echo_title "========================================="
echo_title "  Wintool 打包工具"
echo_title "========================================="
echo ""

# 1. 清理旧的构建
echo_info "清理旧的构建目录..."
rm -rf build
mkdir -p "$BUILD_DIR"

# 2. 复制项目文件
echo_info "复制项目文件..."
cp -r \
    app.py \
    requirements.txt \
    run.sh \
    README.md \
    static \
    templates \
    tools \
    data \
    scripts \
    "$BUILD_DIR/"

# 3. 创建虚拟环境并安装依赖
echo_info "创建虚拟环境..."
python3 -m venv "$BUILD_DIR/.venv"

echo_info "安装依赖到虚拟环境..."
"$BUILD_DIR/.venv/bin/pip" install --upgrade pip -q
"$BUILD_DIR/.venv/bin/pip" install -r requirements.txt -q

# 4. 创建启动脚本（适配打包环境）
echo_info "创建启动脚本..."
cat > "$BUILD_DIR/start.sh" << 'EOF'
#!/usr/bin/env bash
# Wintool 启动脚本（打包版本）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 使用打包的虚拟环境
if [[ ! -x ".venv/bin/python" ]]; then
    echo "错误：虚拟环境不存在"
    exit 1
fi

# 执行统一启动脚本
exec bash run.sh "$@"
EOF

chmod +x "$BUILD_DIR/start.sh"

# 5. 创建 Windows 启动脚本
echo_info "创建 Windows 启动脚本..."
cat > "$BUILD_DIR/start.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo ========================================
echo   Wintool 启动 (Windows)
echo ========================================
echo.

REM 检查 WSL
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 WSL
    echo 请先安装 WSL: https://aka.ms/wsl
    pause
    exit /b 1
)

REM 获取当前目录的 WSL 路径
for /f "delims=" %%i in ('wsl wslpath -a "%CD%"') do set WSL_PATH=%%i

echo [信息] 启动 Wintool...
wsl bash "%WSL_PATH%/start.sh"

pause
EOF

# 6. 创建停止脚本
cat > "$BUILD_DIR/stop.sh" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
exec bash run.sh stop
EOF

chmod +x "$BUILD_DIR/stop.sh"

# 7. 创建部署说明
echo_info "创建部署说明..."
cat > "$BUILD_DIR/DEPLOY.md" << 'EOF'
# Wintool 部署说明

## 快速开始

### Linux / macOS / WSL
```bash
./start.sh
```

### Windows
双击运行 `start.bat`

## 目录结构
```
wintool/
├── start.sh          # Linux/macOS/WSL 启动脚本
├── start.bat         # Windows 启动脚本
├── stop.sh           # 停止脚本
├── run.sh            # 统一启动逻辑
├── app.py            # 主程序
├── .venv/            # Python 虚拟环境（已包含所有依赖）
├── data/             # 数据目录
├── static/           # 静态资源
├── templates/        # 模板文件
└── tools/            # 工具模块
```

## 系统要求

- Python 3.7+
- Linux / macOS / WSL (Windows)
- 端口 5001 可用

## 常见问题

### 1. 启动失败
检查日志文件：`/tmp/wintool.log`

### 2. 端口被占用
修改环境变量：
```bash
export PORT=5002
./start.sh
```

### 3. 权限问题
```bash
chmod +x start.sh stop.sh run.sh
```

## 数据备份

重要数据位于 `data/` 目录，建议定期备份：
```bash
tar -czf wintool_data_backup_$(date +%Y%m%d).tar.gz data/
```

## 更新

1. 备份 `data/` 目录
2. 解压新版本
3. 恢复 `data/` 目录
4. 重新启动

## 技术支持

- 项目地址: https://github.com/IanLeto/wintool
- 问题反馈: 提交 Issue
EOF

# 8. 清理不必要的文件
echo_info "清理不必要的文件..."
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$BUILD_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$BUILD_DIR" -type f -name ".DS_Store" -delete 2>/dev/null || true

# 9. 创建压缩包
echo_info "创建压缩包..."
cd build
tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME"
cd ..

# 10. 计算文件大小和哈希
ARCHIVE_PATH="build/$ARCHIVE_NAME"
SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
HASH=$(sha256sum "$ARCHIVE_PATH" | cut -d' ' -f1)

echo ""
echo_title "========================================="
echo_title "  ✓ 打包完成！"
echo_title "========================================="
echo_info "包名称: $ARCHIVE_NAME"
echo_info "大小: $SIZE"
echo_info "SHA256: $HASH"
echo_info "位置: $ARCHIVE_PATH"
echo_title "========================================="
echo ""
echo_info "部署方法:"
echo "  1. 将压缩包传输到目标服务器"
echo "  2. 解压: tar -xzf $ARCHIVE_NAME"
echo "  3. 进入目录: cd $PACKAGE_NAME"
echo "  4. 启动: ./start.sh"
echo ""
echo_info "或在 Windows 上双击 start.bat"
echo ""
