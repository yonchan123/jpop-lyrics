# Subagent briefs

Fill `{…}` and send all six research briefs in ONE turn (parallel `Agent` calls,
`subagent_type: "general-purpose"`). Every brief ends with the shared rules block.

Contents:
1. Shared rules block (append to every brief)
2. Corpus analyst (reads the local translations)
3. History & members
4. Discography & tie-ups
5. Songwriter in their own words
6. Sound, gear & live
7. Reception (critics, industry, fans, overseas)
8. Report writer

---

## 1. Shared rules block

```
Rules:
- Current as of {today}. Cite a URL (and date when known) for every claim. Mark single-source or snippet-only items.
- Never reproduce a full lyric line or rebuild one from adjacent fragments. To point at a moment, name its location (1절/후렴/브리지, Nth 3-line block) and quote short Japanese phrases (≤9 chars) with a Korean gloss. Interview quotes ≤30 chars, sparingly.
- Items under "Verify" below are hypotheses, not facts: confirm, correct, or report "no source found". Do not repeat them as fact.
- Known blockers: natalie.mu and uta-net.com return 403/CAPTCHA to WebFetch and curl. Use search snippets for them and say so. utaten, j-lyric, BARKS, SPICE, OTOTOY, Skream!, THE FIRST TIMES, ぴあ, Real Sound, CINRA, Billboard JAPAN, Guitar Magazine and Fender News usually load.
- Prefer the official site and first-party interviews over fan wikis and summary sites (cancam-model.net and similar are low-trust).
- Notes may mix Korean/Japanese/English. Structure: Takeaway → Cited findings (by theme) → Inferences → Gaps.
Save your notes to {notes_dir}/{file}.md
```

`{notes_dir}` = `<repo>/research/{research title}/notes` (absolute path).

## 2. Corpus analyst → `lyrics_corpus.md`

```
Analyse the lyric worldview of {artist}'s songs written by {main_lyricist}, using the user's own Korean translations.

Inputs (read all of them; page through meaning.txt with offset/limit if it is long):
- {notes_dir}/../corpus/meaning.txt — one line per song: "[NN title] Korean meaning lines joined by /"
- {notes_dir}/../corpus/stats.md — keyword coverage by era, lyricist credits, songs by other lyricists
- Song files themselves in {collection_dir} if you need the Japanese original for a nuance (do not copy lines out)

Produce:
- Recurring motifs (5–10), each with the songs where it appears and a one-sentence paraphrase of how it appears.
- The arc across eras: what changes in theme, voice, imagery; cite stats.md numbers that support or contradict it.
- What the cover/outside-lyricist list suggests about inherited influences — mark as interpretation.
- Optional: pronoun / persona reading (僕/私/君/あなた), only if it clearly changes how songs read. Keep it short, and don't list it as an open question for interviews.
- 5–10 songs that best represent each era, with why.
- Open questions that interviews could answer (e.g., "is song X about a real person?") — the report writer will match these against interview notes.
```

## 2b. Close reader (one per ~25–30 songs) → `close_reading_{NN}_{NN}.md`

```
Close-read songs {NN}–{NN} in {collection_dir} (read each file fully: Japanese + Korean meaning).
Read first: {notes_dir}/songwriter_interviews.md if it exists, and stats.md.
Background: {lyricist aliases, eras, batches, who sings}.
For EACH song, in Korean, 6–12 sentences: title (#, date, credit); speaker & situation; how it unfolds verse→chorus→end (paraphrase); the dark turn and whether it is retracted, joked away or left standing; key images and devices, incl. what the Japanese does that the Korean meaning line loses (puns, dialect, register); links to interviews ([본인] only if said about this song, else [해석]) and to other songs by number; one-line summary.
Then 6–10 cross-song observations for the range.
Point at each moment by location (1절/후렴/브리지, Nth 3-line block) and short Japanese phrases (≤9 chars) with a Korean gloss; never a full line. Run lyric_leak_check.py on your notes until it prints OK.
```

Run these in parallel with the six briefs. If songwriter_interviews.md doesn't exist yet, they do the links in a second pass, or the writer does them.

## 3. History & members → `history_timeline.md`

```
Research the full history of {artist} from formation to {today}.
Key questions: formation (who, when, where, how they met), every member change with dates and official reasons, support members, labels and management with dates, contest wins, breakthrough moments (TV, viral, tie-up), landmark domestic shows (venue size progression), festivals, overseas shows (country, venue, date), first Korea show if any, and the band's state right now (latest release, current tour).
Verify: {claims from conversation or common knowledge that are not yet sourced}
```

## 4. Discography & tie-ups → `discography_tieups.md`

```
Research the complete discography and tie-ups of {artist} to {today}.
Key questions: every release (date, format, label, notable tracks, Oricon/Billboard JAPAN peak); tie-ups (anime OP/ED, film, drama, CM, game) with the work and year; cover and tribute-album participations (which tribute, original artist, date); producers/arrangers; songwriter's outside work (songs written for others, features, soundtracks); streaming/MV milestones.
Cross-check track groupings against the repo README at {collection_dir}/README.md (release dates live there).
Verify: {unsourced claims}
```

## 5. Songwriter in their own words → `songwriter_interviews.md`

```
Research what {songwriter} has said about themself in interviews, columns, radio, MCs and posts, {start year}–{today}.
Already established in this conversation (go beyond these; re-verify only if cheap): {bullet list of statements already found, each with source}
Key questions: childhood, family, hometown, school life; turning points (why music, why this band); reading, film, art, musical influences; songwriting method (what comes first, notebooks, revising, titles); comments on specific songs — especially {songs flagged as open questions by the corpus analyst}; mental/physical health, gender, social views as they chose to share them; feelings about member changes; solo work.
For dialogues/round-tables, confirm from the speaker labels who said each line.
Verify: {unsourced claims}
```

## 6. Sound, gear & live → `sound_gear_live.md`

```
Research {artist}'s sound, instruments and live performance to {today}.
Key questions: each member's instruments, amps, effects, tunings (with interview/gear-feature sources); how songs are arranged and recorded (demo process, producers, engineers, studios); how the sound changed across releases and why; genre placement by critics vs. the band's own stated influences; live reports (staging, MC style, arrangements that differ from records).
Suggested: Guitar Magazine, Fender News, Bass Magazine, Rhythm & Drums, サウンド&レコーディング, plugplus (rittor-music), live reports on SPICE / THE FIRST TIMES / rockinon / Real Sound.
Verify: {unsourced claims}
```

## 7. Reception → `reception.md`

```
Research how critics, fellow musicians, industry figures, fans and overseas listeners evaluate {artist} / {songwriter}, to {today}.
Key questions: album reviews and year-end lists/awards; named musicians/producers who praised or collaborated (and where the "genius"/"大物絶賛" type labels actually came from); fan-favourite songs (reader polls, YouTube/Spotify/Last.fm numbers, with snapshot dates); dissent and criticism (including fan blogs — label them as individual opinion); overseas reception (Korean official spelling and promoter, Korean/Chinese/English communities, overseas reviews).
Keep professional criticism and fan opinion clearly separated.
Verify: {unsourced claims}
```

## 8. Report writer → `report.md`

Send after all six notes exist.

```
Read every file in {notes_dir}/ and write a Korean long-form research report that answers: "{the user's question, in full — e.g. '{artist}의 모든 것: 연혁·멤버·디스코그래피·타이업·공연, 사운드/기재, 작사가 본인의 발언과 가사 세계관의 연결, 평단·팬·해외 반응'}".

Also fold in these findings already established in the conversation (they are not in the notes): {bullets: lyric analysis points made to the user, stats, interpretations the user reacted to, corrections the user made}.

Structure:
- H1 = an evocative Korean title about the artist (not "보고서").
- Opening summary paragraph: who they are, the arc in 2–3 phases, the core of the lyric world, how it connects to the songwriter's life, how they are received.
- A note on naming (Korean official spelling vs. the user's usage) and scope (lyrics are paraphrased, never quoted).
- Chapters: history (with a timeline table) → members (table) → discography (table with chart peaks; covers table with original lyricist) → tie-ups (table) → live & overseas (table) → sound & gear (table) → the songwriter in their own words → lyric worldview (the longest chapter: motifs as short essays, eras, a per-song guide grouped by release with 3–6 sentences per song from the close-reading notes, each song heading linked to its file in the private GitHub repo (https://github.com/changyeon/jpop-lyrics/blob/main/translation/{encoded folder}/{encoded file}) and each moment located by section/block with short glossed phrases, stats table, "statement ↔ song" table with a column saying whether the link is the artist's own or interpretation) → reception → "확인되지 않은 것과 엇갈리는 기록" (conflict table: A record / B record / judgement) → conclusion.
- Tag every claim-bearing sentence or paragraph with **[확인]** (sourced fact), **[본인]** (the artist's own statement), **[평론]** (critic/media view) or **[해석]** (your interpretation). The page renders these as coloured chips.
- Inline Markdown links for sources. Tables for anything list-like.
- Never reproduce a full lyric line; short Japanese phrases (≤9 chars) with a Korean gloss are fine for pointing at moments, together with the location (1절/후렴/Nth block). Interview quotes ≤30 chars with a Korean gloss.
- Korean readability: the reader knows a little Japanese but reads Korean. Write names, titles and terms in Korean, and give the original in parentheses only the first time each appears. After that, use Korean only.
  - People: 아사히(朝日), 못사(もっさ). Use the Korean official spelling if one exists.
  - Song and album titles: 「오샤레 대작전(オシャレ大作戦)」. Take the Hangul reading from the collection README's `읽기` column. Add the meaning once if the title isn't self-explanatory.
  - Words and pronouns: 보쿠(僕), 오레(俺), 거짓말(嘘).
  - Venues, media and labels: Korean name with the original in parentheses the first time.
  - Inside tables, use Korean. Keep the original only in a column that exists for it.
  - Keep raw kana or kanji only where the point is about the script itself, such as the word statistics. Even there, gloss it.
- Where notes disagree, present both and judge; never silently pick one.

Save to: {report_path}
```

## 9. Biography writer → `biography.md` (평전)

Run after `report.md` exists. The user asked for this format after the encyclopedic reports ("자서전처럼/소설처럼") and approved the first one (Necry Talkie, 2026-11): "이게 바로 내가 원하던 거야". Fill `{artist}`, `{songwriter}`, `{folder}`, `{collection}` and an era outline drawn from `history_timeline.md`.

```
Write a Korean narrative biography (평전) of {artist}, centred on songwriter {songwriter} and also covering the other members and the band. The reader is Korean, knows little Japanese, and wants it to read like a novel: follow the life from the start — childhood, first contact with music, first instrument, early projects, forming the band, each era — and at each point tell which songs were written, the writer's situation, and the feeling that went into them. A reference appendix with tables goes at the END.

## Sources — ONLY these (no web search, no fetching)
{folder}/notes/*.md (songwriter_interviews.md matters most: their own words), the close_reading_*.md files, and report.md (tables, link URLs, Korean title readings; read in parts). Song files: translation/{collection}/ (README has dates and Korean readings). Where notes conflict, follow how report.md settled it.

## Voice and honesty (most important)
- Third person, literary, warm; chapters with scenes, not bullet lists.
- Never invent inner feelings, dialogue or scenes. Feelings come from interviews, written into the flow ("{songwriter}는 훗날 인터뷰에서 …라고 돌아봤다"). Our readings are marked as interpretation ("…였을지도 모른다", "이 시기와 겹쳐 읽으면"). Scene details only from the notes.
- Where the record is thin, say so briefly ("이 시절에 대해 남긴 말은 많지 않다") instead of filling the gap.
- No per-sentence tag chips. End each chapter with a short "이 장의 출처" blockquote: source ids used, and which claims are interpretation.
- Conflicting records: mention briefly; never present as settled.
- No "흔히 …로 잘못 알려져 있다" unless a source shows the misconception is actually common; just state the sourced fact.
- Keep each statement in the year it was said, and the speaker who said it (band-name answers stay "밴드 명의 답").

## Korean readability
Names, titles and terms in Korean; original in parentheses only at first appearance. Song titles: the README's Korean reading in 「」 plus meaning at first appearance when not obvious. No raw kana/kanji in running text after first mention.

## Lyrics — copyright (mechanically checked)
Never quote a full line or stitch fragments. Point at moments: location (1절/후렴/브리지) + a glossed fragment ≤9 chars; a song's first mention links to its translation file (copy the GitHub URL form from report.md). Per song ≤10% quoted (Japanese, and quoted repo Korean meaning wording too), 1–2 fragments max. Run both gates (lyric_leak_check.py, fragment_density_check.py) on your file and fix until both print OK.

## Shape
- Novel-like Korean title + 2–3 line preface (based on the research notes, 기준일, how to read 본인 말 vs 해석, lyric policy).
- Prologue: one real documented moment that sets the theme.
- ~8–12 chronological chapters: {era outline}. Songs appear where written/released; important ones get real space, others grouped.
- Epilogue.
- 부록: 연표; 작품 목록; 타이업; 멤버·기재; 가사 통계 요약; 곡 찾아보기 (# · 한글 제목 · 원제 · 발매일 · 다루는 장).
- Narrative roughly 40–70k Korean characters, plus appendix.

## Output
Write {folder}/biography.md only. If Write is refused, return the whole Markdown in one ```markdown block.
Final message: path, character count, chapter list, both gate results, anything the notes could not support.
```
