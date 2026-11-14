#!/usr/bin/env python3
"""Corpus extraction + statistics for one translation collection.

Reads `translation/{collection}/NN. {title} - {artist}.md` files (3-line JA→KO
format) plus the folder README table (for release dates), and writes:

  meaning.txt   one line per song: "[NN title] meaning/meaning/..." (deduped
                Korean meaning lines) — for the lyric-worldview analyst to read
  credits.tsv   num, title, release date, lyricist, composer, blocks
  stats.md      keyword song-coverage by era, pronoun table, credits summary,
                and the list of songs NOT written by the main lyricist (covers)

Usage:
  corpus_stats.py <collection_dir> <out_dir> [--lyricist NAME]
                  [--eras 2015-2018,2019-2022,2023-2026] [--words extra1,extra2]

--lyricist defaults to the most frequent 作词 credit in the folder. Pass
several comma-separated names when one writer uses aliases (e.g. 朝日,朝日廉,石風呂).
--eras defaults to three equal splits by release order.
"""
import argparse, collections, glob, os, re, sys, urllib.parse

DEFAULT_WORDS = {
    "僕/ぼく": r"僕|ぼく", "私/わたし": r"私|わたし", "俺": r"俺", "君/きみ": r"君|きみ",
    "あなた": r"あなた|貴方", "死/殺": r"死|殺", "戦": r"戦", "夜": r"夜", "空": r"空",
    "星": r"星", "月": r"月", "光": r"光|ひかり", "朝": r"朝", "海": r"海", "雨": r"雨",
    "涙/泣": r"涙|泣", "笑": r"笑", "痛": r"痛", "好き": r"好き", "愛": r"愛",
    "嘘": r"嘘", "夢": r"夢", "帰": r"帰", "息/呼吸": r"息|呼吸", "母/ママ": r"母|ママ",
    "窓": r"窓", "電車/線/駅": r"電車|線|列車|駅", "街/都市": r"街|都市|東京",
    "美し/きれい": r"美し|きれい|綺麗", "神": r"神", "心": r"心", "世界": r"世界",
}


def parse_song(path):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else ""
    lyricist = composer = ""
    m = re.search(r"\*\*作[词詞]\s*[:：]\s*(.+?)\*\*", text)
    if m:
        lyricist = m.group(1).strip()
    m = re.search(r"^(?:작곡|作曲)\s*[:：]\s*(.+?)\s*$", text, re.M)
    if m:
        composer = m.group(1).strip()
    originals, meanings = [], []
    for block in re.split(r"\n\s*\n", text):
        bl = [l for l in block.splitlines() if l.strip()]
        if len(bl) < 3 or not bl[0].startswith("**"):
            continue
        head = bl[0].strip("* ").rstrip()
        if re.match(r"作[词詞]|作曲|편곡", head):
            continue
        # Some files stack several 3-line triplets without a blank line between
        # them; split on each bold original line so no triplet is dropped.
        starts = [i for i, l in enumerate(bl) if l.startswith("**")]
        for j, s in enumerate(starts):
            e = starts[j + 1] if j + 1 < len(starts) else len(bl)
            if e - s < 3:
                continue
            originals.append(re.sub(r"\*+", "", bl[s]).strip())
            meanings.append(bl[e - 1].strip())
    return title, lyricist, composer, originals, meanings


def readme_dates(folder):
    dates = {}
    p = os.path.join(folder, "README.md")
    if not os.path.exists(p):
        return dates
    for row in open(p, encoding="utf-8"):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].isdigit():
            dates[int(cells[0])] = cells[1]
    return dates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("collection")
    ap.add_argument("out")
    ap.add_argument("--lyricist")
    ap.add_argument("--eras")
    ap.add_argument("--words", default="")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.collection, "[0-9]*.md")))
    if not files:
        sys.exit(f"no song files in {a.collection}")
    dates = readme_dates(a.collection)
    songs = []
    for f in files:
        num = int(os.path.basename(f).split(".")[0])
        title, lyr, comp, orig, mean = parse_song(f)
        songs.append(dict(num=num, title=title, lyricist=lyr, composer=comp,
                          orig=orig, mean=mean, date=dates.get(num, "")))

    counts = collections.Counter(s["lyricist"] for s in songs if s["lyricist"])
    aliases = [x.strip() for x in a.lyricist.split(",")] if a.lyricist else \
        ([counts.most_common(1)[0][0]] if counts else [])
    main_lyr = " / ".join(aliases)
    own = [s for s in songs if s["lyricist"] in aliases and s["orig"]]
    others = [s for s in songs if s["lyricist"] and s["lyricist"] not in aliases]
    empty = [s for s in songs if not s["orig"]]

    # eras
    eras = []
    if a.eras:
        for rng in a.eras.split(","):
            lo, hi = rng.split("-")
            eras.append((rng, lambda s, lo=lo, hi=hi: lo <= (s["date"][:4] or "0000") <= hi))
    else:
        n = len(own); k = max(1, n // 3)
        cut = [own[:k], own[k:2 * k], own[2 * k:]]
        for i, grp in enumerate(cut):
            if not grp:
                continue
            ids = {s["num"] for s in grp}
            label = f"{grp[0]['date'][:4] or '?'}–{grp[-1]['date'][:4] or '?'} (#{grp[0]['num']}–{grp[-1]['num']})"
            eras.append((label, lambda s, ids=ids: s["num"] in ids))

    words = dict(DEFAULT_WORDS)
    for w in filter(None, a.words.split(",")):
        words[w] = re.escape(w)

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "meaning.txt"), "w", encoding="utf-8") as fh:
        for s in own:
            seen = list(dict.fromkeys(s["mean"]))
            fh.write(f"[{s['num']:02d} {s['title']}] " + "/".join(seen) + "\n")
    with open(os.path.join(a.out, "credits.tsv"), "w", encoding="utf-8") as fh:
        fh.write("num\ttitle\tdate\tlyricist\tcomposer\tblocks\n")
        for s in songs:
            fh.write(f"{s['num']}\t{s['title']}\t{s['date']}\t{s['lyricist']}\t{s['composer']}\t{len(s['orig'])}\n")

    out = []
    out.append(f"# Corpus stats — {os.path.basename(os.path.normpath(a.collection))}\n")
    out.append(f"- songs in folder: {len(songs)}")
    out.append(f"- main lyricist: **{main_lyr}** — {len(own)} songs with lyrics analysed")
    out.append(f"- other lyricists (covers / outside writers): {len(others)}")
    out.append(f"- no lyrics / instrumental stubs: {len(empty)}\n")
    out.append("## Keyword coverage (share of songs containing the word, original Japanese)\n")
    groups = [(lab, [s for s in own if f(s)]) for lab, f in eras]
    out.append("| word | " + " | ".join(f"{lab} [{len(g)}곡]" for lab, g in groups) + " |")
    out.append("|---|" + "---:|" * len(groups))
    for w, rx in words.items():
        r = re.compile(rx)
        cells = []
        for _, g in groups:
            hit = sum(1 for s in g if r.search("\n".join(s["orig"])))
            cells.append(f"{hit / len(g) * 100:.0f}%" if g else "–")
        out.append(f"| {w} | " + " | ".join(cells) + " |")
    out.append("\nRegex counts are approximate (月 also hits dates, 線 hits line names, etc.).\n")
    out.append("## Lyricist credits\n")
    for name, c in counts.most_common():
        out.append(f"- {name}: {c}")
    if others:
        out.append("\n## Songs not by the main lyricist (likely covers / tributes / outside writers)\n")
        out.append("| # | title | date | lyricist | composer |")
        out.append("|---:|---|---|---|---|")
        for s in others:
            out.append(f"| {s['num']} | {s['title']} | {s['date']} | {s['lyricist']} | {s['composer']} |")
    open(os.path.join(a.out, "stats.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out[:6]))
    print(f"wrote meaning.txt ({os.path.getsize(os.path.join(a.out, 'meaning.txt'))} bytes), credits.tsv, stats.md → {a.out}")


if __name__ == "__main__":
    main()
