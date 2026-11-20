#!/usr/bin/env python3
"""Concept card: one thing splits into many (fan-out queries, one keyword -> many pages,
one task -> many agents). Default card style of /shorts:edit (colours from your settings), 1080x1920.

Usage: tree_card.py spec.json > cmds.json

spec = {
  "dur": 12.3,                      # card length in seconds (= layout duration)
  "num": "#3",                      # optional big grey number
  "title": "WRITE FOR\\nFAN-OUT QUERIES",
  "rootLabel": "YOU ASK",           # small label over the root bubble
  "root": "Who can clean up my mom's full house?",
  "rootAt": 0.6,                    # seconds on the card's clock
  "branchLabel": "AI SILENTLY ASKS ITSELF",
  "branchAt": 2.9,                  # trunk starts growing here
  "branches": [{"text": "How much will it cost?", "at": 3.3}, ...],   # max 4, keep under ~28 chars
  "tag": {"text": "ANSWER", "at": 10.5, "color": "#2FA36B"}         # optional pill on every branch
}
Every word comes from what the speaker says (or their own example): tell them which ones are paraphrased.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sconfig
K = sconfig.load()["brand"]["card"]  # colours from the member's settings

s = json.load(open(sys.argv[1]))
D = s["dur"]
C = []
add = C.append


def node_len(start):
    return round(D - start, 2)


def rect(nid, start, x, y, w, h, color, radius=None):
    d = {"type": "addShape", "nodeId": nid, "start": start, "duration": node_len(start), "shape": "rect",
         "box": {"x": x, "y": y, "width": w, "height": h}, "color": color}
    if radius:
        d["radius"] = radius
    add(d)


def text(nid, start, t, x, y, w, size, weight, color, font="inter", align="left", lh=1.1):
    add({"type": "addTitle", "nodeId": nid, "start": start, "duration": node_len(start), "text": t,
         "box": {"x": x, "y": y, "width": w}, "font": font, "fontSize": size, "weight": weight,
         "color": color, "align": align, "lineHeight": lh})


def pop(nid, cx, cy, dur=0.35, easing="springBouncy"):
    add({"type": "setProperty", "node": nid, "property": "anchorX", "value": cx})
    add({"type": "setProperty", "node": nid, "property": "anchorY", "value": cy})
    add({"type": "animate", "node": nid, "in": {"kind": "pop", "duration": dur, "easing": easing}})


add({"type": "canvas.set", "canvas": {"duration": {"seconds": D}}})
rect("bg", 0, 0, 0, 1080, 1920, K["bg"])
if s.get("num"):
    text("num", 0, s["num"], 40, 190, 1000, 170, 900, K["muted"], font="archivo", lh=1)
    add({"type": "animate", "node": "num", "in": {"kind": "slideLeft", "duration": 0.4}})
text("title", 0.1, s["title"], 40, 375, 1000, 96, 900, K["title"], font="archivo", lh=1.05)
add({"type": "setTextAnimation", "node": "title", "phase": "in", "preset": "rise", "unit": "word",
     "duration": 0.35, "stagger": 0.07})

# root bubble
ra = s.get("rootAt", 0.6)
text("rootlabel", ra, s.get("rootLabel", "YOU ASK"), 140, 618, 800, 24, 800, K["muted"])
rect("root", ra, 140, 652, 800, 112, K["dark"], 30)
pop("root", 540, 708)
text("roottext", ra + 0.1, s["root"], 170, 688, 740, 34, 700, K["white"], align="center")
add({"type": "setTextAnimation", "node": "roottext", "phase": "in", "preset": "typewriter",
     "unit": "character", "duration": 0.05, "stagger": 0.018})

# trunk + branches
br = s["branches"][:4]
ba = s.get("branchAt", br[0]["at"] - 0.4)
y0, gap, ch = 845, 120, 92
last_mid = y0 + gap * (len(br) - 1) + ch // 2
rect("trunk", ba, 198, 764, 6, last_mid - 764 + 3, K["accent"], 3)
add({"type": "setKeyframes", "node": "trunk", "property": "field:geometry/rect/rect/height",
     "keys": [{"at": ba, "value": 4, "easing": "easeOutCubic"}, {"at": br[-1]["at"], "value": last_mid - 764 + 3}]})
text("branchlabel", ba, s.get("branchLabel", "AI ASKS ITSELF"), 230, 790, 700, 24, 800, K["accent"])
add({"type": "setTextAnimation", "node": "branchlabel", "phase": "in", "preset": "typewriter",
     "unit": "character", "duration": 0.05, "stagger": 0.02})
tag = s.get("tag")
for i, b in enumerate(br):
    y = y0 + gap * i
    at = b["at"]
    rect(f"tick{i+1}", at, 198, y + ch // 2 - 3, 46, 6, K["accent"], 3)
    add({"type": "setKeyframes", "node": f"tick{i+1}", "property": "field:geometry/rect/rect/width",
         "keys": [{"at": at, "value": 4, "easing": "easeOutCubic"}, {"at": at + 0.2, "value": 46}]})
    rect(f"chipshadow{i+1}", at + 0.1, 244, y + 8, 696, ch, "#0000001A", 24)
    rect(f"chip{i+1}", at + 0.1, 244, y, 696, ch, K["white"], 22)
    pop(f"chipshadow{i+1}", 592, y + ch / 2)
    pop(f"chip{i+1}", 592, y + ch / 2)
    text(f"chiptext{i+1}", at + 0.15, b["text"], 276, y + 27, 500, 34, 600, K["text"])
    add({"type": "setTextAnimation", "node": f"chiptext{i+1}", "phase": "in", "preset": "rise",
         "unit": "word", "duration": 0.3, "stagger": 0.04})
    if tag:
        ta = tag["at"] + 0.15 * i
        pw = 17 * len(tag["text"]) + 48
        rect(f"tag{i+1}", ta, 920 - pw, y + 19, pw, 54, tag.get("color", K["cta"]), 27)
        pop(f"tag{i+1}", 920 - pw / 2, y + 46, 0.3)
        text(f"tagtext{i+1}", ta, tag["text"], 920 - pw, y + 31, pw, 24, 800, K["white"], align="center", lh=1.2)
        pop(f"tagtext{i+1}", 920 - pw / 2, y + 46, 0.3)

json.dump(C, sys.stdout)
