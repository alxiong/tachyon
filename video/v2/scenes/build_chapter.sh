#!/usr/bin/env bash
# Mux each scene of chapter N with its final audio, concat -> v2/video/chN.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
N=$1; FF=/home/alex/work/tachyon_wt1/video/bin/ffmpeg
TMP=$(mktemp -d); LIST=$TMP/list.txt
for a in $(ls audio/final/scene-$N.*.mp3 | sort -V); do
  sid=$(basename "$a" .mp3 | sed 's/scene-//'); S="Scene${sid/./}"
  V=renders/$S.mp4
  h=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$V")
  [ "$h" = 1080 ] || { echo "refusing: $V is ${h}p"; exit 1; }
  $FF -y -loglevel error -i "$V" -i "$a" -c:v copy -c:a aac -b:a 160k "$TMP/$S.mp4"
  echo "file '$TMP/$S.mp4'" >> "$LIST"
done
mkdir -p video
$FF -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "video/ch$N.mp4"
echo "video/ch$N.mp4 $(ffprobe -v error -show_entries format=duration -of csv=p=0 video/ch$N.mp4)s"
