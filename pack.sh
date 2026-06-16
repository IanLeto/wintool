#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 内网版本打包脚本
# 用途：将内网版本（Python 后端 + Vue 前端）打包成加密压缩包

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="wintool-inner-${TIMESTAMP}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"
OUTPUT_FILE="${SCRIPT_DIR}/${PACKAGE_NAME}.zip"
PASSWORD="123"

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

echo_title "========================================="
echo_title "  Wintool 内网版本打包工具"
echo_title "========================================="
echo ""

# 检查 zip 命令
if ! command -v zip >/dev/null 2>&1; then
    echo_error "未找到 zip 命令"
    echo_error "请先安装: brew install zip (macOS) 或 apt-get install zip (Linux)"
    exit 1
fi

# 清理旧的临时目录
if [[ -d "$TEMP_DIR" ]]; then
    echo_info "清理旧的临时目录..."
    rm -rf "$TEMP_DIR"
fi

# 创建临时目录
echo_info "创建临时目录: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo ""
echo_info "开始复制文件..."

# 复制 Python 后端
echo_info "  [1/5] 复制 Python 后端..."
mkdir -p "$TEMP_DIR/backend-python"
cp -r "$SCRIPT_DIR/backend-python/"* "$TEMP_DIR/backend-python/"

# 复制前端（排除 node_modules）
echo_info "  [2/5] 复制前端代码..."
mkdir -p "$TEMP_DIR/frontend"
rsync -av --exclude='node_modules' --exclude='dist' --exclude='.vite' \
    "$SCRIPT_DIR/frontend/" "$TEMP_DIR/frontend/"

# 复制启动脚本
echo_info "  [3/5] 复制启动脚本..."
cp "$SCRIPT_DIR/inner.sh" "$TEMP_DIR/"
chmod +x "$TEMP_DIR/inner.sh"

# 复制数据目录（如果存在）
if [[ -d "$SCRIPT_DIR/code_snippets" ]]; then
    echo_info "  [4/5] 复制数据文件..."
    cp -r "$SCRIPT_DIR/code_snippets" "$TEMP_DIR/"
else
    echo_warn "  [4/5] 数据目录不存在，跳过"
    mkdir -p "$TEMP_DIR/code_snippets"
fi

# 创建 README
echo_info "  [5/5] 创建说明文档..."
cat > "$TEMP_DIR/README_INNER.md" << 'EOF'
# Wintool 内网版本使用说明

## 📦 包含内容

- `backend-python/` - Python Flask 后端
- `frontend/` - Vue 3 前端
- `inner.sh` - 启动脚本
- `code_snippets/` - 数据存储目录
- `README_INNER.md` - 本说明文档

## 🚀 快速开始

### 1. 环境要求

- **Python 3.7+** （必需）
- **Node.js 16+** （必需）
- **pip3** （Python 包管理器）
- **npm** （Node.js 包管理器）

### 2. 安装依赖

#### Python 依赖
```bash
cd backend-python
pip3 install -r requirements.txt --user
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 3. 启动服务

```bash
chmod +x inner.sh
./inner.sh
```

启动后访问：http://localhost:5173

### 4. 停止服务

按 `Ctrl+C` 停止所有服务

## 📝 功能说明

### 代码片段库
- ✅ 添加/编辑/删除代码片段
- ✅ 搜索和筛选
- ✅ 一键复制代码
- ✅ 数据持久化到本地文件

### 数据存储
所有数据保存在 `code_snippets/snippets.json` 文件中

## 🔧 故障排除

### Python 依赖安装失败
```bash
# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --user
```

### 前端依赖安装失败
```bash
# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

### 端口被占用
- 后端端口：8080
- 前端端口：5173

如果端口被占用，请先关闭占用端口的程序

## 📞 技术支持

如有问题，请联系开发团队

---

**版本**: 1.0.0 (内网版)  
**打包时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo ""
echo_info "文件复制完成"
echo ""

# 打包
echo_info "开始打包..."
cd /tmp
if zip -r -P "$PASSWORD" "$OUTPUT_FILE" "$PACKAGE_NAME" >/dev/null 2>&1; then
    echo_info "打包成功！"
else
    echo_error "打包失败"
    exit 1
fi

# 清理临时目录
echo_info "清理临时文件..."
rm -rf "$TEMP_DIR"

# 显示结果
echo ""
echo_title "========================================="
echo_title "  打包完成！"
echo_title "========================================="
echo ""
echo_info "输出文件: $OUTPUT_FILE"
echo_info "文件大小: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo_info "压缩密码: $PASSWORD"
echo ""
echo_warn "解压命令: unzip -P $PASSWORD $(basename "$OUTPUT_FILE")"
echo ""
echo_info "可以通过邮件将此文件发送到内网环境"
echo ""
