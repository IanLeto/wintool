#!/usr/bin/env bash
# 停止监听 PORT 的 Wintool（Flask app.py），默认端口 5001。
set -euo pipefail

PORT="${PORT:-5001}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "错误: 需要 lsof（WSL 一般自带）。请安装后再试。"
  exit 1
fi

PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -z "$PIDS" ]]; then
  echo "Wintool 未运行（端口 ${PORT} 无监听）。"
  exit 0
fi

echo "停止 Wintool（端口 ${PORT}）: ${PIDS}"
# shellcheck disable=SC2086
kill ${PIDS} 2>/dev/null || true
sleep 1
PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "$PIDS" ]]; then
  echo "强制结束: ${PIDS}"
  # shellcheck disable=SC2086
  kill -9 ${PIDS} 2>/dev/null || true
fi

if lsof -iTCP:"$PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  echo "警告: 端口 ${PORT} 仍被占用，请手动检查。"
  exit 1
fi

echo "已停止。"
