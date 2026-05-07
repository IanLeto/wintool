#!/bin/bash
set -euo pipefail

PORT="5001"

PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN || true)"
if [ -z "$PIDS" ]; then
  echo "Wintool 未运行。"
  exit 0
fi

echo "停止 Wintool 进程: $PIDS"
kill $PIDS
echo "已停止。"
