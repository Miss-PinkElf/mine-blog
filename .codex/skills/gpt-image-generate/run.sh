#!/usr/bin/env bash
# 兼容旧入口：转调 Python 主实现；无 Python 时尝试 Node
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$DIR/run.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$DIR/run.py" "$@"
elif command -v node >/dev/null 2>&1; then
  exec node "$DIR/run.mjs" "$@"
else
  echo "错误: 需要 Python 3 或 Node.js（run.sh 已降级为薄封装）" >&2
  exit 127
fi
