#!/usr/bin/env bash
# Fast timing + layout sweep of every scene (skip mode: no video, exact scene time).
#   ./lint_all.sh [act numbers...]   e.g. ./lint_all.sh 3 6
cd "$(dirname "$0")"
ACTS=${*:-0 1 2 3 4 5 6 7 8}
for n in $ACTS; do
  for sc in $(grep -oE "^class Scene${n}[0-9]+" act$n.py | sed 's/class //'); do
    ../.venv/bin/manimgl act$n.py $sc -s -w > /dev/null 2>&1 || echo "$sc FAILED"
    rm -f renders/$sc.png
    printf "%-8s %3d findings\n" $sc $(wc -l < lint/$sc.txt)
  done
done
