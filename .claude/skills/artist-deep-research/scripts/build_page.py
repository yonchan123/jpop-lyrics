#!/usr/bin/env python3
"""Render a Markdown research report into the artifact HTML page.

Usage:
  build_page.py <report.md> <out.html> --title "아티스트 종합 연구"
                --eyebrow "ARTIST · Romaji · 2014 — 2026" --subtitle "한 줄 설명"
                [--template path] [--accent "#3a4fb8"] [--accent-dark "#9fb0ff"]

The page H1 is the report's first "# " heading. The Markdown is embedded as a
JSON string and rendered client-side with marked (cdnjs, pinned). Bold tags
**[확인]** **[본인]** **[평론]** **[해석]** become coloured chips.
"""
import argparse, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("out")
    ap.add_argument("--title", required=True)
    ap.add_argument("--eyebrow", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--template", default=os.path.join(HERE, "..", "assets", "page_template.html"))
    ap.add_argument("--accent", default="#3a4fb8")
    ap.add_argument("--accent-dark", default="#9fb0ff")
    a = ap.parse_args()

    md = open(a.report, encoding="utf-8").read()
    m = re.search(r"^# (.+)$", md, re.M)
    h1 = m.group(1).strip() if m else a.title
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = open(a.template, encoding="utf-8").read()
    rep = {
        "__TITLE__": esc(a.title), "__H1__": esc(h1), "__EYEBROW__": esc(a.eyebrow),
        "__SUBTITLE__": esc(a.subtitle), "__ACCENT__": a.accent, "__ACCENT_DARK__": a.accent_dark,
        "__MD_JSON__": json.dumps(md, ensure_ascii=False).replace("</", "<\\/"),
    }
    for k, v in rep.items():
        t = t.replace(k, v)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(t)
    print(f"wrote {a.out} ({os.path.getsize(a.out)} bytes)")


if __name__ == "__main__":
    main()
