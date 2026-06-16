#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 内网版本启动脚本
# 用途：启动 Python 后端 + Vue 前端（内网环境，无需 JDK/Maven）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend-python"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PID_DIR="$SCRIPT_DIR/.pids"

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
echo_service() { echo -e "${BLUE}[SERVICE]${NC} $*"; }

# 创建 PID 目录
mkdir -p "$PID_DIR"

# 清理函数
cleanup() {
    echo ""
    echo_warn "正在停止所有服务..."
    
    # 停止前端
    if [[ -f "$PID_DIR/frontend.pid" ]]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo_info "停止前端服务 (PID: $FRONTEND_PID)..."
            kill "$FRONTEND_PID" 2>/dev/null || true
            rm -f "$PID_DIR/frontend.pid"
        fi
    fi
    
    # 停止 Python 后端
    if [[ -f "$PID_DIR/backend-python.pid" ]]; then
        BACKEND_PID=$(cat "$PID_DIR/backend-python.pid")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo_info "停止 Python 后端服务 (PID: $BACKEND_PID)..."
            kill "$BACKEND_PID" 2>/dev/null || true
            rm -f "$PID_DIR/backend-python.pid"
        fi
    fi
    
    echo_info "所有服务已停止"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup SIGINT SIGTERM

echo_title "========================================="
echo_title "  启动 Wintool 内网版本"
echo_title "  Python 后端 + Vue 前端"
echo_title "========================================="
echo ""

# 检查 Python
if ! command -v python3 >/dev/null 2>&1; then
    echo_error "未找到 Python3"
    echo_error "请先安装 Python 3.7+: https://www.python.org/"
    exit 1
fi

echo_info "Python 版本: $(python3 --version)"

# 检查 Node.js
if ! command -v node >/dev/null 2>&1; then
    echo_error "未找到 Node.js"
    echo_error "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo_info "Node.js 版本: $(node --version)"
echo ""

# 检查 Python 依赖
echo_service "检查 Python 依赖..."
cd "$BACKEND_DIR"
if ! python3 -c "import flask" 2>/dev/null; then
    echo_warn "Flask 未安装，正在安装依赖..."
    pip3 install -r requirements.txt --user
    echo_info "依赖安装完成"
fi
echo ""

# 启动 Python 后端
echo_service "启动 Python 后端..."
cd "$BACKEND_DIR"
nohup python3 app.py > "$PID_DIR/backend-python.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_DIR/backend-python.pid"
echo_info "Python 后端已启动 (PID: $BACKEND_PID)"
echo_info "日志文件: $PID_DIR/backend-python.log"
echo_info "访问地址: http://localhost:8080"
echo ""

# 等待后端启动
sleep 2

# 检查前端依赖
echo_service "检查前端依赖..."
cd "$FRONTEND_DIR"
if [[ ! -d "node_modules" ]]; then
    echo_warn "未找到 node_modules，开始安装依赖..."
    npm install
    echo_info "依赖安装完成"
fi
echo ""

# 启动前端
echo_service "启动前端服务..."
cd "$FRONTEND_DIR"
nohup npm run dev > "$PID_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PID_DIR/frontend.pid"
echo_info "前端服务已启动 (PID: $FRONTEND_PID)"
echo_info "日志文件: $PID_DIR/frontend.log"
echo_info "访问地址: http://localhost:5173"
echo ""

echo_title "========================================="
echo_title "  所有服务启动完成！"
echo_title "========================================="
echo ""
echo_info "服务列表："
echo_info "  - Python 后端: http://localhost:8080"
echo_info "  - Vue 前端:    http://localhost:5173"
echo ""
echo_info "日志目录: $PID_DIR"
echo ""
echo_warn "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
while true; do
    sleep 1
done
