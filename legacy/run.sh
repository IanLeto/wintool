#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 统一启动脚本
# 适用于：本地开发、内网部署、打包环境

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-5001}"
URL="http://127.0.0.1:${PORT}"
LOG_FILE="/tmp/wintool.log"

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

# 停止已有进程
stop_existing() {
    if command -v lsof >/dev/null 2>&1; then
        local pid=$(lsof -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null || true)
        if [[ -n "$pid" ]]; then
            echo_info "停止已有进程 (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
        fi
    fi
}

# 打开浏览器
open_browser() {
    local url="$1"
    sleep 1
    
    # WSL 环境
    if [[ -x /mnt/c/Windows/System32/cmd.exe ]]; then
        /mnt/c/Windows/System32/cmd.exe /c start "" "$url" >/dev/null 2>&1 && return 0
    fi
    
    # wslview
    if command -v wslview >/dev/null 2>&1; then
        wslview "$url" >/dev/null 2>&1 && return 0
    fi
    
    # Linux
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url" >/dev/null 2>&1 && return 0
    fi
    
    # macOS
    if command -v open >/dev/null 2>&1; then
        open "$url" >/dev/null 2>&1 && return 0
    fi
    
    echo_warn "无法自动打开浏览器，请手动访问: $url"
}

# 检测 Python 环境
detect_python() {
    local python_bin=""
    
    # 1. 检查打包环境（内网部署）- 优先级最高
    if [[ -f "run_simple.py" && -d "lib" ]]; then
        echo_info "检测到打包环境（内网部署模式）"
        echo_info "使用打包的依赖库: ./lib"
        exec python3 run_simple.py
        exit 0
    fi
    
    # 2. 检查虚拟环境
    if [[ -x ".venv/bin/python" ]]; then
        python_bin=".venv/bin/python"
        echo_info "使用虚拟环境: $python_bin"
    elif command -v python3 >/dev/null 2>&1; then
        python_bin="python3"
        echo_info "使用系统 Python3: $(which python3)"
    elif command -v python >/dev/null 2>&1; then
        python_bin="python"
        echo_info "使用系统 Python: $(which python)"
    else
        echo_error "未找到 Python 环境"
        echo_error "请安装 Python 3.7+ 或创建虚拟环境"
        exit 1
    fi
    
    PYTHON_BIN="$python_bin"
}

# 检查依赖
check_dependencies() {
    echo_info "检查依赖..."
    
    if ! "$PYTHON_BIN" -c "import flask" 2>/dev/null; then
        echo_warn "Flask 未安装"
        
        if [[ -f "requirements.txt" ]]; then
            echo_info "尝试安装依赖..."
            "$PYTHON_BIN" -m pip install -r requirements.txt || {
                echo_error "依赖安装失败"
                echo_error "请手动运行: pip install -r requirements.txt"
                exit 1
            }
            echo_info "依赖安装完成"
        else
            echo_error "未找到 requirements.txt"
            exit 1
        fi
    else
        echo_info "依赖检查通过"
    fi
}

# 启动服务
start_service() {
    echo_info "启动 Wintool (端口: $PORT)..."
    
    # 后台启动
    nohup "$PYTHON_BIN" app.py >"$LOG_FILE" 2>&1 &
    local pid=$!
    
    echo_info "等待服务启动..."
    sleep 2
    
    # 检查服务是否启动成功
    local max_retry=10
    local retry=0
    
    while [[ $retry -lt $max_retry ]]; do
        if curl -sf -o /dev/null "$URL" 2>/dev/null; then
            echo ""
            echo_title "========================================="
            echo_title "  ✓ Wintool 启动成功！"
            echo_title "========================================="
            echo_info "访问地址: $URL"
            echo_info "日志文件: $LOG_FILE"
            echo_info "进程 PID: $pid"
            echo_title "========================================="
            echo ""
            
            open_browser "$URL"
            return 0
        fi
        
        retry=$((retry + 1))
        sleep 1
    done
    
    echo_error "启动失败，请查看日志: $LOG_FILE"
    echo ""
    echo "最近的日志内容:"
    tail -20 "$LOG_FILE" 2>/dev/null || echo "无法读取日志文件"
    exit 1
}

# 主流程
main() {
    echo_title "========================================="
    echo_title "  Wintool 统一启动脚本"
    echo_title "========================================="
    echo ""
    
    stop_existing
    detect_python
    check_dependencies
    start_service
}

# 处理参数
case "${1:-}" in
    stop)
        echo_info "停止 Wintool..."
        stop_existing
        echo_info "已停止"
        exit 0
        ;;
    restart)
        echo_info "重启 Wintool..."
        stop_existing
        sleep 1
        main
        ;;
    *)
        main
        ;;
esac
