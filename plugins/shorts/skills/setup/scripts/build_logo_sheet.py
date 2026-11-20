#!/usr/bin/env python3
"""Build YOUR logo sprite sheet for Tella cards, on your machine.

Brand logos are not shipped with the plugin. This script downloads them
(Simple Icons, CC0 icon data, or the site's own favicon), adds anything you put
in <settings>/logo_masters/, and writes one sheet:

  <settings>/sheets/logos.png, logos_preview.jpg, logos.json

Then upload logos.png to Tella once (the setup skill does it) and store its
sourceId with:  sconfig.py set tella.logos_source_id su_...
Logos remain trademarks of their owners: use them to refer to the tools you name.

Usage: python3 build_logo_sheet.py [--only name1,name2]
Needs: Python 3 + Pillow, Chrome/Chromium (for SVG), internet.
"""
import io, json, os, subprocess, sys, tempfile, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chrome, sconfig  # noqa: E402

CELL, COLS, PAD = 300, 6, 26
OUT = os.path.join(sconfig.HOME, "sheets")
MASTERS = os.path.join(sconfig.HOME, "logo_masters")


def fetch(url):
    r = subprocess.run(["curl", "-sfL", "--max-time", "20", "-A", "Mozilla/5.0", url], capture_output=True)
    return r.stdout if r.returncode == 0 and r.stdout else None


def render_svgs(svgs):
    """svgs: list of svg strings -> list of RGBA images (one Chrome run)."""
    exe = chrome.find()
    if not exe:
        sys.exit("No Chrome/Chromium found. Install Google Chrome or set CHROME=/path/to/chrome.")
    size = CELL - 2 * PAD
    W, H = len(svgs) * CELL, CELL
    parts = []
    for i, s in enumerate(svgs):
        s = s.replace("<svg", f'<svg width="{size}" height="{size}"', 1) if "width=" not in s.split(">")[0] else s
        parts.append(f'<div style="position:absolute;left:{i*CELL+PAD}px;top:{PAD}px;width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center">'
                     f'<div style="width:{size}px;height:{size}px">{s}</div></div>')
    css = f"svg{{width:{size}px!important;height:{size}px!important}}"
    html = f'<html><head><style>{css}</style></head><body style="margin:0;background:transparent;width:{W}px;height:{H}px;position:relative">{"".join(parts)}</body></html>'
    with tempfile.TemporaryDirectory() as d:
        hp, pp = os.path.join(d, "s.html"), os.path.join(d, "s.png")
        open(hp, "w").write(html)
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                        f"--window-size={W},{H}", "--force-device-scale-factor=1", f"--screenshot={pp}", "file://" + hp],
                       capture_output=True, timeout=120)
        strip = Image.open(pp).convert("RGBA")
        strip.load()
    return [strip.crop((i * CELL, 0, (i + 1) * CELL, CELL)) for i in range(len(svgs))]


def fit(im):
    bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if not bbox:
        return None
    im = im.crop(bbox)
    inner = CELL - 2 * PAD
    k = inner / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    c = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    c.alpha_composite(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
    return c


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    spec = json.load(open(os.path.join(HERE, "..", "assets", "logos_default.json")))["logos"]
    if os.path.isdir(MASTERS):
        known = {s["name"] for s in spec}
        for f in sorted(os.listdir(MASTERS)):
            n, ext = os.path.splitext(f)
            if ext.lower() in (".png", ".jpg", ".jpeg", ".svg", ".webp") and n not in known:
                spec.append({"name": n, "file": os.path.join(MASTERS, f)})
    if only:
        spec = [s for s in spec if s["name"] in only]
    images, svg_jobs, skipped = {}, [], []
    for s in spec:
        name = s["name"]
        local = os.path.join(MASTERS, f"{name}.svg") if os.path.exists(os.path.join(MASTERS, f"{name}.svg")) else None
        if "file" in s or local or any(os.path.exists(os.path.join(MASTERS, name + e)) for e in (".png", ".jpg", ".webp")):
            p = s.get("file") or local or next(os.path.join(MASTERS, name + e) for e in (".png", ".jpg", ".webp") if os.path.exists(os.path.join(MASTERS, name + e)))
            if p.endswith(".svg"):
                svg_jobs.append((name, open(p).read()))
            else:
                images[name] = Image.open(p).convert("RGBA")
            continue
        if s.get("si"):
            data = fetch(f"https://cdn.simpleicons.org/{s['si']}")
            if data and b"<svg" in data:
                svg_jobs.append((name, data.decode()))
                continue
        dom = s.get("domain")
        if dom:
            data = fetch("https://www.google.com/s2/favicons?sz=256&domain=" + urllib.parse.quote(dom))
            if data:
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                if min(im.size) >= 64:
                    images[name] = im
                    continue
        skipped.append(name)
    if svg_jobs:
        for (name, _), im in zip(svg_jobs, render_svgs([j[1] for j in svg_jobs])):
            images[name] = im
    order = [s["name"] for s in spec if s["name"] in images]
    cells = {}
    rows = -(-len(order) // COLS)
    sheet = Image.new("RGBA", (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, name in enumerate(order):
        c = fit(images[name])
        if c is None:
            skipped.append(name); continue
        sheet.alpha_composite(c, ((i % COLS) * CELL, (i // COLS) * CELL))
        cells[name] = {"col": i % COLS, "row": i // COLS}
    os.makedirs(OUT, exist_ok=True)
    sheet.save(os.path.join(OUT, "logos.png"), optimize=True)
    prev = Image.new("RGBA", sheet.size, (236, 236, 236, 255)); prev.alpha_composite(sheet)
    prev.convert("RGB").resize((sheet.width // 2, sheet.height // 2)).save(os.path.join(OUT, "logos_preview.jpg"), quality=85)
    json.dump({"cell": CELL, "cols": COLS, "rows": rows, "width": sheet.width, "height": sheet.height, "order": order, "cells": cells},
              open(os.path.join(OUT, "logos.json"), "w"), indent=1)
    print(f"{len(cells)} logos -> {OUT}/logos.png ({sheet.width}x{sheet.height})")
    if skipped:
        print("skipped (no source found, add a file to logo_masters/):", ", ".join(skipped))
    print("next: upload logos.png to Tella (create_source kind image, width/height above), then sconfig.py set tella.logos_source_id <id>")


if __name__ == "__main__":
    main()
