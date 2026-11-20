#!/usr/bin/env python3
"""Concept card: many sources feed into one (AI reads directories, reviews, map pack,
then decides who to recommend). Default card style of /shorts:edit (colours from your settings), 1080x1920.

Usage: converge_card.py spec.json > cmds.json

spec = {
  "dur": 11.7, "num": "#4", "title": "GET MENTIONED\\nWHERE AI LOOKS",
  "nodeAt": 1.0, "nodeLogo": "icon:bot.white", "nodeLabel": "AI DECIDES",   # nodeLogo: icon:<name>.<colour> or logo:<name> (white icons read best on the dark node)
  "sources": [{"text": "Your website", "at": 1.6, "muted": true},
              {"text": "Directories", "at": 4.5}, ...],      # max 5, under ~14 chars
  "tag": {"text": "BE ON IT", "at": 10.5, "color": "#2FA36B"} # on every non-muted source
}
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sconfig
K = sconfig.load()["brand"]["card"]  # colours from the member's settings

s = json.load(open(sys.argv[1]))
D = s["dur"]
C = []
add = C.append
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sheet_cmd.py")


def L(start):
    return round(D - start, 2)


def rect(nid, start, x, y, w, h, color, radius=None):
    d = {"type": "addShape", "nodeId": nid, "start": round(start, 2), "duration": L(start), "shape": "rect",
         "box": {"x": x, "y": y, "width": w, "height": h}, "color": color}
    if radius:
        d["radius"] = radius
    add(d)


def text(nid, start, t, x, y, w, size, weight, color, font="inter", align="left", lh=1.1):
    add({"type": "addTitle", "nodeId": nid, "start": round(start, 2), "duration": L(start), "text": t,
         "box": {"x": x, "y": y, "width": w}, "font": font, "fontSize": size, "weight": weight,
         "color": color, "align": align, "lineHeight": lh})


def pop(nid, cx, cy, dur=0.35):
    add({"type": "setProperty", "node": nid, "property": "anchorX", "value": cx})
    add({"type": "setProperty", "node": nid, "property": "anchorY", "value": cy})
    add({"type": "animate", "node": nid, "in": {"kind": "pop", "duration": dur, "easing": "springBouncy"}})


add({"type": "canvas.set", "canvas": {"duration": {"seconds": D}}})
rect("bg", 0, 0, 0, 1080, 1920, K["bg"])
if s.get("num"):
    text("num", 0, s["num"], 40, 190, 1000, 170, 900, K["muted"], font="archivo", lh=1)
    add({"type": "animate", "node": "num", "in": {"kind": "slideDown", "duration": 0.4}})
text("title", 0.1, s["title"], 40, 375, 1000, 96, 900, K["title"], font="archivo", lh=1.05)
add({"type": "setTextAnimation", "node": "title", "phase": "in", "preset": "blur", "unit": "word",
     "duration": 0.35, "stagger": 0.07})

src = s["sources"][:5]
cx0, cw, ch, gap, y0 = 80, 500, 84, 112, 650
nx, nw, nh = 690, 310, 230
ys = [y0 + gap * i for i in range(len(src))]
ny = (ys[0] + ys[-1] + ch) / 2 - nh / 2
ncy = ny + nh / 2

# the one: AI node
na = s.get("nodeAt", 1.0)
rect("node", na, nx, ny, nw, nh, K["dark"], 34)
pop("node", nx + nw / 2, ncy, 0.4)
if s.get("nodeLogo"):
    out = subprocess.check_output([sys.executable, LOGO, str(D),
                                   f"{s['nodeLogo'] if ':' in s['nodeLogo'] else 'logo:' + s['nodeLogo']}:{nx + nw / 2 - 48}:{ny + 40}:96:{na + 0.15}:nodelogo"])
    C.extend(json.loads(out))
text("nodelabel", na + 0.2, s.get("nodeLabel", "AI DECIDES"), nx, ny + 160, nw, 26, 800, K["white"], align="center")

tag = s.get("tag")
k = 0
for i, (b, y) in enumerate(zip(src, ys)):
    at = b["at"]
    muted = b.get("muted")
    rect(f"src{i+1}", at, cx0, y, cw, ch, "#DCDCDC" if muted else K["white"], 22)
    pop(f"src{i+1}", cx0 + cw / 2, y + ch / 2)
    text(f"srctext{i+1}", at + 0.05, b["text"], cx0 + 30, y + 24, 300, 34, 600, "#6A6A6A" if muted else K["text"])
    add({"type": "setTextAnimation", "node": f"srctext{i+1}", "phase": "in", "preset": "rise",
         "unit": "word", "duration": 0.3, "stagger": 0.04})
    la = at + 0.2
    add({"type": "addPath", "nodeId": f"line{i+1}", "start": round(la, 2), "duration": L(la),
         "path": f"M {cx0 + cw} {y + ch / 2} L {nx} {ncy}", "color": K["accent"] if not muted else "#B5B5B5",
         "paint": "stroke", "strokeWidth": 5, "cap": "round"})
    add({"type": "setKeyframes", "node": f"line{i+1}", "property": "opacity",
         "keys": [{"at": la, "value": 0}, {"at": la + 0.25, "value": 1}]})
    if tag and not muted:
        ta = tag["at"] + 0.12 * k
        k += 1
        pw = 17 * len(tag["text"]) + 48
        px = cx0 + cw - 16 - pw
        rect(f"tag{i+1}", ta, px, y + 15, pw, 54, tag.get("color", K["cta"]), 27)
        pop(f"tag{i+1}", px + pw / 2, y + 42, 0.3)
        text(f"tagtext{i+1}", ta, tag["text"], px, y + 27, pw, 24, 800, K["white"], align="center", lh=1.2)
        pop(f"tagtext{i+1}", px + pw / 2, y + 42, 0.3)

json.dump(C, sys.stdout)
