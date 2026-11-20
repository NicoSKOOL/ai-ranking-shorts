#!/bin/bash
# Check the local tools the Shorts Machine needs. Prints OK / MISSING with how to fix.
# (Tella and Zernio connectors are checked by the skill itself, not here.)
ok(){ printf "  OK       %s\n" "$1"; }
miss(){ printf "  MISSING  %s  ->  %s\n" "$1" "$2"; FAIL=1; }
FAIL=0
echo "Shorts Machine: local tools"
command -v ffmpeg  >/dev/null && ok "ffmpeg"  || miss "ffmpeg"  "macOS: brew install ffmpeg | Windows: winget install ffmpeg | Linux: apt install ffmpeg"
command -v ffprobe >/dev/null && ok "ffprobe" || miss "ffprobe" "comes with ffmpeg"
command -v curl    >/dev/null && ok "curl"    || miss "curl"    "install curl"
if command -v python3 >/dev/null; then ok "python3 ($(python3 -V 2>&1 | cut -d' ' -f2))"
  python3 -c "import PIL" 2>/dev/null && ok "Pillow" || miss "Pillow" "python3 -m pip install --user Pillow"
  python3 -c "import zoneinfo" 2>/dev/null && ok "zoneinfo" || miss "zoneinfo" "use Python 3.9 or newer"
else miss "python3" "install Python 3.9+ from python.org"; fi
python3 "$(dirname "$0")/chrome.py" >/dev/null 2>&1
python3 -c "import sys; sys.path.insert(0,'$(dirname "$0")'); import chrome; p=chrome.find(); print(p or '')" | grep -q . \
  && ok "Chrome/Chromium (only to build the logo sheet)" || miss "Chrome" "install Google Chrome, or set CHROME=/path/to/chrome"
if command -v zernio >/dev/null; then ok "zernio CLI"
  zernio auth:check >/dev/null 2>&1 && ok "zernio logged in" || miss "zernio login" "zernio auth:set --key <your key from zernio.com>"
else miss "zernio CLI" "npm install -g @zernio/cli  (needs Node.js)"; fi
exit $FAIL
