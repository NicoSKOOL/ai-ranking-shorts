---
name: edit
description: Use when raw talking-head recordings in Tella should become finished 9:16 shorts (TikTok, Reels, Shorts), e.g. "edit my shorts", "edit this Tella video into a short", "I recorded the batch", or a tella.tv link plus "make it a short". Cuts retakes and silences, builds a different animated visual idea per short with icons, logos and sound in Tella Motion, adds captions and a comment-keyword pill, and verifies frame by frame. Everything stays editable in Tella.
---

# Shorts Machine: edit

Raw recording in Tella in, finished 9:16 short out, all through the Tella MCP (`mcp__tella__*`), so the member can still change anything in Tella. Cuts, Motion cards, captions and exports use no Tella AI credits.

**Before anything:** read `~/.config/ai-ranking-shorts/style.md` (the member's own rules win over this file) and `config.json` (card colours). If they're missing, run `/shorts:setup`. Also read `reference/cards.md` and `reference/gotchas.md` in this skill folder before building the first card.

## Rules

- **Duplicate first** (`duplicate_video`, name it `<original> (edit)`). Never touch the original.
- **Words on cards come from what the speaker says**, or are clearly illustrative mock content (an example URL, a product in a mock shop). Never invent a number, a claim or a tool. Report every paraphrase and placeholder.
- **Every short gets its own signature visual idea.** Before building, write one line: "the signature idea of this short is ___". If two shorts in a batch have the same answer, change one. See `reference/signature-ideas.md`.
- **Every concrete noun gets a visual on its word**: an agent, a phone, a calendar, a town, a bot, money. Icons (`icon:` in `scripts/sheet_cmd.py`), real tool logos (`logo:`) when a tool is named, mock UI, counters.
- **Hard cuts only** between cards, screen and face. No em dashes anywhere on screen.
- Report honestly: frames are checked, audio is not heard.

## How much to do per run

One short uses a lot of Claude: about 250,000 to 300,000 tokens in testing. Default to **2 or 3 shorts per run**, and finish each one before starting the next. For a big batch, the member can ask for parallel editing (one helper agent per 2 shorts); then YOU write each short's signature idea and per-word visuals first and hand that brief to the helper. Helpers told only "follow the skill" produce look-alike shorts.

## Step 1: Find and read the raw

- Videos are named after the script titles. `list_videos` / `search_videos` to find them. A tella.tv link ends in the video id's tail.
- `get_transcript` (text) and `get_timeline` include `layouts`. Note:
  - **Tracks.** Many Tella recordings carry a screen track. If it shows a teleprompter, notes or anything that isn't a real demo, NEVER show it: set the base layout to camera-only fullscreen. Show the screen only during real demos (check frames).
  - **Orientation.** Phone footage sometimes arrives sideways: see "Sideways footage" in `reference/gotchas.md`.
  - **Retakes** (a line said twice: keep the last full take), the sections (one per point), lines to drop ("link below").
  - **Where they went off script.** The recording wins. Flag anything that changes a claim, a number or the keyword.

## Step 2: Base settings

`update_video`: 1080x1920, `defaultClipTransition: hard_cut`, motion blur off (it smears a frame at cuts). Base layout fullscreen camera.

## Step 3: Cut

1. `cut_clip_by_transcript` for retakes and dropped lines.
2. `remove_silences` mode `faster`.
3. `get_timeline` include `words`: fix slivers at clip edges with `update_clip` `cuts`. Word timings can drift near long pauses; check with `ffmpeg -af silencedetect=noise=-35dB:d=0.12` on the source and cut by time.
4. Target: speech nearly back to back. Length is about spoken time plus 10 percent.

## Step 4: Plan the visuals (write it down before building)

For each section: what's said, the visual, the entrance, the sound (if any). Then build. Pattern that reads well: a 1 to 2 s face beat, then the card, so face and cards alternate; never more than two cards back to back.

Toolkit (details in `reference/cards.md`):
- **Split intro** for the first 3 to 5 s: title or mini-scene on top, face on the bottom half.
- **Cards** in Tella Motion (1080x1920), each with a different entrance. Row cards are ONE option, not the default.
- **Concept cards** whenever a point explains *how something works*: one-splits-into-many (`scripts/tree_card.py`), many-into-one (`scripts/converge_card.py`), before/after, steps in order.
- **Mock UI**: chat bubbles with typing dots, a phone, a browser bar, checkout steps, a search result, a listing, a calendar strip.
- **Counters** that count up to the number said.
- **Face stickers**: an icon or 1 to 3 word label beside the head for 1 to 2 s during face sections (Motion doc without background, `apply_video_edits` `add_media_overlay`). 2 to 4 per short. Dark or coloured icon on a white disc reads on any background.
- **Effects** (`list_motion_effects`): one particle burst at most per short (sparks, confetti) on the win; glow on the hero; trimPath to draw lines; radialWipe for a timer ring; linearWipe for a highlighter; chromatic aberration for "broken".
- **Sound** (`add_sound_effect` presets: press, tick, toggle, success, error, cha-ching, clock-ticking, countdown-tick, notification-chime, keyboard-typing, deep-woosh, cyber-glitch, bloom): 4 to 8 per short, volume 0.2 to 0.5, only on moments that matter.
- **Screen demos**: crop the screen to the content, face in a box below, captions at y 0.88; zoom where the speaker clicked (`get_mouse_events`, `add_zoom`) or use a tight crop for a single number.

## Step 5: Captions and the comment pill

- `update_video`: captions and subtitles on; classic style, white text, black outline 0.12, shadow, maxWidth 0.6; Inter 700 size 52; chunked, 1 line; position 0.5 / 0.78 (0.88 during screen demos). Use the member's style.md if it says otherwise.
- `update_transcript_words` only for words you can verify (tool names, numbers, the keyword). The keyword caption must match the keyword exactly.
- Comment pill on the last line: `add_text_overlay` `Comment "KEYWORD"`, Inter 800 60 px, white on the `cta` colour, squircle radius 60, padding 0.25, point 20/63, 648x130, intro `grow` with overshoot. If the speaker never says the keyword, flag it.

## Step 6: Verify

1. `get_filmstrip` of the whole video with subtitles (about 24 frames): every card, sticker, face section and the pill.
2. Strips at 30 to 40 ms steps around every cut: no colour flash, no black frame.
3. `get_video_frame` on any new element you're unsure about.

Report per short: the Tella view link, length, what was cut, the signature idea, placeholders and paraphrases, where they left the script, and that audio was not heard. Do not export here: `/shorts:post` exports after the member approves.

## When the member doesn't like an edit

Fix it in place (same video, same link). Then ask whether it should be a rule for every future short; if yes, add a dated line to `style.md` with the reason. That's how the machine gets better batch to batch.
