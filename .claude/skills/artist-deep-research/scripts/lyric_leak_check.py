#!/usr/bin/env python3
"""Check that a report does not reproduce lyrics from a translation collection.

Flags any run of >= --ja-window consecutive characters of an original Japanese
lyric line, or >= --ko-window characters of a Korean meaning line, that appears
verbatim in the report. Song titles are whitelisted (titles may be named).

Usage: lyric_leak_check.py <collection_dir> <report.md> [--ja-window 10] [--ko-window 16]
Exit code 1 if anything is found.
"""
import argparse, glob, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from corpus_stats import parse_song  # noqa: E402


def norm(s):
    return re.sub(r"[\s　*、。,.!?！？「」『』\"'“”‘’()（）\-—…~〜・]", "", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("collection")
    ap.add_argument("report")
    ap.add_argument("--ja-window", type=int, default=10)
    ap.add_argument("--ko-window", type=int, default=16)
    a = ap.parse_args()

    report = norm(open(a.report, encoding="utf-8").read())
    titles = []
    lines = []
    for f in sorted(glob.glob(os.path.join(a.collection, "[0-9]*.md"))):
        title, _, _, orig, mean = parse_song(f)
        titles.append(norm(title))
        lines += [("JA", title, i + 1, l, a.ja_window) for i, l in enumerate(orig)]
        lines += [("KO", title, i + 1, l, a.ko_window) for i, l in enumerate(mean)]

    hits = {}
    for kind, title, idx, line, win in lines:
        n = norm(line)
        if len(n) < win:
            continue
        for i in range(len(n) - win + 1):
            frag = n[i:i + win]
            if any(frag in t for t in titles):
                continue
            if frag in report:
                hits.setdefault((kind, title, idx), len(frag))
                break
    if not hits:
        print(f"OK — no lyric fragments (JA≥{a.ja_window}, KO≥{a.ko_window} chars) found in report")
        return 0
    # Report locations only — printing the matched text would itself reproduce lyrics.
    print(f"FOUND {len(hits)} lyric lines with verbatim fragments in the report:")
    for (kind, title, idx), n in hits.items():
        line_kind = "original line" if kind == "JA" else "meaning line"
        print(f"  {title}: {line_kind} #{idx} (≥{n} chars match) — paraphrase that passage")
    return 1


if __name__ == "__main__":
    sys.exit(main())
