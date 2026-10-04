#!/usr/bin/env bash
# Render one scene + 4x5 contact sheet + lint print.
#   ./qa.sh ch0.py Scene01 [fast]      QA_TIMES="12 40" ./qa.sh ...  (extra full frames)
set -euo pipefail
cd "$(dirname "$0")"
FILE=$1; SCENE=$2; MODE=${3:-}
FF=/home/alex/work/tachyon_wt1/video/bin/ffmpeg
# 1) every anchor phrase must resolve against the current words.json
CHK=$(../.venv/bin/python check_anchors.py "$FILE" || true)
if grep -q MISSING <<<"$CHK"; then grep MISSING <<<"$CHK"; echo "ANCHOR CHECK FAILED"; exit 1; fi
FLAGS="-w"
[ "$MODE" = fast ] && FLAGS="-w -r 854x480"
rm -f ../renders/$SCENE.mp4
LOG=$(mktemp)
../.venv/bin/manimgl "$FILE" "$SCENE" $FLAGS >"$LOG" 2>&1 || true
[ -f ../renders/$SCENE.mp4 ] || { tr "\r" "\n" <"$LOG" | grep -v -i warn | tail -25; echo "RENDER FAILED"; exit 1; }
VID=../renders/$SCENE.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VID")
OUT=qa/$SCENE; mkdir -p "$OUT"
# 20 evenly spaced frames -> 4x5 sheet
FPS=$(python3 -c "print(20/float('$D'))")
$FF -y -loglevel error -i "$VID" -vf "fps=$FPS,scale=480:-1,tile=4x5" -frames:v 1 "$OUT/sheet.png"
for t in ${QA_TIMES:-}; do $FF -y -loglevel error -ss "$t" -i "$VID" -frames:v 1 "$OUT/t$t.png"; done
echo "duration $D  sheet $OUT/sheet.png"
echo "--- lint ---"; cat lint/$SCENE.txt 2>/dev/null || echo "(none)"
