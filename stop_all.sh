#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 停止所有服务脚本
# 用途：停止所有正在运行的服务

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
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

echo_title "========================================="
echo_title "  停止 Wintool 所有服务"
echo_title "========================================="
echo ""

# 检查 PID 目录是否存在
if [[ ! -d "$PID_DIR" ]]; then
    echo_warn "未找到 PID 目录，可能没有服务在运行"
    exit 0
fi

STOPPED_COUNT=0

# 停止前端
if [[ -f "$PID_DIR/frontend.pid" ]]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo_info "停止前端服务 (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
        # 等待进程结束
        for i in {1..10}; do
            if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                echo_info "前端服务已停止"
                ((STOPPED_COUNT++))
                break
            fi
            sleep 0.5
        done
        # 如果还没结束，强制杀死
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo_warn "强制停止前端服务..."
            kill -9 "$FRONTEND_PID" 2>/dev/null || true
            ((STOPPED_COUNT++))
        fi
    else
        echo_warn "前端服务进程不存在 (PID: $FRONTEND_PID)"
    fi
    rm -f "$PID_DIR/frontend.pid"
fi

# 停止后端
if [[ -f "$PID_DIR/backend.pid" ]]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo_info "停止后端服务 (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
        for i in {1..10}; do
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                echo_info "后端服务已停止"
                ((STOPPED_COUNT++))
                break
            fi
            sleep 0.5
        done
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo_warn "强制停止后端服务..."
            kill -9 "$BACKEND_PID" 2>/dev/null || true
            ((STOPPED_COUNT++))
        fi
    else
        echo_warn "后端服务进程不存在 (PID: $BACKEND_PID)"
    fi
    rm -f "$PID_DIR/backend.pid"
fi

# 停止 Legacy
if [[ -f "$PID_DIR/legacy.pid" ]]; then
    LEGACY_PID=$(cat "$PID_DIR/legacy.pid")
    if kill -0 "$LEGACY_PID" 2>/dev/null; then
        echo_info "停止 Legacy 服务 (PID: $LEGACY_PID)..."
        kill "$LEGACY_PID" 2>/dev/null || true
        for i in {1..10}; do
            if ! kill -0 "$LEGACY_PID" 2>/dev/null; then
                echo_info "Legacy 服务已停止"
                ((STOPPED_COUNT++))
                break
            fi
            sleep 0.5
        done
        if kill -0 "$LEGACY_PID" 2>/dev/null; then
            echo_warn "强制停止 Legacy 服务..."
            kill -9 "$LEGACY_PID" 2>/dev/null || true
            ((STOPPED_COUNT++))
        fi
    else
        echo_warn "Legacy 服务进程不存在 (PID: $LEGACY_PID)"
    fi
    rm -f "$PID_DIR/legacy.pid"
fi

echo ""
echo_title "========================================="
if [[ $STOPPED_COUNT -eq 0 ]]; then
    echo_warn "没有服务需要停止"
else
    echo_info "已停止 $STOPPED_COUNT 个服务"
fi
echo_title "========================================="
