#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 全部启动脚本
# 用途：同时启动前端和后端服务

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }
echo_service() { echo -e "${CYAN}[SERVICE]${NC} $*"; }

# PID 文件目录
PID_DIR="$SCRIPT_DIR/.pids"
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
            # 等待进程结束
            for i in {1..10}; do
                if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                    break
                fi
                sleep 0.5
            done
            # 如果还没结束，强制杀死
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                kill -9 "$FRONTEND_PID" 2>/dev/null || true
            fi
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
                    break
                fi
                sleep 0.5
            done
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                kill -9 "$BACKEND_PID" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_DIR/backend.pid"
    fi
    
    echo_info "所有服务已停止"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM EXIT

echo_title "========================================="
echo_title "  启动 Wintool 全部服务"
echo_title "========================================="
echo ""

# 检查是否有服务正在运行
if [[ -f "$PID_DIR/frontend.pid" ]] || [[ -f "$PID_DIR/backend.pid" ]]; then
    echo_warn "检测到有服务正在运行，正在清理..."
    cleanup
fi

# 启动后端
echo_service "启动后端服务..."
cd "$SCRIPT_DIR"
nohup bash run.sh dev > "$PID_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_DIR/backend.pid"
echo_info "后端服务已启动 (PID: $BACKEND_PID)"
echo_info "日志文件: $PID_DIR/backend.log"
echo_info "访问地址: http://localhost:8080"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo_service "启动前端服务..."
cd "$SCRIPT_DIR"
nohup bash run_frontend.sh > "$PID_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PID_DIR/frontend.pid"
echo_info "前端服务已启动 (PID: $FRONTEND_PID)"
echo_info "日志文件: $PID_DIR/frontend.log"
echo_info "访问地址: http://localhost:5173 (或 5174)"
echo ""

echo_title "========================================="
echo_title "  所有服务启动完成！"
echo_title "========================================="
echo ""
echo_info "服务列表："
echo_info "  - 后端 (Spring Boot): http://localhost:8080"
echo_info "  - 前端 (Vue 3):       http://localhost:5173"
echo ""
echo_info "日志目录: $PID_DIR"
echo ""
echo_warn "按 Ctrl+C 停止所有服务"
echo ""

# 实时显示日志（可选）
echo_info "实时日志输出 (最新 20 行):"
echo_title "========================================="

# 持续监控服务状态
while true; do
    sleep 5
    
    # 检查服务是否还在运行
    SERVICES_RUNNING=0
    
    if [[ -f "$PID_DIR/backend.pid" ]]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            ((SERVICES_RUNNING++))
        else
            echo_error "后端服务已停止！"
            rm -f "$PID_DIR/backend.pid"
        fi
    fi
    
    if [[ -f "$PID_DIR/frontend.pid" ]]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            ((SERVICES_RUNNING++))
        else
            echo_error "前端服务已停止！"
            rm -f "$PID_DIR/frontend.pid"
        fi
    fi
    
    # 如果所有服务都停止了，退出
    if [[ $SERVICES_RUNNING -eq 0 ]]; then
        echo_error "所有服务都已停止，退出监控"
        break
    fi
done
