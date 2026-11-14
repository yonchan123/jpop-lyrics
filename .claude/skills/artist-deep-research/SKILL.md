---
name: artist-deep-research
description: Build an exhaustive Korean research report on one artist/band in this jpop-lyrics repo — history, members, discography, tie-ups, live/overseas, gear, the songwriter's own interview statements, and how those connect to the lyric worldview read from the repo's own 3-line translations (with era statistics) — then publish it as a private Artifact page and save it under research/ (private repo only). Use whenever the user asks to analyze an artist's lyrics or worldview, find interviews about the songwriter and connect them to the lyrics, or says things like "○○의 모든 것을 알고 싶어", "가사 분석해줘", "작사가는 어떤 경험을 했을까", "인터뷰 찾아서 가사랑 연결해줘", "리포트로 정리해줘", even if they don't say "research" or name the skill.
---

# Artist deep research

You turn the repo's translations of one artist into a fan-grade research report. Fans read it as "everything about this artist". Three things make it worth more than a web summary:

1. **The corpus.** The repo holds every song in 3-line form (original / reading / Korean meaning). Reading all the meaning lines gives a worldview analysis that no outside article has. Counting words in the Japanese originals by era turns impressions into numbers.
2. **The songwriter's own words.** Interviews are matched against songs, and each link is labelled as either the artist's own statement or our interpretation.
3. **Honest sourcing.** Every claim carries a tag. Conflicting records are shown side by side, and nothing unsourced is stated as fact.

Lyrics are copyrighted. The report paraphrases and never quotes a lyric line. This is checked mechanically before anything is published (step 6).

Paths below are relative to the repo root. `$K` = `.claude/skills/artist-deep-research`.

## 0. Scope

- Find the collection: `translation/{artist} - ALL/` (fall back to album/setlist folders). Its README gives release dates, and the song files hold the credits.
- Pick a research title in Korean, short, with no punctuation: `{호칭} 종합 연구`. If one already exists in `research/`, add what is new (`… 인터뷰 보강`) or a number. Never write into an earlier folder.
- Create `research/{title}/corpus/` and `research/{title}/notes/`. `research/` is in `.publish-exclude`, so nothing here reaches the public repo. Check that the line is still there.
- If the user has already been discussing this artist, collect what was established: claims with sources, interpretations the user liked, and corrections the user made. These go into the briefs and the writer prompt. Without them the subagents would redo or contradict that work.

## 1. Corpus

```bash
python3 -I $K/scripts/corpus_stats.py "translation/{collection}" "research/{title}/corpus" [--eras 2015-2018,2019-2022,2023-2026] [--lyricist NAME]
```

- `--lyricist` defaults to the most frequent 作词 credit. Check that this is really the songwriter you mean. For artists with several writers, run once per writer or pass the one the user cares about.
- Choose `--eras` from real career breaks such as major debut or member changes. When unsure, leave it out and the script splits the songs into thirds.
- Output: `meaning.txt` (the corpus), `credits.tsv`, and `stats.md` (keyword table, credits, and the songs by other lyricists, which are usually covers and tributes).

Don't read `meaning.txt` yourself. It is large, and the corpus analyst reads it. Do read `stats.md`, because it shapes the briefs.

## 2. Research (six agents, one turn)

Send all six briefs from `references/briefs.md` in a single turn, as parallel `Agent` calls of `subagent_type: "general-purpose"`:

| brief | notes file |
|---|---|
| corpus analyst | `lyrics_corpus.md` |
| history & members | `history_timeline.md` |
| discography & tie-ups | `discography_tieups.md` |
| songwriter in their own words | `songwriter_interviews.md` |
| sound, gear & live | `sound_gear_live.md` |
| reception | `reception.md` |

Lessons from the first run (Regal Lily, 2026-11):

- **Put guesses under "Verify", never in the question.** When the coordinator seeded briefs with half-remembered "facts" (a wrong anime tie-up, a guitar model, an injury, a concert venue), researchers had to spend effort disproving them, and some nearly slipped through. List what is already sourced as "established", and everything else as "verify".
- **Don't correct the user from one source.** The user said the songwriter's songs were dismissed by a boys' band. One interview mentioned only gender, and the coordinator "corrected" the user. A second interview confirmed the user was right. Before telling the user they are wrong, check a second source or say plainly that the evidence is thin.
- natalie.mu and uta-net block fetching. Snippet-only facts are fine if they are labelled.
- **WebSearch quota runs out (200 per session).** On the 2026-11 にしな/Conton run it ran dry mid-research and later notes came back thin. Put this fallback in every research brief: when WebSearch errors on quota, keep going through the Aside browser (Claude in Chrome tools, loaded in one ToolSearch call). Open your own new tab, search on Bing or DuckDuckGo (if Google shows a CAPTCHA, switch engines, never solve it), and read pages with get_page_text or same-origin fetch via javascript_tool. Known URLs still open directly with curl/WebFetch, which don't use the quota. Don't click terms or consent buttons.
- **Lyric analysis needs song-by-song close reading, not only motif tables.** On the second run (Necry Talkie) the user called the lyric chapter "너무 빈약" because it had only motif and stats tables. Alongside the six briefs, send close-reading agents (`references/briefs.md` §2b), one per block of about 25–30 songs by file number. Each writes `notes/close_reading_{NN}_{NN}.md`: speaker and situation, how the song unfolds, where the dark turn lands, devices the Korean loses, and links to interviews. The lyric chapter is the core of the report. Give it a per-song guide grouped by release, not just tables.
- **Point at the lyric itself.** On the fifth run (CHOQMAY) the user found pure paraphrase useless ("가사 부분 언급도 안되는건 솔직히 개에바임") and the first fix too strict ("적당히해"). Each discussed moment gets its location (1절/후렴/브리지, Nth block), short glossed Japanese phrases (≤9 chars, no count cap), and the song heading links to its translation file in the private GitHub repo. Only full lines (or fragments stitched into one) are off limits, and the leak check still gates.

While the agents run, tell the user what is in flight in one or two lines. When each one finishes, pass on the one or two findings a fan would care about most, and any correction to something you said earlier. Don't paste the agent's whole report.

## 3. Report

When all six notes exist, send the report-writer brief (`references/briefs.md` §8) with:

- the user's full question,
- conversation findings that are not in the notes,
- the conflicts you noticed between notes, so the writer adjudicates them openly,
- the save path `research/{title}/report.md`.

The harness may refuse the writer's Write call for a report file and have it return the Markdown as text instead (seen on the second run, Necry Talkie). Don't retype it. Pull the fenced ```markdown block out of the agent's output transcript (JSONL, last assistant text block) with a short Python script and write that to `report.md`.

The user reads Korean and knows only a little Japanese. In the report, write names, titles and terms in Korean, and give the original in parentheses only the first time each appears (rule in `references/briefs.md` §8). When reading the report in step 4, check for raw kanji or kana left in the running text.

## 4. Read the whole report

You publish this report, so read every line. Page through it with offset and limit if it is long. Look for:

- lyric quotes that slipped in,
- claims without a tag or source,
- conflicts presented as settled,
- anything that contradicts what you told the user.

Fix small problems with Edit. Send larger ones back to the writer.

## 5. Lyric-leak check (gate)

```bash
python3 -I $K/scripts/lyric_leak_check.py "translation/{collection}" "research/{title}/report.md"
```

This flags any run of 10 or more characters from an original line, or 16 or more from a Korean meaning line, that appears verbatim in the report. Song titles are allowed. It prints only song titles and line numbers, never the text. Exit 1 means you paraphrase those passages and run it again. Don't publish until it prints OK.

Short quoted fragments add up, so run the density gate too:

```bash
python3 -I $K/scripts/fragment_density_check.py "translation/{collection}" "research/{title}/report.md"
```

Per song, quoted fragments may cover at most 10% of the original text and at most 10% of the Korean meaning text, and no line may be ≥50% quoted. Quoting the repo's Korean meaning wording counts: it is a translation of the lyric, so swapping a Japanese fragment for its quoted Korean meaning does not get around the limit. Use unquoted paraphrase. The first fragment-quoting drafts quoted up to 32% of a song, so trim to 1–3 well-chosen fragments plus location markers. Both checks must print OK.

## 6. Page and Artifact

```bash
python3 -I $K/scripts/build_page.py "research/{title}/report.md" "research/{title}/report.html" \
  --title "{title}" --eyebrow "{原語名} · {romaji} · {first year} — {now}" --subtitle "{one Korean sentence}" \
  [--accent "#xxxxxx" --accent-dark "#xxxxxx"]
```

- The template (`assets/page_template.html`) is a dark hero band, a sticky table of contents, tag chips, and scrollable tables, with light and dark themes. It renders Markdown with marked from cdnjs.
- Give each artist something of their own world. Pick an accent colour that fits the artist and their visual language. Put one small mark in the hero canvas: replace the `drawMotif` comment with a constellation, waveform, city skyline or similar. Keep it to one mark.
- Before the first publish in a session, the Artifact tool wants `action: "quickstart"` (intent `other`). Then publish `report.html` with a one-word `icon` and a one-sentence `description`. To update later, publish the same file path again.
- The artifact is private. Tell the user that other people need to be added through the Share menu.
- The template escapes every `~` before marked parses it. GFM reads a pair of single tildes ("2~3년 … ~라고") as strikethrough, which drew lines through whole sentences on the first eleven pages. Keep that escape if you touch the template.

## 6b. Biography (평전)

After the report, write a novel-like biography from the same notes: send the biography brief (`references/briefs.md` §9) to one general-purpose agent. The user read the first one (Necry Talkie, 2026-11) and said it was exactly what they wanted, so this is part of every run now, not an extra.

- It uses only the existing notes and report. No new research.
- Gate it with both lyric checks, then read the whole narrative yourself (strip link URLs into a scratch copy first; the links double the length). Look for invented scenes, feelings or dialogue that the notes don't support.
- When several biographies run at once, give each one an independent fact-check agent with the notes open (claim by claim, fixes by targeted Edit, gates rerun). On the 2026-11 batch these caught 5–17 fixes per book: invented quotes and scene details, statements moved to the wrong year or speaker, unlabelled band-name answers given to one member, and "흔히 잘못 알려져 있다" claims with no source.
- Build `biography.html` with build_page.py (`--title "{호칭} 평전"`, same eyebrow and accent as the report, a motif of its own) and publish it as a separate artifact with icon `book`.

## 7. Save and push (private repo only)

The report, notes, corpus and html already live under `research/{title}/`. To push:

```bash
scripts/publish.sh --only changyeon     # squashes local main into one snapshot commit, force-pushes the full tree to the private repo
scripts/publish.sh --dry-run --no-snapshot   # confirm the public tree would drop research/ (file count)
```

This force-pushes and rewrites history (see CLAUDE.md §9). Do it when the user's request covers saving or pushing, as in the original "개인 private repo에만 넣고". Otherwise ask once. Never push to yonchan from this skill. The next normal publish carries the public tree without `research/`.

Afterwards, send the Slack notification if `~/.claude/hooks/notify-slack.sh` exists.

## 8. Tell the user

Write in Korean, and keep it short:

- the artifact link,
- where the files are,
- the push result, including that the remote was verified,
- three or four findings a fan would love,
- what could not be confirmed.

If anything you told the user earlier in the conversation turned out wrong, say so plainly.
