# The Shorts Machine

**Record once. Post every day.** Claude Code skills that turn one recording session into two weeks of short-form videos, edited inside [Tella](https://refer.tella.com/nicolas-gorrono) and scheduled with comment-to-DM automations through [Zernio](https://zernio.link/nicolas-gorrono).

<!-- TODO before publishing: media/round1-vs-round2.gif (same short, first edit vs final) -->

## What it does

0. **`/shorts:ideas`** (optional) researches your website: it pulls the People Also Ask questions for your services and industry from DataWise, ranks them by search volume, and writes 14 scripts that answer what people actually search. Needs the DataWise connector.
1. **`/shorts:script`** writes a batch of shorts. Every short gets a word-for-word script, a comment keyword and a real link it sends people to. Facts to verify are marked.
2. **You record** them in one sitting in Tella.
3. **`/shorts:edit`** edits each short inside Tella: cuts retakes and silences, builds its own animated visual idea (icons, real tool logos, mock screens, counters, sound effects), adds captions and the comment pill. Everything stays editable in Tella. You review every edit.
4. **`/shorts:post`** exports, writes the captions, schedules one short a day to TikTok, Instagram and Facebook (YouTube optional) and sets up the comment automations:
   - Instagram and Facebook: commenting the keyword sends a DM with a button to your link.
   - TikTok: a reply with the link (TikTok can't DM), and you put that day's link in your bio.

When an edit isn't right, say what's wrong. The fix goes into your own `style.md`, so every later short gets it.

## Install

```
/plugin marketplace add NicoSKOOL/ai-ranking-shorts
/plugin install shorts@ai-ranking-shorts
```
Then run `/shorts:setup` once.

## What you need

- **Claude Code** (terminal or desktop app).
- **[Tella](https://refer.tella.com/nicolas-gorrono)** with its MCP connector. Exports need a paid plan: Pro is enough ($29/month, or $16/month billed yearly; 7-day free trial, no card).
- **[Zernio](https://zernio.link/nicolas-gorrono)** for scheduling and automations, with its CLI (`npm install -g @zernio/cli`). First 2 accounts free, then $6/month each.
- **ffmpeg**, **Python 3.9+** with Pillow, **curl**, and **Chrome** (only to build your logo sheet).
- macOS or Linux. Windows users: run Claude Code in WSL.

`/shorts:setup` checks all of these and tells you how to fix anything missing.

**Usage heads-up:** editing is the heavy part. In testing, one short used about 250,000 to 300,000 Claude tokens. On smaller plans, edit 2 or 3 shorts per session.

## Where your settings live

Nothing personal goes into the plugin. Your settings stay on your machine, so plugin updates never touch them:

```
~/.config/ai-ranking-shorts/
  config.json     brand colours, default link, Tella sheet ids, Zernio accounts, posting time
  style.md        your edit rules
  sheets/         your icon and logo sheets
  logo_masters/   your own logo files (optional)
```

## What's inside

```
plugins/shorts/skills/
  setup/    one-time setup, icon sheet (Lucide), logo sheet builder
  script/   ideas to scripts with keyword + link
  edit/     the Tella edit, card scripts, reference/ (cards, gotchas, signature ideas)
  post/     export, captions, schedule_batch.py (Zernio + automations)
tools/      maintainer scripts
```

## Honest limits

- You still record, review every edit and update your TikTok bio link.
- Claude checks the edit frame by frame but does not listen to the audio. Watch each short before approving.
- Tella and Zernio change their tools; if a step fails, tell Claude what happened and it will adapt.

## Licence

MIT. Icons from Lucide (ISC). No brand logos are shipped: see THIRD_PARTY_NOTICES.md.

Made by [AI Ranking](https://www.airankingskool.com).
