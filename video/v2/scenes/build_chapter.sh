#!/usr/bin/env bash
# Kept for muscle memory: see build_chapter.py (scene cuts dip through black unless chained).
exec "$(dirname "$0")/../.venv/bin/python" "$(dirname "$0")/build_chapter.py" "$@"
