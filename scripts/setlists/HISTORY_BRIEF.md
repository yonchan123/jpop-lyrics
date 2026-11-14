# Setlist history brief (for live-frequency stats)

Goal: for each assigned artist, collect **many past setlists** so we can count how often each song is played live.

## Scope
- Window: shows dated **2025-01-01 → today**. Take every show with a full published setlist, including one-man shows, tour stops and festival sets.
- Aim for **10–25 shows per artist**. If a tour repeats an identical setlist, include each date anyway, because repeats are real plays. Stop at 25, newest first.
- If fewer than 5 shows exist in the window, extend back to 2024-01-01.
- Mark each show `"type": "oneman" | "tour" | "fes" | "event"`.

## How to search
Use the Aside browser (Claude in Chrome). Same tools, tab rules and CAPTCHA/consent rules as `scripts/setlists/BRIEF.md`. Read that file first.
- Best list sources:
  - **LiveFans** artist page → イベント/セットリスト list (livefans.jp/artists/{id}), paged.
  - **setlist.fm** artist page (paged, `?page=2`). Titles may be romaji. If so, add `repo_title` per song by matching against the repo folder README, or set it to null when the song isn't in the repo.
- Page loads are cheap here. Use `get_page_text` on list pages, then open each event. Budget is about 40 page loads per artist. Use javascript_tool fetch for same-origin pages when it is faster.
- WebSearch is exhausted, so don't use it.

## Output
ONE JSON file (path given in your prompt): a list of artist objects.
```json
{"folder": "SHISHAMO - ALL", "status": "ok|not_found",
 "shows": [
   {"event": "...", "date": "2026-06-14", "venue": "...", "type": "oneman",
    "source_url": "...", "songs": [{"title": "明日も", "encore": false}, ...]}
 ],
 "note": "short Korean note: coverage gaps, e.g. '2025 상반기 기록 적음'"}
```
- Song titles are Japanese originals as the source writes them, with version tags like (Acoustic ver.) stripped. Skip SE/MC/medley headers, but list medley songs individually.
- No duplicate shows (same date + venue).
- Finish with 1 line per artist: number of shows and date range.
