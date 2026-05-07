#!/usr/bin/env bash
# 先停止再启动 Wintool（与 start_wintool_wsl.sh 相同启动方式）。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT="${PORT:-5001}"
URL="http://127.0.0.1:${PORT}"
LOG_FILE="/tmp/wintool.log"

"$SCRIPT_DIR/stop.sh" || true

cd "$PROJECT_DIR"

_open_url() {
  local u="$1"
  if [[ -x /mnt/c/Windows/System32/cmd.exe ]]; then
    /mnt/c/Windows/System32/cmd.exe /c start "" "$u" >/dev/null 2>&1 && return 0
  fi
  if command -v wslview >/dev/null 2>&1; then
    wslview "$u" >/dev/null 2>&1 && return 0
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$u" >/dev/null 2>&1 && return 0
  fi
  echo "请手动在浏览器打开: $u"
}

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="$(command -v python3)"
fi

echo "启动 Wintool..."
nohup "$PYTHON_BIN" app.py >"$LOG_FILE" 2>&1 &
sleep 1

if command -v lsof >/dev/null 2>&1; then
  if lsof -iTCP:"$PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "启动成功，日志：$LOG_FILE"
    _open_url "$URL"
    exit 0
  fi
else
  sleep 1
  if curl -sf -o /dev/null "$URL" 2>/dev/null; then
    echo "启动成功，日志：$LOG_FILE"
    _open_url "$URL"
    exit 0
  fi
fi

echo "启动失败，请查看日志：$LOG_FILE"
exit 1
