#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="5001"
URL="http://127.0.0.1:${PORT}"
LOG_FILE="/tmp/wintool.log"

cd "$PROJECT_DIR"

if lsof -iTCP:"$PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  echo "Wintool 已在运行，直接打开浏览器：${URL}"
  open "$URL"
  exit 0
fi

if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="$(command -v python3)"
fi

echo "启动 Wintool..."
nohup "$PYTHON_BIN" app.py >"$LOG_FILE" 2>&1 &
sleep 1

if lsof -iTCP:"$PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  echo "启动成功，日志：$LOG_FILE"
  open "$URL"
else
  echo "启动失败，请查看日志：$LOG_FILE"
  exit 1
fi
