#!/bin/bash
# Upload p1.mp4..pN.mp4 to Tella upload URLs, one after another.
# Usage: bash put_pieces.sh <workdir>
#   <workdir>/urls.txt holds one uploadUrl per line (from create_source), in piece order.
# Some networks cut long uploads; if an upload fails, cut smaller pieces (under ~18 MB each).
set -uo pipefail
cd "$1"
i=0
while IFS= read -r u; do
  [ -z "$u" ] && continue
  i=$((i+1))
  curl -s -o "put$i.out" -w "p$i %{http_code} up=%{size_upload} t=%{time_total}\n" \
    -X PUT -H "Expect:" --upload-file "p$i.mp4" "$u"
done < urls.txt
