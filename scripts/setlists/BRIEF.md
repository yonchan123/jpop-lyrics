# Setlist brief (shared)

For each artist assigned to you, find their **most recent completed concert with a full, published setlist** dated before or on 2026-11-15. Prefer, in order:
1. The latest one-man show or tour stop (a tour final is a good pick).
2. Otherwise the latest festival set (only if it has a full setlist).

If the most recent tour has several shows with different setlists, pick the latest show and say so.

## How to search (Aside browser = Claude in Chrome)
1. Load the tools in ONE ToolSearch call: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp,mcp__claude-in-chrome__browser_batch`
2. Call tabs_context_mcp, then open **your own new tab** with tabs_create_mcp. Other agents share this browser at the same time, so use only your own tab id. Close it when you finish.
3. Search on Bing: `https://www.bing.com/search?q=<url-encoded>`. Queries like `{artist} セットリスト 2026` or `{artist} setlist`.
4. Good sources:
   - setlist.fm (artist page → latest)
   - livefans.jp
   - the official site's live report
   - SPICE, BARKS, Real Sound, rockinon.com, ぴあ, M-ON!, the BanG Dream official news site (bang-dream.com)
   - fan setlist blogs (lower confidence)
5. natalie.mu may show a CAPTCHA. If any site shows a CAPTCHA, skip it and never solve it. Never click consent, terms or login buttons. X needs a login, so skip it.
6. WebSearch is exhausted, so don't use it. curl/WebFetch on known URLs is OK.
7. Budget: about 8–12 page loads per artist. If nothing is found after 3 searches, record `not_found`.

## Matching help
The repo folder for each artist is `/Users/changyeon/Workspace/jpop-lyrics/translation/{folder}/`. README.md lists every song title. Write setlist song titles **exactly as the source writes them** (Japanese original). Don't translate them. Don't include lyrics. MC, SE, encore markers: put encore songs in order and mark `"encore": true`. Skip SE/MC/opening-movie lines unless they are actual songs.

## Output
Write ONE JSON file (path given in your prompt): a list of objects:
```json
{"folder": "SHISHAMO - ALL", "status": "ok|not_found",
 "event": "SHISHAMO ... TOUR 2026 ...", "date": "2026-10-12", "venue": "...", "city": "...",
 "source_url": "...", "source_type": "setlist.fm|livefans|official|press|blog", "confidence": "high|medium|low",
 "songs": [{"title": "明日も", "encore": false}, ...],
 "note": "short note (e.g. 'tour final', 'festival set', 'setlist differs by day')"}
```
Finish with a short summary of 1 line per artist (event, date, song count).
