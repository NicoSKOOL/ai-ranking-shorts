#!/bin/bash
# Download a Tella raw source (HLS), optionally rotate it, and split it into
# upload-sized pieces at the given boundaries.
#
# Usage: bash prep_footage.sh "<m3u8 url from list_sources>" <workdir> <rotate> <cut1> <cut2> ...
#   rotate: ccw (head points right in the raw frame), cw (head points left), none
#   cuts:   boundaries in seconds of the raw recording, in the pauses between sections.
#           Pieces are [0,cut1] [cut1,cut2] ... [cutN,end]. Keep each piece under ~22 s.
# Output: <workdir>/p1.mp4 ... pN.mp4 (1080x1920 when rotated, 30 fps, <= ~5.5 Mbps)
set -euo pipefail
URL="$1"; WORK="$2"; ROT="$3"; shift 3
mkdir -p "$WORK"; cd "$WORK"
BASE="${URL%%\?*}"; BASE="${BASE%/*}"; Q="${URL#*\?}"

curl -sf "$URL" -o master.m3u8
VPL=$(grep -v '^#' master.m3u8 | head -1)
APL=$(grep -o 'URI="[^"]*"' master.m3u8 | head -1 | sed 's/URI="//;s/"//')

fetch() { # playlist name, output file
  curl -sf "$BASE/$1?$Q" -o "$2.m3u8"
  : > "$2.mp4"
  { grep -o 'URI="[^"]*"' "$2.m3u8" | head -1 | sed 's/URI="//;s/"//'; grep -v '^#' "$2.m3u8"; } |
  while IFS= read -r seg; do curl -sf "$BASE/$seg?$Q" >> "$2.mp4"; done
}
fetch "$VPL" video
if [ -n "$APL" ]; then fetch "$APL" audio; fi

case "$ROT" in
  ccw) VF="transpose=2";; cw) VF="transpose=1";; *) VF="null";;
esac
if [ -n "$APL" ]; then IN=(-i video.mp4 -i audio.mp4 -map 0:v -map 1:a); else IN=(-i video.mp4); fi
ffmpeg -v error -y "${IN[@]}" -vf "$VF" -r 30 -c:v libx264 -crf 18 -preset fast \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart upright.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 upright.mp4)

STARTS=(0 "$@"); ENDS=("$@" "$DUR")
for i in "${!STARTS[@]}"; do
  n=$((i+1))
  ffmpeg -v error -y -ss "${STARTS[$i]}" -to "${ENDS[$i]}" -i upright.mp4 -c:v libx264 -crf 20 \
    -maxrate 5500k -bufsize 11000k -preset slow -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k \
    -movflags +faststart "p$n.mp4"
  echo "p$n $(wc -c < "p$n.mp4" | tr -d " ") bytes $(ffprobe -v error -show_entries format=duration -of csv=p=0 "p$n.mp4") s"
done
ffmpeg -v error -y -ss 5 -i upright.mp4 -frames:v 1 -vf scale=270:-1 check.jpg
echo "check orientation: $WORK/check.jpg"
