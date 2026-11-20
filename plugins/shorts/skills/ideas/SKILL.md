---
name: ideas
description: Use when someone gives a website and wants short-form video (TikTok, Reels, Shorts) topics researched from it, e.g. "find shorts ideas for my site", "research my industry for shorts", "14 shorts from my website", "what questions should my shorts answer". Reads the site, pulls the People Also Ask questions for each service and the wider industry from DataWise, ranks them by search volume and writes 14 recordable scripts with hooks, comment keywords and real destination links. Needs the DataWise connector.
---

# Shorts Machine: ideas from a website

Website in, 14 researched scripts out (two weeks of one short a day). Every short answers a question people really search, found with DataWise. The writing follows the `script` skill's rules, so `/shorts:edit` and `/shorts:post` work on the result unchanged.

This skill never edits the `script` skill. It only reads its rules.

## 0. Check the tools

- DataWise must be connected: look for tools named `datawise_people_also_ask` and `datawise_keyword_metrics` (any prefix). If missing, stop and say: "Connect DataWise first: in Claude Code run `/mcp` and sign in to DataWise; in the Claude app add the DataWise connector. It's included with AI Ranking."
- Read `~/.config/ai-ranking-shorts/config.json` if it exists (`cta_default_link`, brand). If it does not exist, carry on and ask for a default link in step 2.
- Read the `script` skill (the SKILL.md next to this folder, `../script/SKILL.md`), sections "3. Write each script" and "4. Deliver". Those rules and that format apply to everything written here.
- If the `script` skill isn't installed (this skill was added on its own), use these rules instead: 25 to 50 seconds spoken (70 to 130 words); line 1 is the hook and names the topic; one point per line; plain words in their voice; no em dashes; no "link in bio"; end on `Comment KEYWORD and I'll send you <the thing>.`; one-word keywords, easy to spell, unique unless two shorts share a destination; mark every number, date or claim with `[CHECK: what to verify]`; never invent a link. Per short write: `<n>. <Title>` (they name the video this), `Keyword: X · Sends: <name> (<link>)`, `Screen: none | what to record`, the script one line per beat, then the [CHECK] notes.

## 1. Read the website

Fetch the homepage, then the service pages (nav links, `/services`, `sitemap.xml` if the nav is unclear). At most about 10 pages. Write down:
- What the business does, for whom, and where (city/country, or online).
- The services: 3 to 7, using the business's own names for them.
- FAQs already on the site (their wording is gold: these are questions customers really ask).
- Destinations: free checklists, guides, tools, reports, a booking or contact page, a community, a newsletter. Name + full URL each. Check the footer too: "free tools" and "popular guides" links there often match a question exactly (a free keyword tool for "best free keyword research tool").
- Proof: a wins, results, case study or testimonials page. Note each result with its number and the person's name, to confirm in step 1.
- The tone of voice (casual, technical, premium).

Show a 5-line summary, the destinations list and any results found on the site. Ask once: "Anything wrong, can I use these results, and are there other client wins with real numbers?" Do not continue until they answer (an empty answer is fine).

## 2. Pull the questions (DataWise)

Seeds:
- **Service seeds**: one per service, in the words a customer would search ("roof repair", "gutter cleaning cost", "local SEO"). Add the city only if the business is local and the plain seed is too broad.
- **Industry seeds**: 2 or 3 broad ones for the whole field ("roofing", "SEO for small business").

Calls:
1. `datawise_people_also_ask` for every seed (service seeds first), with `depth: 1`. Use `depth: 2` only for the one or two most important seeds: deeper levels drift off topic fast and the replies are long. Keep each question with the seed it came from.
2. Add the site's own FAQ questions.
3. **Throw out noise.** PAA mixes in questions that are near the topic but useless for a business's shorts: careers, jobs and salaries ("is SEO a high paying skill"), generic marketing trivia ("what is the 3-3-3 rule"), viral oddities, and anything about a different industry. Keep only questions a potential customer of this business would ask.
4. Dedupe (same question in other words counts once; keep the clearest wording).
4. `datawise_keyword_metrics` on the questions plus each seed (up to 50 per call; one call is usually enough). Questions often show no volume: keep them, the seed's volume shows the topic is searched.

Budget: DataWise has a daily data allowance. Stay under about 12 calls in total. Never loop over every question with separate calls.

If a seed returns nothing, try a shorter version once, then move on.

## 3. Pick 14

Score each question:
- **Searched**: volume of the question or its seed.
- **Sells**: close to a paid service (cost, how long, is it worth it, X vs Y, do I need) beats trivia.
- **Shortable**: answerable in 30 to 45 seconds with one clear point.
- **Has a destination**: maps to one of the destinations. No destination, no short (fall back to `cta_default_link` or the booking/contact page).

Pick 14 with this mix:
- About 8 **service FAQs** (cost, timing, mistakes, comparisons, "do I need").
- About 4 **industry PAAs** (the broad questions that bring new people in).
- About 2 **proof** shorts from the real results they gave in step 1. If they gave none, use 2 more service FAQs and say so.

Do not pick two shorts that answer the same thing.

## 4. Hooks

Line 1 of each script uses one of these patterns, rotated so no pattern is used more than 3 times:

| Pattern | Example |
|---|---|
| The real answer | "How much does a new roof cost? Here's the real number." |
| Most people get it wrong | "Most people think X. It's the opposite." |
| Stop / don't | "Don't sign a roofing quote until you check this." |
| The question I get most | "The question I get every single week: ..." |
| Number list | "3 signs your gutters need replacing, not cleaning." |
| Before vs after / X vs Y | "Repair or replace? Here's how to decide in 10 seconds." |
| Proof | "This client went from 0 to 40 calls a month. Here's what changed." |

The hook names the topic in the first five words. Never a slow intro ("Hey guys, today...").

## 5. Write and deliver

Write all 14 with the `script` skill's rules (25 to 50 seconds, one point per line, `Comment KEYWORD and I'll send you ...`, one-word keywords, [CHECK] on every number, date or claim, never invent a link).

Deliver in the `script` skill's format (one document plus `batch.json`), with this added under each short:

```
Source: People Also Ask for "<seed>" · volume <n or "topic: n">
Hook pattern: <pattern>
```

And at the top of the document, a short research table: seed, monthly volume, questions found. This is the proof the topics are real.

Save next to each other in the current folder: `shorts-<site>-<YYYY-MM-DD>.md` and `batch.json`.

Next step for them: read the scripts out loud once, confirm every [CHECK], record in Tella, then `/shorts:edit`.
