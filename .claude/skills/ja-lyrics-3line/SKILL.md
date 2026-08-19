---
name: ja-lyrics-3line
description: Use when given a list of Japanese songs (titles + artists, Spotify/Apple/YouTube URLs, or a Spotify playlist URL) and asked to produce 3-line JA→KO lyric translations (original / Hangul phonetic / Korean meaning) matching spotify-tools `.md` output format. Uses only Claude Code built-in tools (WebSearch, WebFetch, Read, Write); no external APIs.
---

# JA Lyrics 3-Line Translation

## When to use

Invoke this skill when:
- User provides a list of Japanese songs and asks for Korean lyric translation
- Input contains Spotify / Apple Music / YouTube URLs for JA songs
- User explicitly asks for "3-line translation" / "3단 가사 번역" / spotify-tools-style output

Do **not** invoke when:
- Translating concert MC dialogue (use `subtitle-pipeline-ja-to-ko`)
- Aligning existing canonical lyrics to audio (use `song-lyric-xval-pipeline`)
- Source language is not Japanese

## Repo conventions come first

If the working directory has a `CLAUDE.md` describing lyric-collection conventions, **read it and let it win** wherever it disagrees with this skill. A long-lived collection accumulates house style — credit-line wording, trailing-space width, transliteration choices, folder layout — and consistency with the existing files matters more than this document's defaults.

Before "fixing" a convention you think is wrong, count how the rest of the repo actually writes it. Judging from one folder, or from a handful of sampled files, has repeatedly produced confident changes in the wrong direction.

## Input formats

Accept any of:

1. **Spotify playlist URL** (single) — e.g. `https://open.spotify.com/playlist/<id>`. Expand via WebFetch to get the full track list + playlist title.
2. **Track URLs** (Spotify / Apple Music / YouTube, multiple). Each expanded via WebFetch to get (title, artist, album?).
3. **Freeform text list** — one song per line, in any of:
   - `Title - Artist`
   - `NN. Title - Artist`
   - `Title by Artist`
   - raw titles if artist is obvious from context
4. **Mixed** of the above.

Normalize internally to:

```
[
  { num: 1, title: "...", artist: "...", anchor_url?: "..." },
  { num: 2, ... },
  ...
]
```

Plus optional `playlist_title` string when the input was a playlist URL.

If the input is ambiguous (e.g., "translate these songs" with no titles or playlist), ask the user for the list. Do not proceed on guesswork.

## Pipeline

Process tracks sequentially through 5 stages. Stop at first stage that succeeds per track.

### 1. Normalize

For each input element:

- **Spotify playlist URL**: `WebFetch(url, "List all tracks. For each track output: track number, song title, artist. Also return the playlist title. Plain list output.")`. Parse into internal track records.
- **Single track URL** (Spotify/Apple/YouTube): `WebFetch(url, "What is the song title, artist, and album of this track? Return as 'Title | Artist | Album'.")`. Store as anchor metadata.
- **Freeform text line**: parse `Title - Artist` or variants. If only title given but artist can be inferred from a sibling URL or the user's message context, attach it.

If the input consists only of a single song, skip to stage 2 with a 1-element list.

### 2. Match

For each track:

1. **Build anchor** — remember `anchor_title`, `anchor_artist` (and `anchor_album` if known) from normalized metadata.
2. **Candidate search** — run `WebSearch` with query `"{title}" "{artist}" 歌詞`. If zero useful results, retry with `"{title}" {artist} lyrics` as secondary.
3. **Rank candidates** — for each result URL + snippet, evaluate two axes:
   - **Artist match**: exact, or transliteration variant (`BiSH` ↔ `ビッシュ`, `Aina The End` ↔ `アイナ・ジ・エンド`). "No" means an obviously different artist.
   - **Title match**: exact, or script/romanization variant (kanji ↔ kana ↔ romaji ↔ English).
4. **Confidence**:
   - Both pass → `high`
   - One passes, other unclear → `medium`
   - Both unclear OR artist obviously wrong → `low`
5. **Prefer** canonical lyric sites when confidence-tied: `uta-net.com`, `j-lyric.net`, `utaten.com` typically more reliable than aggregator blogs. Avoid video-caption sites where lyrics are OCR-scraped.
6. **Select best candidate** — highest confidence, ties broken by domain preference. If `low`, proceed anyway (flag for report); never block the batch.

Record `chosen_url`, `confidence`, and the ordered `candidates` list.

### 3. Fetch

**Do not use `WebFetch` for lyric bodies.** Its backing model refuses full-lyric reproduction on copyright grounds. Use `Bash` + `curl` and parse the raw HTML locally.

1. **Fetch raw HTML** with `Bash`:

   ```bash
   curl -sS -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15" "<chosen_url>"
   ```

2. **Extract the lyric body** using the per-domain recipe below. Pipe the HTML through `python3 -c` with a short inline extractor that:
   - Finds the lyric container via regex (see table).
   - Replaces `<br>` / `<br/>` with `\n`.
   - Strips remaining tags.
   - `html.unescape`s entities.

   Reference recipe (works for uta-net; adjust selector per domain):

   ```bash
   curl -sS -A "Mozilla/5.0" "<chosen_url>" | python3 -c "
   import sys, re, html
   raw = sys.stdin.read()
   m = re.search(r'<div[^>]*id=\"kashi_area\"[^>]*>(.*?)</div>', raw, re.S)
   if not m:
       sys.exit(2)
   body = m.group(1)
   body = re.sub(r'<br\s*/?>', '\n', body)
   body = re.sub(r'<[^>]+>', '', body)
   body = html.unescape(body).strip()
   print(body)
   "
   ```

3. **Per-domain selectors** (extend as needed):

   | Domain | Container selector (regex-friendly) | Notes |
   |---|---|---|
   | `utaten.com` | `<div[^>]*class="hiragana"[^>]*>(.*?)</div>` | **Try first.** Contains `<ruby>` furigana — strip the ruby tags but read them first, they settle kanji readings. |
   | `j-lyric.net` | `<p[^>]*id="Lyric"[^>]*>(.*?)</p>` | `<br>` as line break. Second choice. |
   | `kashinavi.com` | `<div[^>]*class="kashi"[^>]*>(.*?)</div>` | Third choice. |
   | `petitlyrics.com` | POST `/com/get_lyrics.ajax` | Body is not in the page HTML. Needs a same-session `PLSESSION` cookie plus the `X-CSRF-Token` scraped from `/lib/pl-lib.js`; response is a JSON array of base64 lines. Carries obscure tracks the other sites lack. |
   | `uta-net.com` | `<div[^>]*id="kashi_area"[^>]*>(.*?)</div>` | **Cloudflare-blocks curl (HTTP 403).** Use its search results to confirm a match, but extract the body elsewhere. An `r.jina.ai` proxy fetch sometimes works. |
   | `genius.com` | `<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>` | Last resort. Scrape residue (`N Contributors`, `… Lyrics`) leaks into the body — strip it. Also marks instrumentals explicitly. |
   | `lyrical-nonsense.com` | `<div[^>]*class="olyrictext">(.*?)</div>` | English-audience site; often romanized — avoid unless JP sites fail. |

4. **Credits** (optional, best-effort): search the HTML for `作詞` / `作曲` lines near the lyric container and keep them as a single `CREDITS` block for the output-format header. Missing → omit.

5. **Sanity-check** the extracted lines:
   - If fewer than 3 non-blank lines → treat as failure.
   - Strip leading lines that match obvious meta-headers (`^Lyrics$`, `^歌詞$`, artist name alone, title alone).
   - If the text is clearly not Japanese (no hiragana/katakana/kanji at all) → treat as failure (wrong page or English-only translation page).

6. **On failure** — try the next candidate URL from the Match stage (up to 3 total).

7. **If all candidates fail** — run **one fallback query** using title variants (romaji ↔ kana, add the album name if known) via `WebSearch`, then retry stages 2–3 once. If still failing, mark status `no_lyrics`.

8. **Instrumental tracks** exist and are not failures. If the sources agree the track has no lyrics (Genius marks it `[Instrumental]`, or the artist's other tracks are all indexed and this one is absent from every site), record it as an instrumental rather than `no_lyrics` — the distinction matters to the reader.

9. **Very recent releases** (days to a couple of weeks old) are often not transcribed anywhere yet. Say so plainly and leave a stub; do not pad with a guess.

### 4. Translate

Feed the extracted Japanese lines to the rules in the **Translation rules** section below. Produce the 3-line block output per line.

For lines where you are unsure of the intended meaning or reading, append `[?]` to the **third** (meaning) line. Do not skip lines. Do not invent content.

### 5. Write

Switch on track count:

- **1 track** → output the formatted 3-line block **directly in the chat response**. Do not create any file.
- **≥ 2 tracks** → create a new directory, write one `.md` file per track, a folder `README.md`, and update the root `README.md` index if one exists.

**Directory naming**:

1. If a `playlist_title` is known → sanitize it: replace `/\:*?"<>|` with `_`, collapse whitespace. Use as-is (e.g. `BiSH - Bye-Bye Show for Never/`).
2. Else → ask the user once: "Give me a short folder name for these translations (or press enter to use a timestamp)".
3. Fallback → `lyrics-YYYY-MM-DD-HHMM/` (zero-padded, local time).

Create under the current working directory unless the user specified otherwise.

**File naming**: `{NN}. {title} - {artist}.md` where `NN` is zero-padded 2 digits (`01`..`99`). Sanitize `title` and `artist` the same way as directory names.

**Folder `README.md`** (≥ 2 tracks): write a `README.md` in the output folder listing every track as a Markdown **table**, one row per track, in the folder's order. Percent-encode the filename in the link target (spaces → `%20`, etc.). Escape any `|` inside a cell as `\|`.

```markdown
| # | 발매일 | 곡 | 가수 | 읽기 | 뜻 |
|---:|---|---|---|---|---|
| 1 | 2020-10-23 | [うっせぇわ](01.%20...md) | Ado | 웃세에와 | 시끄러워 |
```

- `#` must always equal the track's filename number.
- `발매일` is the **original** release date `YYYY-MM-DD` — use the digital-single date when it predates the CD. Only write `발매일 미상` when it is genuinely unfindable. Fetch the artist's discography **once** and map releases to track ranges; do not run one search per track.
- `곡` holds the title alone (no artist); the artist gets its own column. Derive the artist from the **filename**, not the label — some collections label rows with the title only.
- `읽기` / `뜻` describe the **title**, not the lyrics: its Hangul reading and its Korean meaning, following the same phonetic rules as the lyric lines.

**Existing collections**: when adding to a folder that already exists, match whatever header and trailing-space convention that folder already uses rather than imposing this one.

**Ordering**: a folder that collects an artist's *complete* discography is kept in **release-date ascending** order, and its folder name carries an `- ALL` suffix. Ties (same single/album) keep their existing relative order — sort stably. Album folders stay in tracklist order and setlist folders stay in performance order; never date-sort those.

Adding a track to an `- ALL` collection therefore means re-sorting: renumber the `.md` filenames, then rewrite the README table and the status report so `#`, filename, and report row all agree. Rename in **two phases** (each file to a unique temp name, then to its final name) so numbers being swapped never collide.

**Root `README.md`** (when one exists at the repo/working-directory root): after creating the folder, add an entry for it to the **existing main track index list** — append a single list item continuing the existing numbering, with the folder link (percent-encoded) and track count, matching the surrounding items' format. **Do not create a separate section/heading** for the new batch; integrate into the existing list even if the batch is a thematically distinct collection (note any theme inline in the item, e.g. `— 68 tracks (BanG Dream!, 전곡 발매 순)`). Do not rewrite or renumber unrelated entries. If no root `README.md` exists, skip this step.

**After writing all files**, produce the batch report (see "Error & status classification").

## Output format

Each `.md` file (or the single chat output) must match the `spotify-tools` format exactly. Template:

````markdown
# {title}

**{artist}**

---

**{credits line if present, e.g. "作词 : KAZUYA YOSHII"}**
{credits continuation lines if any, e.g. "作曲 : KAZUYA YOSHII"}

**{Japanese original line 1}**  
{Hangul phonetic line 1}  
{Korean meaning line 1}

**{Japanese original line 2}**  
{Hangul phonetic line 2}  
{Korean meaning line 2}

...
````

**Formatting rules** (strict — match `spotify-tools` reference byte-for-byte):

- Title is an H1 `# `.
- Artist is bold `**Artist**` on its own line.
- A single `---` horizontal rule separates header from body.
- Credits block (if any) uses `**bold**` for the first credit line.
- Each Japanese original line is bold `**...**` followed by **2 trailing spaces** (`  `) for a Markdown hard-break.
- Each phonetic line is followed by **2 trailing spaces** (`  `).
- Each meaning line (block's last line) has **no trailing whitespace**.
- Blocks are separated by exactly one blank line.
- Preserve blank lines in the source lyrics (verse breaks) as blank lines between blocks — do **not** output three blank Hangul lines in that case.
- Do not add section labels like "[Verse]", "[Chorus]" unless the source explicitly contained them.

**Low-confidence marker** — if matching confidence was `low` or the chosen URL had partial metadata match, prepend the file with an HTML comment on line 1 (above the H1):

```html
<!-- source: https://..., confidence: low, note: artist partial-match -->
```

**Ambiguous-line marker** — for any line whose meaning you are uncertain about, append `[?]` to the end of the meaning line (not the phonetic line):

```
**心の奥底に眠る**  
코코로노 오쿠소코니 네무루  
마음 속 깊이 잠든 [?]
```

**No-lyrics case** — if the track reached status `no_lyrics`, the file body is exactly:

```
# {title}

**{artist}**

---

(lyrics not available)
```

## Translation rules

Port of `spotify-tools/.../prompts/translation.txt`, adapted for Claude Code invocation. Apply strictly.

### Output shape (per line)

For every non-blank line of Japanese lyrics, output exactly three lines in this order:

1. **Original Japanese** — unchanged.
2. **Hangul phonetic reading** — a syllable-by-syllable rendering of the Japanese pronunciation using Korean characters. This is **not** a meaning translation.
3. **Korean meaning translation** — a natural, fluent Korean rendering of the meaning.

Preserve all original line breaks exactly. Do not merge or split lines.

Blank lines in the source → blank lines in the output (one blank line, not three).

### Translation guidelines

- Prioritize natural fluent Korean over word-for-word literal translation.
- Preserve the emotional tone and register (casual ↔ casual, poetic ↔ poetic, rough ↔ rough).
- Proper nouns (place/brand/character names): keep the original or use standard Korean transliteration.
- Onomatopoeia / mimetic words (キラキラ, ドキドキ, etc.): use the closest natural Korean equivalent.
- Do not add explanatory notes, parentheticals, or interpretations beyond what the original expresses.
- For ambiguous lines, choose the reading most consistent with the song's overall tone. If still uncertain, append `[?]` to the meaning line.

### Phonetic reading rules

- Render each Japanese mora faithfully using Korean syllables.
- **Long vowels are spelled out, not marked with a dash**: `おう`/`おお` → `오오`, `ゆう` → `유우`, `えい` → `에이`, katakana `ー` repeats the preceding vowel (`ヒーロー` → `히이로오`). Never use `-` or the jamo `ㅡ` as a length mark.
- **Sokuon `っ` becomes a ㅅ batchim** on the preceding syllable (`まって` → `맛테`, `ずっと` → `즛토`). Where there is no syllable to carry it — after a closing quote or a `～` — drop it (`「…」って` → `「…」테`).
- `ん` → `ㄴ`/`ㅇ` batchim according to the following consonant; standalone → `은`.
- `じゃ`/`じゅ`/`じょ` → `쟈`/`쥬`/`죠`; `ざ`/`ず`/`ぞ` → `자`/`즈`/`조`.
- Katakana loanwords: render their **Japanese pronunciation** in Hangul (`ラブ → 라부` not `러브`, `タイム → 타이무` not `타임`, `ハート → 하아토` not `하트`).
- Latin-script words inside a line stay **verbatim** in the phonetic line rather than being transliterated.
- Pitch accent and dialect variations are not reflected.
- **Never leave a bare jamo** (`ㅅ`, `ㄴ`) standing alone — compose it into the preceding syllable as a batchim.
- **Never leave kana** (`ん`, `っ`, `ざ`, `ノ` …) sitting in a phonetic line.
- A hyphen in the original that separates repeated interjections (`oh-oh-oh`) is a **separator, not a length mark** — keep the separation instead of merging the vowels.

These are the conventions a mature collection converges on; if the repo you are working in says otherwise, follow the repo.

### Mixed-script lines

Japanese lyrics frequently mix hiragana, katakana, kanji, and romaji within one line.

- Romaji words inside Japanese lines (`my love`, `forever`, `OK`): on the phonetic line, render the romaji using its **sung Japanese pronunciation** (`my love → 마이 러브` only if actually sung that way, else closer to English phonology as sung). On the meaning line, translate naturally into Korean.
- Fully-English lines still get three output lines: English as-is on line 1, Japanese-accented Hangul on line 2, Korean meaning on line 3.
- Kanji with furigana-style gloss in the source: follow the furigana reading, not the dictionary default.

### Repetition & partials

- Chorus repetitions and ad-lib echoes: translate each repeated line individually. Do **not** collapse with `(repeat)` — emit the full 3-line block every occurrence.
- Mid-phrase cutoffs: translate what is present; do not complete.
- Interjection-only lines (`ラララ`, `あーあ`, `yeah yeah`): still emit all three lines. Use the closest Korean interjection; if none fits, `(감탄사)` is acceptable.

### Romanization edge cases

- Loanwords with Japanese-specific meaning (`マンション` = apartment; `テンション` = mood/excitement): translate the Japanese sense, not the English etymology.
- Archaic/literary kanji readings (e.g., `愛しい` read as `かなしい`): use the archaic reading in the phonetic line when strongly indicated by context.
- Elided/contracted forms common in song (`ている→てる`, `ておく→とく`, `では→じゃ`): use the elision in the phonetic line, matching what is sung.

### English-in-Japanese meaning rules

1. Standard English use → natural Korean equivalent (`love → 사랑`).
2. Japanese cultural twist on an English word → translate that twist, not the English.
3. English as pure stylistic/sonic device → retain phonetic rendering in the meaning line, with a short parenthetical only if needed for comprehension.

### Formatting consistency

- Preserve source punctuation (`。、！？…「」`) on line 1.
- Phonetic line omits most Japanese punctuation; use Korean equivalents only where they aid readability.
- Meaning line uses natural Korean punctuation.
- No line numbers, bullets, or markup added to the three output lines.
- Blank source lines → one blank output line.

### Batch quality note

The output is read by Korean fans and is directly compared to `spotify-tools` reference translations. Accuracy in both the phonetic reading and the meaning translation is critical. When in doubt about a reading, prefer the more common pronunciation; when in doubt about meaning, prefer the more natural Korean phrasing.

## Error & status classification

Each track concludes with exactly one status:

| Status | Meaning | File content |
|---|---|---|
| `ok` | Match confidence = high, lyrics fetched and translated in full. | Normal 3-line output, no comment header. |
| `ok_with_low_conf` | Match confidence = medium; translation produced but source needs human spot-check. | Normal output **with** `<!-- source: ..., confidence: medium, note: ... -->` on line 1. |
| `flagged` | Match confidence = low; proceeded anyway to keep the batch moving. | Normal output **with** `<!-- source: ..., confidence: low, note: ... -->` on line 1. |
| `no_lyrics` | All candidate URLs and the fallback query failed to yield lyrics. | `(lyrics not available)` body per the "No-lyrics case" template. |

**Batch report** — after the last track, emit a report:

- Always print a Markdown table to the chat, even when writing files.
- When writing files (≥ 2 tracks), also write `_REPORT.md` in the output folder with the same table plus any per-track notes.

Report columns: `#`, `Song`, `Artist`, `Status`, `Source`, `Note`.

Example:

```
| # | Song | Artist | Status | Source | Note |
|---|------|--------|--------|--------|------|
| 01 | 星が瞬く夜に | BiSH | ok | https://uta-net.com/song/12345/ | — |
| 02 | 本当本気 | BiSH | flagged | https://j-lyric.net/... | artist partial-match |
| 03 | XXX | YYY | no_lyrics | — | 3 candidates + 1 fallback all failed |
```

**Never** silently drop a track from the report. If a track was skipped because the user said so mid-run, still list it with a `skipped` status and a note.

## Anti-patterns

Do **not**:

- Call any external API (OpenAI, DeepL, Spotify Web API, Google Translate). Skill uses only `WebSearch`, `WebFetch`, `Read`, `Write`, `Bash`.
- Use `WebFetch` to fetch lyric bodies. Its backing model blocks full-lyric reproduction. Use `Bash` + `curl` per Stage 3 instead. `WebFetch` is still fine for Spotify playlist/track metadata and for non-lyric web pages.
- Skip matching validation and fetch the top search result blindly. This is the exact failure mode this skill was built to prevent.
- Ask the user to confirm each candidate URL interactively. Flag low confidence in the final report instead.
- Invent lyrics when the source is unclear. Use `[?]` markers or `no_lyrics` status.
- Merge repeating chorus lines with `(×2)` — always emit the full 3-line block per occurrence.
- Append project-specific glossary / tone notes (BiSH `清掃員→청소원` etc.). Keep the skill context-free; user will post-process if needed.
- Write output outside the designated folder (or outside the chat for single tracks).
- Create `_REPORT.md` for single-track runs.
- Convert `.md` to project-specific downstream shapes (JSON schemas, per-line aligned files, etc.). Format conversion is the caller's responsibility.
- Parallelize WebFetch/WebSearch across tracks in a way that changes output ordering. Process tracks sequentially in input order; batched WebSearch is allowed only when ordering is preserved at the result-assembly step.
