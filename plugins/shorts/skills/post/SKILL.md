---
name: post
description: Use when edited shorts are approved and should go out, e.g. "schedule my shorts", "post these one a day", "set up the comment keywords", "approved, schedule them", or to check how the comment automations are doing. Exports from Tella, writes captions, schedules one short a day to TikTok, Instagram and Facebook (YouTube optional) through Zernio, and creates comment-to-DM automations for every short that has a keyword.
---

# Shorts Machine: post

Approved shorts in, a two-week schedule with working comment automations out. Only run this after the member has approved the edits.

Needs `/shorts:setup` done (Zernio accounts, timezone, posting time). Scripts are in `<skill dir>/scripts/`.

## 1. Export

For each approved short: `export_video` (`subtitles: true`, fps 30), then `get_export_status` until `completed`. Use the `downloadUrl` from the COMPLETED status (the one returned at queue time can 404). Download each to a folder the member can find, e.g. `~/Downloads/shorts_<date>/short_<id>.mp4`, and check one frame per file with ffmpeg (the exported file should show the final visuals).

## 2. Captions

One caption per short, from what the short actually says (not the original script if they went off it):
- Line 1: the hook, with an emoji at most.
- The points, short lines or a short list.
- `Comment KEYWORD and I'll send you <the thing>.` (only when the short has a keyword)
- 3 to 5 relevant hashtags.
- No em dashes. No "link in bio" (the automation handles it). Never a claim the video doesn't make.

## 3. The batch file

Fill `batch.json` (from `/shorts:script`, or write it now):
```json
{"start_date": "2026-12-01", "first_time": "18:30",
 "shorts": [{"id": "1", "file": "/path/short_1.mp4", "caption": "...", "keyword": "AUDIT",
             "link": "https://...", "thing": "the free audit checklist", "button": "Get the checklist"}]}
```
- `link` must be a real page; never invent one. A short with no link: leave out `keyword`, `link`, `thing` and `button`; it is scheduled with no automation. `keyword` and `link` always go together.
- `button` is the DM button label, 20 characters max.
- Order: time-sensitive news first; spread similar shorts apart (a week between two on the same topic).
- `first_time` (optional) is for posting the first one later today.

## 4. Dry run, then schedule

```bash
python3 <skill dir>/scripts/schedule_batch.py batch.json --dry-run
```
Show the member the plan (date, time, keyword, link per short) and get a yes. Then:
```bash
python3 <skill dir>/scripts/schedule_batch.py batch.json
```
It re-encodes files over 18 MB, uploads each with the Zernio CLI (uploads are single use, so each short is ONE post with every platform), schedules it, and creates one automation per platform bound to the post. They switch on when the post goes live. Results are saved to `batch.result.json`.

What the commenter gets:
- **Instagram and Facebook**: a DM with a button to the link, then a public reply "Sent! Check your DMs".
- **TikTok**: a public reply with the link as text plus "also in my bio". TikTok can't DM and links in comments aren't clickable, so the member puts that day's link in their bio. The script prints the list of bio links by date.
- **YouTube** (if enabled): a reply "the link is in the description". Add the link to the description.

## 5. Report

Per short: date and time, keyword, where it sends. Plus what the member does by hand (TikTok bio link each day) and where the files are.

## Checking results later

Zernio connector `call_tool` `comment_automations_list_comment_automations` (profile id from the settings), or `zernio automations:list`: triggered, DMs sent, failed, link clicks. Compare shorts: which keywords got comments is the best guide for the next batch.

## If something fails

- Upload error: the file is too big for the network; re-encode smaller and retry that short only.
- Duplicate-content error (409): the same caption and media went to that account in the last 24 h; it's already scheduled.
- Instagram DMs need a Business or Creator account connected in Zernio.
