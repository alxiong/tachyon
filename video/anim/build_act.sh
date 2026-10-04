#!/usr/bin/env bash
# Mux every scene of act N with its audio and concat into demo/actN.mp4.
#   ./build_act.sh 3
set -euo pipefail
cd "$(dirname "$0")"
N=$1; FF=../bin/ffmpeg
TMP=$(mktemp -d)
: > "$TMP/list.txt"
for sc in $(grep -oE "^class Scene${N}[0-9]+" act$N.py | sed 's/class //'); do
  sid="${sc:5:1}.${sc:6}"
  r=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "renders/$sc.mp4")
  [ "$r" = 1080 ] || { echo "renders/$sc.mp4 is ${r}p, render without 'fast' first"; exit 1; }
  $FF -loglevel error -y -i "renders/$sc.mp4" -i "../audio/final/scene-$sid.mp3" \
      -c:v copy -c:a aac -b:a 160k "$TMP/$sc.mp4"
  echo "file '$TMP/$sc.mp4'" >> "$TMP/list.txt"
done
$FF -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c copy "../demo/act$N.mp4"
rm -rf "$TMP"
echo "built demo/act$N.mp4 ($(ffprobe -v quiet -show_entries format=duration -of csv=p=0 ../demo/act$N.mp4)s)"
