# Cards: specs and recipes

Colours below are config keys (`brand.card.*` in config.json), not fixed hex values. Defaults: bg #ECECEC, title #3A3A3A, muted #9C9C9C, text #1F1F1F, accent #DE7356, dark #2B2B2B, cta #2FA36B.

## Building a card

Canvas 1080x1920. Create with `create_motion_document` (videoId, width 1080, height 1920), fill with `apply_motion_editor_commands`. Reuse a card inside the same video with `duplicate_motion_document` plus `setTitle` edits. Place it with `add_layout` (`media: {type: "motion", documentId}`, `transitionStyle: "hardCut"`, start and duration on the playback timeline); `apply_video_edits` does not accept motion media. Then set the layout after each card to `hardCut` too.

Make every node end at the card length and set the canvas to the same length; make the doc slightly LONGER than its slot (a doc that ends exactly at the slot end shows one black frame). Keep the area below y 1400 empty: captions sit there.

## Row card (one option, for "things to do")

| Node | Spec |
|---|---|
| `bg` | fill, `bg` |
| `num` | "#1", Archivo 900, 170 px, `muted`, box x40 y250 w1000, lineHeight 1 |
| `title` | 2 lines, Archivo 900, 104 px, `title`, box x40 y430 w1000, lineHeight 1.05, start 0.1 |
| `shadow` | rect x120 y778 w840 h570, #0000001F, radius 40, start 0.45 |
| `card` | rect x120 y760 w840 h570, white, radius 36, start 0.45 |
| `accent` | rect x880 y700 w120 h120, `dark`, radius 28, start 0.7, with a white icon or a logo on it |
| `row1..4` | Inter 600, 38 px, `text`, box x170 w520, y 836 / 961 / 1086 / 1211, starts 0.9 / 1.15 / 1.4 / 1.65 |
| `div1..3` | rect x170 w740 h2 #E4E4E4, y 922 / 1047 / 1172 |
| pills | h54 radius 27, right edge x910, y 834 / 959 / 1084 / 1209; Inter 800 24 px white; `accent` for the problem, `dark` for neutral, `cta` for "do this". Start on the word that names them. |

Entrances, one set per card, rotate: (1) number pop, title rise by word, card pop, rows rise by line; (2) title typewriter, card slideUp, rows typewriter; (3) number slideDown, title drop by word, card slideRight, rows slideLeft; (4) number slideLeft, title spread from centre, card pop springBouncy, rows blur; (5) title blur by word, card x keyframes 1080 to 0 easeOutBack, rows pop by word.

## Concept cards (for "how it works")

- **One splits into many**: `python3 scripts/tree_card.py spec.json` (spec in its docstring). Root bubble, trunk that grows, 2 to 4 branch chips on their words, optional tag on every branch.
- **Many feed into one**: `python3 scripts/converge_card.py spec.json`. Source chips (one `muted`, e.g. "your website"), lines into a dark node with an icon or logo (`nodeLogo: "icon:bot.white"` or `"logo:chatgpt"`), tag on every source.
- **Before / after or dropping**: two stacked states, or a number or bar falling, keyed on the words.
- **Steps in order**: numbered chips joined by a line that grows step by step.

A concept card can run 10 to 13 s when it builds with the words. When a card gets longer, move the next face section's start too, or the old section cuts it short.

## Split intro

First 3 to 5 s: mini-scene on the top half, face on the bottom half, then hard cut.
- Face: time-ranged `add_layout` `{kind: custom, subject: {point: {x: -314, y: 960}, dimensions: {width: 1707, height: 960}, corners: none}}` with `hardCut` (16:9 camera cover-fitted to 1080x960; adjust x if they sit off-centre). For a 9:16 camera, fit the face into the bottom half instead.
- Top: a Motion doc whose `bg` covers only 0..960, placed with `apply_video_edits` `add_media_overlay` (`motionDocumentId`) for the same range. A Motion doc plays in one place only; duplicate to reuse.
- Never use slide presets here: they fly across the face. Fade or pop.

## Tool-row card (for "the tools I use")

Title Archivo 900, 112 px at y 300 (2 lines) or 128 px at y 400. Card x120 w840 y640, height rows x 140 + 24. Row: logo 84 px at x170 (`sheet_cmd.py ... logo:<name>:170:<rowTop>:84:<start>`), name Inter 700 46 px at x285, optional pill. No logo for a tool: dark 84 px tile with its initial (tell the member).

## Icons and logos

```bash
python3 scripts/sheet_cmd.py --list icon      # names; colours: dark coral white green
python3 scripts/sheet_cmd.py --list logo
python3 scripts/sheet_cmd.py 6.5 icon:bot.coral:170:680:120:0.8 logo:claude:420:680:110:1.0:l2
```
Paste the output into the card's `apply_motion_editor_commands` batch. Line icons read well at 90 to 200 px; one hero icon can go to 420 px. Favicon-based logos are soft above about 120 px.
