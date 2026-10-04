#!/usr/bin/env bash
# Render one scene and produce QA artifacts.
#   ./qa.sh act3.py Scene31 [fast]
# fast = 480p preview (DON'T ship it; re-render without 'fast' before build_act.sh).
# Outputs: renders/<Scene>.mp4, qa/<Scene>/sheet.png (4x5 contact sheet),
#          qa/<Scene>/t<sec>.png for any extra times in $QA_TIMES, lint/<Scene>.txt
set -euo pipefail
cd "$(dirname "$0")"
FILE=$1; SC=$2; MODE=${3:-full}
FF=../bin/ffmpeg
Q=""; [ "$MODE" = fast ] && Q="-l"
../.venv/bin/manimgl "$FILE" "$SC" -w $Q > "qa_$SC.log" 2>&1 || { tail -30 "qa_$SC.log"; exit 1; }
rm -f "qa_$SC.log"
mkdir -p "qa/$SC"
D=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "renders/$SC.mp4")
IV=$(python3 -c "print($D/20)")
$FF -loglevel error -y -i "renders/$SC.mp4" -vf "fps=1/$IV,scale=640:-1,tile=4x5" -frames:v 1 "qa/$SC/sheet.png"
for t in ${QA_TIMES:-}; do
  $FF -loglevel error -y -ss "$t" -i "renders/$SC.mp4" -frames:v 1 "qa/$SC/t$t.png"
done
echo "duration ${D}s  sheet: anim/qa/$SC/sheet.png  (frame k at k*${IV}s)"
echo "--- lint/$SC.txt ($(wc -l < lint/$SC.txt) findings) ---"; cat "lint/$SC.txt"
