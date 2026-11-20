#!/usr/bin/env python3
"""Print Tella Motion commands that place icons and logos from YOUR sheets.

Usage:
  python3 sheet_cmd.py <docDuration> <kind>:<name>:<x>:<y>:<size>:<start>[:<nodeId>] ...
    kind  icon  -> name is <icon>.<colour>, colour = dark | coral | white | green  (e.g. icon:bot.coral)
          logo  -> name from your logo sheet                                    (e.g. logo:claude)
    x, y  top-left of the box in canvas px; size = width = height; start in seconds on the doc clock
  python3 sheet_cmd.py --list icon|logo        list the names you can use

Example: python3 sheet_cmd.py 6.5 icon:bot.coral:170:680:120:0.8 logo:claude:420:680:110:1.0:l2
Paste the printed JSON array into apply_motion_editor_commands `commands`.
Each placed item pops in; change its last command for another entrance. Node ids must be unique per doc.

Reads <settings>/sheets/icons.json + logos.json and the Tella source ids from the config
(set by the /shorts:setup skill). Run /shorts:setup first if this errors.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sconfig  # noqa: E402

CFG = sconfig.load()
SHEETS = os.path.join(sconfig.HOME, "sheets")


def registry(kind):
    path = os.path.join(SHEETS, f"{kind}s.json")
    src = CFG["tella"].get(f"{kind}s_source_id")
    if not os.path.exists(path) or not src:
        sys.exit(f"No {kind} sheet set up yet. Run the /shorts:setup skill (it builds and uploads the sheet).")
    reg = json.load(open(path))
    reg["sourceId"] = src
    return reg


def commands(doc_dur, spec, n):
    parts = spec.split(":")
    kind, name = parts[0], parts[1]
    x, y, size, start = (float(v) for v in parts[2:6])
    node = parts[6] if len(parts) > 6 else f"{kind}{n}"
    reg = registry(kind)
    if name not in reg["cells"]:
        sys.exit(f"Unknown {kind} '{name}'. See: sheet_cmd.py --list {kind}")
    c = reg["cells"][name]
    k = size / reg["cell"]
    r = lambda v: round(v, 2)
    p = lambda prop, val: {"type": "setProperty", "node": node, "property": prop, "value": r(val)}
    return [
        {"type": "addMedia", "nodeId": node, "start": start, "duration": r(doc_dur - start), "sourceId": reg["sourceId"]},
        p("field:destination/x", x - c["col"] * size),
        p("field:destination/y", y - c["row"] * size),
        p("field:destination/width", reg["width"] * k),
        p("field:destination/height", reg["height"] * k),
        {"type": "setMasks", "node": node, "masks": [{"shape": "rect", "x": r(x), "y": r(y), "width": r(size), "height": r(size)}]},
        p("anchorX", x + size / 2),
        p("anchorY", y + size / 2),
        {"type": "animate", "node": node, "in": {"kind": "pop", "duration": 0.35, "easing": "springBouncy"}},
    ]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    if sys.argv[1] == "--list":
        reg = json.load(open(os.path.join(SHEETS, f"{sys.argv[2]}s.json")))
        print(" ".join(reg["order"]) + ("\ncolours: " + " ".join(reg.get("colors", [])) if reg.get("colors") else ""))
        sys.exit()
    dur = float(sys.argv[1])
    out = []
    for i, spec in enumerate(sys.argv[2:], 1):
        out += commands(dur, spec, i)
    print(json.dumps(out))
