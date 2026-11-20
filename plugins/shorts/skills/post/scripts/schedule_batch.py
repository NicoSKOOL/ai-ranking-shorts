#!/usr/bin/env python3
"""Schedule a batch of finished shorts: one a day, every platform, with comment automations.

Usage:
  python3 schedule_batch.py batch.json --dry-run     # print the plan, change nothing
  python3 schedule_batch.py batch.json               # upload, schedule, create automations

batch.json:
{
  "start_date": "2026-11-18",              # first post day (local date)
  "first_time": "18:30",                   # optional: time for day 1 only (e.g. later today)
  "shorts": [
    {"id": "1", "file": "/path/short1.mp4",
     "caption": "Hook line... Comment WALLET and I'll send you ...  #tag #tag",
     "keyword": "WALLET",
     "link": "https://...",                # where the commenter is sent (must be real)
     "thing": "the free checklist",        # used in the DM: "Here you go! The free checklist"
     "button": "Get the checklist"}        # DM button label, max 20 characters
  ]
}
Posting time, timezone, platforms and Zernio accounts come from the settings (/shorts:setup).

What it does per short:
  1. Re-encodes files over 18 MB (some networks cut long uploads), uploads with `zernio media:upload`.
     Zernio uploads are single use, so each short is ONE post carrying every platform.
  2. `zernio posts:create --accounts <all> --scheduledAt <UTC>`.
  3. One automation per platform, bound to the not-yet-published post (arms when it goes live):
     Instagram + Facebook: DM with a link button, then a public "Sent! Check your DMs" reply.
     TikTok / YouTube: public reply with the link (TikTok can't DM; put the link in your bio that day).
Writes <batch>.result.json with post ids and automation ids.
Needs: zernio CLI (npm i -g @zernio/cli; zernio auth:set --key ...), ffmpeg, curl.
"""
import datetime as dt, json, os, subprocess, sys, tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sconfig  # noqa: E402

API = "https://zernio.com/api/v1/comment-automations"
MAX_BYTES = 18_000_000


def api_key():
    k = os.environ.get("ZERNIO_API_KEY")
    if k:
        return k
    p = os.path.expanduser("~/.zernio/config.json")
    if os.path.exists(p):
        return json.load(open(p)).get("apiKey")
    sys.exit("No Zernio key. Run: zernio auth:set --key <your key>  (or set ZERNIO_API_KEY)")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {r.stderr[:300] or r.stdout[:300]}")
    return r.stdout


def small_enough(path, tmp):
    if os.path.getsize(path) <= MAX_BYTES:
        return path
    out = os.path.join(tmp, os.path.basename(path))
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-c:v", "libx264", "-preset", "slow", "-crf", "23",
         "-maxrate", "1300k", "-bufsize", "2600k", "-c:a", "copy", "-movflags", "+faststart", out])
    return out


def automation(cfg, key, platform, account, post_id, s):
    b = {"profileId": cfg["zernio"]["profile_id"], "accountId": account, "postId": post_id,
         "postTitle": s["caption"].split("\n")[0][:60], "name": f"Short {s['id']} {s['keyword']} ({platform})",
         "keywords": [s["keyword"].lower()], "matchMode": "contains", "repeatPolicy": {"mode": "once"}}
    if platform in ("instagram", "facebook"):
        thing = s.get("thing", "the link")
        b.update({"dmMessage": f"Here you go! {thing[0].upper() + thing[1:]} 👇",
                  "buttons": [{"type": "url", "title": s.get("button", "Get it here")[:20], "url": s["link"]}],
                  "commentReply": "Sent! Check your DMs 📩",
                  "commentReplyVariations": ["Just sent it to your DMs 🙌", "Check your inbox, it's there 📩"],
                  "publicReplyPolicy": "after_dm"})
    elif platform == "tiktok":
        b.update({"commentReply": f"Here it is: {s['link']} (it's also in my bio) 🙌",
                  "commentReplyVariations": [f"Link: {s['link']} (also in my bio) 📩"]})
    else:
        b.update({"commentReply": "The link is in the description 🙌"})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(b, f)
    out = run(["curl", "-s", "-X", "POST", API, "-H", f"Authorization: Bearer {key}",
               "-H", "Content-Type: application/json", "--data-binary", f"@{f.name}"])
    os.unlink(f.name)
    j = json.loads(out)
    if not j.get("success"):
        raise RuntimeError(f"automation failed ({platform}): {out[:300]}")
    return j["automation"]["id"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    batch_path, dry = sys.argv[1], "--dry-run" in sys.argv
    batch, cfg = json.load(open(batch_path)), sconfig.load()
    sch, accts = cfg["schedule"], cfg["zernio"]["accounts"]
    platforms = [p for p in sch["platforms"] if accts.get(p)]
    missing = [p for p in sch["platforms"] if not accts.get(p)]
    if missing:
        print("note: no Zernio account set for", ", ".join(missing), "(skipped). Run /shorts:setup to add it.")
    if not platforms or not cfg["zernio"]["profile_id"] or not sch.get("timezone"):
        sys.exit("Settings incomplete (Zernio profile/accounts or timezone). Run the /shorts:setup skill.")
    tz = ZoneInfo(sch["timezone"])
    day0 = dt.date.fromisoformat(batch["start_date"])
    hh, mm = map(int, sch["time_local"].split(":"))
    plan = []
    for i, s in enumerate(batch["shorts"]):
        t = batch.get("first_time") if i == 0 and batch.get("first_time") else None
        h, m = map(int, t.split(":")) if t else (hh, mm)
        when = dt.datetime.combine(day0 + dt.timedelta(days=i), dt.time(h, m), tz)
        utc = when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for k in ("file", "caption", "keyword", "link"):
            if not s.get(k):
                sys.exit(f"short {s.get('id', i + 1)}: missing '{k}'")
        if not os.path.exists(s["file"]):
            sys.exit(f"short {s['id']}: file not found {s['file']}")
        if "—" in s["caption"]:
            print(f"warning: short {s['id']} caption has an em dash")
        plan.append((s, when, utc))
        print(f"#{s['id']:>3}  {when:%a %b %d %H:%M %Z}  {s['keyword']:<10} -> {s['link']}")
    print("platforms:", ", ".join(platforms))
    if dry:
        print("dry run: nothing uploaded or scheduled"); return
    if dt.datetime.now(dt.timezone.utc).isoformat() > plan[0][2].replace("Z", "+00:00"):
        sys.exit("The first post time is in the past. Change start_date / first_time.")
    key = api_key()
    ids = ",".join(accts[p] for p in platforms)
    res = []
    with tempfile.TemporaryDirectory() as tmp:
        for s, when, utc in plan:
            url = json.loads(run(["zernio", "media:upload", small_enough(s["file"], tmp)]))["url"]
            post = json.loads(run(["zernio", "posts:create", "--text", s["caption"], "--accounts", ids,
                                   "--media", url, "--scheduledAt", utc]))["post"]
            autos = {p: automation(cfg, key, p, accts[p], post["_id"], s) for p in platforms}
            res.append({"id": s["id"], "post_id": post["_id"], "scheduled_utc": utc, "keyword": s["keyword"],
                        "link": s["link"], "automations": autos})
            print(f"#{s['id']} scheduled {utc} post {post['_id']} automations {len(autos)}")
    out = os.path.splitext(batch_path)[0] + ".result.json"
    json.dump(res, open(out, "w"), indent=2)
    print("saved", out)
    if "tiktok" in platforms:
        print("\nTikTok bio links (change each day):")
        for r in res:
            print(f"  {r['scheduled_utc'][:10]}  {r['link']}")


if __name__ == "__main__":
    main()
