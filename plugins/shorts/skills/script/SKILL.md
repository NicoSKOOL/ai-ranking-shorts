---
name: script
description: Use when someone wants ideas or scripts for short-form videos (TikTok, Reels, Shorts), says "write my shorts", "what shorts should I record", "turn this video/post/report into shorts", or starts a new Shorts Machine batch. Produces a batch of word-for-word scripts, each with a comment keyword, a real destination link and facts to check, ready to record in Tella.
---

# Shorts Machine: scripts

Output: a batch of shorts where every one has **a script, a keyword and a destination**. No destination, no short.

Read `~/.config/ai-ranking-shorts/config.json` first (`cta_default_link`, brand). If it does not exist, run `/shorts:setup` first.

## 1. Ask (once, short)

- What the business does and who it's for.
- How many shorts this batch (default 10 to 15: one recording session).
- **Destinations**: the real links they can send people to (free checklist, tool, report, booking page, community, a product). Write them down with a short name each. Anything without a link only goes to `cta_default_link`.
- Anything to repurpose: a long video, a blog post, a report, a case study. Read it.

## 2. Find ideas in three places

1. **News this week** in their field (search the web; prefer the official source). Post these first, they go stale.
2. **Their own proof**: results, client wins, numbers from their own data. These are the strongest shorts. Ask for the real numbers; never estimate one.
3. **Evergreen how-tos**: the questions their customers ask most. One question per short.

Offer about 1.5x the number they asked for, grouped by those three, one line each. Let them pick.

## 3. Write each script

Rules:
- 25 to 50 seconds spoken (about 70 to 130 words).
- Line 1 is the hook and names the topic. Say the keyword idea early.
- One point per line: every line becomes a visual beat in the edit.
- Plain words, their voice. No em dashes.
- No "link in bio" or "link below" lines (the automation handles links).
- End on: `Comment KEYWORD and I'll send you <the thing>.`
- **Keyword**: one word, easy to spell, matches the thing (CHECKLIST, ROBOTS, AUDIT). Unique within the batch unless two shorts send to the same place.
- Mark every number, date or claim that could be wrong or outdated with **[CHECK: what to verify]**.
- If a short needs a screen demo, say what to record and where to click (they click and hold the mouse still for one second on anything to zoom).

## 4. Deliver

One document they can read while recording (a Google Doc or docs connector if available, otherwise a Markdown file they open). Per short:

```
3. Your title here            <- name the Tella video exactly this
Keyword: AUDIT · Sends: Free audit checklist (https://...)
Screen: none | what to record + where to click
<script, one line per beat>
[CHECK] ...
```

At the top: a table of destinations with their keywords, and the recording tips:
- Name each Tella video exactly like its title (number first).
- Messed up a line? Say it again; the last take wins.
- Screen shorts: record screen and camera together in Tella; browser at 125% zoom or more; hide emails, keys and client names.

Also save `batch.json` next to it for `/shorts:post` (fill `file` later):
```json
{"start_date": "", "shorts": [{"id": "3", "title": "Your title here", "keyword": "AUDIT",
  "link": "https://...", "thing": "the free audit checklist", "button": "Get the checklist", "file": "", "caption": ""}]}
```

Next step for them: record, then `/shorts:edit`.
