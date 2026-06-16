#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 前端启动脚本
# 用途：启动 Vue 3 前端开发服务器

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

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
echo_title "  启动 Wintool 前端 (Vue 3)"
echo_title "========================================="
echo ""

# 检查 Node.js
if ! command -v node >/dev/null 2>&1; then
    echo_error "未找到 Node.js"
    echo_error "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo_info "Node.js 版本: $(node --version)"
echo_info "npm 版本: $(npm --version)"
echo ""

# 检查前端目录
if [[ ! -d "$FRONTEND_DIR" ]]; then
    echo_error "未找到 frontend 目录"
    echo_error "请确保项目结构完整"
    exit 1
fi

# 进入前端目录
cd "$FRONTEND_DIR"

# 检查依赖
if [[ ! -d "node_modules" ]]; then
    echo_warn "未找到 node_modules，开始安装依赖..."
    npm install
    echo_info "依赖安装完成"
    echo ""
fi

# 启动开发服务器
echo_info "启动前端开发服务器..."
echo_info "访问地址: http://localhost:5173"
echo_info "API 代理: http://localhost:8080"
echo_title "========================================="
echo ""

npm run dev
