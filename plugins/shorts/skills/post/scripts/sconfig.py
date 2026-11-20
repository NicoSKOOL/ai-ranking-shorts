#!/usr/bin/env python3
"""Read and write the member's Shorts Machine settings.

Settings live OUTSIDE the plugin (plugin updates would wipe them):
  ~/.config/ai-ranking-shorts/config.json   (override with SHORTS_HOME)
  ~/.config/ai-ranking-shorts/sheets/       icon + logo sheets and their registries
  ~/.config/ai-ranking-shorts/style.md      the member's own edit rules

CLI:
  sconfig.py path                      print the settings folder
  sconfig.py show                      print the whole config
  sconfig.py get brand.card.accent     print one value
  sconfig.py set cta_default_link https://example.com
  sconfig.py set-json zernio.accounts '{"tiktok":"..."}'
  sconfig.py init                      write defaults if no config exists yet
"""
import json, os, sys

HOME = os.path.expanduser(os.environ.get("SHORTS_HOME", "~/.config/ai-ranking-shorts"))
PATH = os.path.join(HOME, "config.json")

DEFAULTS = {
    "version": 1,
    "brand": {
        "name": "",
        "card": {"bg": "#ECECEC", "title": "#3A3A3A", "muted": "#9C9C9C", "text": "#1F1F1F",
                 "accent": "#DE7356", "dark": "#2B2B2B", "cta": "#2FA36B", "white": "#FFFFFF"},
        "fonts": {"title": "Archivo", "body": "Inter"},
    },
    "cta_default_link": "",
    "tella": {"icons_source_id": "", "logos_source_id": ""},
    "zernio": {"profile_id": "", "accounts": {}},
    "schedule": {"platforms": ["tiktok", "instagram", "facebook"], "time_local": "12:00", "timezone": ""},
}


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load():
    if not os.path.exists(PATH):
        return json.loads(json.dumps(DEFAULTS))
    return _merge(DEFAULTS, json.load(open(PATH)))


def save(cfg):
    os.makedirs(HOME, exist_ok=True)
    json.dump(cfg, open(PATH, "w"), indent=2)


def get(cfg, dotted):
    v = cfg
    for k in dotted.split("."):
        v = v[k]
    return v


def put(cfg, dotted, value):
    keys = dotted.split(".")
    d = cfg
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "path":
        print(HOME)
    elif a[0] == "show":
        print(json.dumps(load(), indent=2))
    elif a[0] == "get":
        v = get(load(), a[1]); print(v if isinstance(v, str) else json.dumps(v))
    elif a[0] in ("set", "set-json"):
        c = load(); put(c, a[1], json.loads(a[2]) if a[0] == "set-json" else a[2]); save(c); print("ok")
    elif a[0] == "init":
        if os.path.exists(PATH):
            print("exists", PATH)
        else:
            save(load()); print("created", PATH)
    else:
        sys.exit(__doc__)
