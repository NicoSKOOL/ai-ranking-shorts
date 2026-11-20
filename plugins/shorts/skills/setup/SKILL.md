---
name: setup
description: Use once before the first batch of shorts, or when someone says "set up the shorts machine", "shorts setup", "connect Tella and Zernio for shorts", or a /shorts skill reports that settings, sheets or accounts are missing. Checks local tools, connects Tella and Zernio, saves brand colours, links and posting time, and uploads the icon and logo sheets to the member's own Tella.
---

# Shorts Machine: setup

Run this once. Everything it saves lives in the member's settings folder, outside the plugin, so plugin updates never wipe it:

```
~/.config/ai-ranking-shorts/
  config.json        brand colours, default link, Tella sheet ids, Zernio accounts, schedule
  style.md           the member's own edit rules (grows as they give feedback)
  sheets/            icons.png + icons.json, logos.png + logos.json
  logo_masters/      optional: their own logo files (<name>.png or .svg)
```

`scripts/sconfig.py` reads and writes it (`path`, `show`, `get a.b`, `set a.b value`, `set-json a.b '{...}'`, `init`).

Ask the questions in plain language, a few at a time. Offer the default in brackets so they can just say yes.

## 1. Local tools

```bash
bash <skill dir>/scripts/doctor.sh
```
Fix anything MISSING with the printed command before going on (ask before installing anything).

## 2. Connectors

- **Tella**: call a light Tella tool (`list_videos`). If Tella tools are not available, tell the member to connect Tella's MCP server in Claude (Tella's help docs give the address), then restart this skill. Editing and exports in Tella need a paid Tella plan; check the current plan names on tella.tv/pricing rather than quoting one.
- **Zernio**: the CLI from step 1 must be logged in. If the Zernio connector is also available, use `profiles_list` and `accounts_list` from it; otherwise `zernio accounts:list`.

## 3. Settings

`python3 <skill dir>/scripts/sconfig.py init`, then ask and `set` each:

1. **Brand name** (`brand.name`).
2. **Card colours** (`brand.card.*`). Default is the tested look: light grey cards, dark titles, coral highlight, green comment pill. If they have brand colours, map them: `bg` (card background, keep it light), `title`, `accent` (highlights, problems), `cta` (comment pill, "do this" tags), `dark` (tiles and dark cards). Check text stays readable on `bg`.
3. **Default link** (`cta_default_link`): where a comment keyword sends people when a short has no specific link (their community, booking page, newsletter). It must be a real page they own.
4. **Platforms** (`schedule.platforms`, default tiktok, instagram, facebook; youtube optional).
5. **Timezone** (`schedule.timezone`, an IANA name like `America/New_York`) and **posting time** (`schedule.time_local`, default 12:00). If Zernio has posting history, `analytics_get_best_time_to_post` gives their best hour in UTC: convert it.
6. **Zernio** (`zernio.profile_id`, `zernio.accounts` as `{"tiktok": "...", "instagram": "...", ...}`). Pick from the account list; never guess an id. Instagram must be a Business or Creator account for DMs.

## 4. Icon sheet (ships with the plugin)

82 Lucide line icons in dark, coral, white and green. Copy and upload once:
```bash
H=$(python3 <skill dir>/scripts/sconfig.py path); mkdir -p "$H/sheets"
cp <skill dir>/assets/icons.png <skill dir>/assets/icons.json "$H/sheets/"
```
Then `create_source` (kind `image`, width and height from icons.json), `curl -X PUT -T "$H/sheets/icons.png" "<uploadUrl>"` (expect 200), and `sconfig.py set tella.icons_source_id <sourceId>`.

## 5. Logo sheet (built on their machine)

Brand logos are not shipped. Build them locally from public sources:
```bash
python3 <skill dir>/scripts/build_logo_sheet.py
```
Show them `sheets/logos_preview.jpg`. Ask which tools they talk about that are missing, have them drop a file into `logo_masters/` (or fetch a logo from the brand's own site with their OK), rerun, then upload like step 4 and `sconfig.py set tella.logos_source_id <sourceId>`. Rebuilding later means a new upload and a new id; videos already made keep the old sheet.

## 6. Style file

If `style.md` does not exist, copy `<skill dir>/assets/style_template.md` there and fill in the brand name. Every rule the member gives later ("never use that colour", "captions smaller") goes into this file, not into the plugin.

## 7. Finish

Print `sconfig.py show` (it holds no secrets) and tell them: next is `/shorts:script` to write the first batch.
