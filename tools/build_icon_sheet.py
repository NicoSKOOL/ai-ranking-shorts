#!/usr/bin/env python3
"""MAINTAINERS ONLY. Rebuild the shipped icon sheet (plugins/shorts/skills/setup/assets/icons.png): Lucide icons (ISC licence) in 4 colours, one cell each.

Usage: python3 tools/build_icon_sheet.py <lucide icons dir>   (npm pack lucide-static, use package/icons)


Renders with headless Chrome (no cairo needed).
"""
import json, os, subprocess, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "shorts", "skills", "setup", "scripts"))
from PIL import Image

NAMES = """bot shopping-cart wallet credit-card calendar-check clock map-pin phone star shield-check lock
triangle-alert circle-check circle-x search trending-up trending-down file-text code globe store user users
message-circle sparkles eye eye-off link trophy flame hourglass timer smartphone mouse-pointer-click thumbs-up
thumbs-down ban bug zap target rocket gauge list-checks layers house building-2 wrench calendar receipt
badge-check scan-search brain bell mail heart-pulse stethoscope dog chart-column chart-line file-code-2
bot-message-square hand-coins package truck mic video repeat refresh-cw arrow-big-up arrow-big-down x check
copy siren skull megaphone lightbulb key settings filter database server""".split()
COLORS = {"dark": "#2B2B2B", "coral": "#DE7356", "white": "#FFFFFF", "green": "#2FA36B"}
CELL, DRAW, PER_ROW = 192, 150, 16

here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(here, "..", "plugins", "shorts", "skills", "setup", "assets")
src = sys.argv[1]
cells = [(n, c) for n in NAMES for c in COLORS]
cols = PER_ROW
rows = -(-len(cells) // cols)
W, H = cols * CELL, rows * CELL
pad = (CELL - DRAW) / 2
parts = []
for i, (n, c) in enumerate(cells):
    svg = open(os.path.join(src, n + ".svg")).read()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'width="24"', f'width="{DRAW}"', svg, count=1)
    svg = re.sub(r'height="24"', f'height="{DRAW}"', svg, count=1)
    svg = svg.replace('stroke="currentColor"', f'stroke="{COLORS[c]}"').replace('stroke-width="2"', 'stroke-width="2.1"')
    x, y = (i % cols) * CELL + pad, (i // cols) * CELL + pad
    parts.append(f'<div style="position:absolute;left:{x}px;top:{y}px">{svg}</div>')
html = f'<html><body style="margin:0;background:transparent;width:{W}px;height:{H}px;position:relative">{"".join(parts)}</body></html>'
hp = os.path.join(out_dir, "_sheet.html"); open(hp, "w").write(html)
png = os.path.join(out_dir, "icons.png")
subprocess.run([__import__("chrome").find() or sys.exit("no Chrome"), "--headless=new", "--disable-gpu",
                "--hide-scrollbars", "--default-background-color=00000000", f"--window-size={W},{H}",
                "--force-device-scale-factor=1", f"--screenshot={png}", "file://" + hp], check=True, capture_output=True)
im = Image.open(png).convert("RGBA")
assert im.size == (W, H), im.size
prev = Image.new("RGB", (W, H), (150, 150, 150)); prev.paste(im, (0, 0), im)
prev.resize((W // 3, H // 3)).save(os.path.join(here, "icons_preview.jpg"), quality=80)
jp = os.path.join(out_dir, "icons.json")
old = json.load(open(jp)) if os.path.exists(jp) else {}
reg = {"cell": CELL, "cols": cols, "rows": rows, "width": W, "height": H, "colors": list(COLORS), "order": NAMES,
       "cells": {f"{n}.{c}": {"col": i % cols, "row": i // cols} for i, (n, c) in enumerate(cells)}}
json.dump(reg, open(jp, "w"), indent=1)
os.remove(hp)
print(W, H, len(cells), "cells", os.path.getsize(png), "bytes")
