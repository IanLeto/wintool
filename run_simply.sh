#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool Legacy 版本启动脚本
# 用途：启动重构前的 Python Flask 版本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEGACY_DIR="$SCRIPT_DIR/legacy"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }

echo_title "========================================="
echo_title "  启动 Wintool Legacy 版本"
echo_title "========================================="
echo ""

# 检查 legacy 目录
if [[ ! -d "$LEGACY_DIR" ]]; then
    echo_error "未找到 legacy 目录"
    echo_error "请确保项目结构完整"
    exit 1
fi

# 检查启动脚本
if [[ ! -f "$LEGACY_DIR/run.sh" ]]; then
    echo_error "未找到 legacy/run.sh"
    exit 1
fi

# 进入 legacy 目录并启动
echo_info "切换到 legacy 目录..."
cd "$LEGACY_DIR"

echo_info "执行 legacy 启动脚本..."
bash run.sh "$@"
