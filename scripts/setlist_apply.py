#!/usr/bin/env python3
"""Insert/replace a '## 최근 공연 셋리스트' section in each '- ALL' folder README.

usage (from repo root):
  python3 scripts/setlist_apply.py . scripts/setlists/2026-11-15.json --dry   # report matches only
  python3 scripts/setlist_apply.py . scripts/setlists/2026-11-15.json         # write READMEs

JSON format and how to collect setlists: scripts/setlists/BRIEF.md (CLAUDE.md §4).
Matching: NFKC + punctuation-insensitive title match against the README track table,
then version-suffix strip, then unique substring; ALIAS covers known spelling variants.
A song entry may carry "repo_title" (exact repo title, or null = not in repo) to override.
Re-running is idempotent: the existing section is replaced up to the next '## ' heading or
the track table header ('| # |'), so READMEs without a '## Tracks' heading are safe.
"""
import sys, os, re, json, unicodedata

HEAD = "## 최근 공연 셋리스트"
ALIAS = {"流星鎮魂歌": "竜星鎮魂歌", "TARINAI": "足りない", "大事なものは大事にできたら": "大事なことは大事にできたら", "ストウドロップ": "スノウドロップ", "ロングスカートは履いて": "ロングスカートは靡いて", "The End of F***ing World": "The End of the F***ing World", "Comming-of-age-Story": "Coming-of-age Story", "天球(そら)のMúsica": "天球のMúsica"}

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[\s　・·'‘’\"“”!！?？,，.。、~〜～\-‐–—_/\\()（）\[\]「」『』【】<>＜＞:：;；#＃&＆*＊+＋=♪☆★♡♥…]", "", s)
    return s

def strip_ver(s):
    return re.sub(r"(ver|version|remix|acoustic|liveversion|edit|mix)$", "", s)

def parse_tracks(readme):
    rows = []
    for line in readme.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|([^|]*)\|\s*\[(.+?)\]\(([^)]+)\)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$", line)
        if m:
            rows.append(dict(num=int(m.group(1)), title=m.group(3).replace("\\|", "|"), link=m.group(4),
                             reading=m.group(6).strip(), meaning=m.group(7).strip()))
    return rows

def match(title, rows):
    n = norm(title)
    if not n:
        return None
    exact = [r for r in rows if norm(r["title"]) == n]
    if exact:
        return exact[0]
    n2 = strip_ver(n)
    loose = [r for r in rows if strip_ver(norm(r["title"])) == n2]
    if loose:
        return loose[0]
    cont = [r for r in rows if len(n) >= 3 and (n in norm(r["title"]) or norm(r["title"]) in n) and len(norm(r["title"])) >= 3]
    if len(cont) == 1:
        return cont[0]
    return None

def esc(s):
    return s.replace("|", "\\|")

def build(entry, rows):
    L = [HEAD, ""]
    meta = [f"**{esc(entry['event'])}**", entry.get("date", "")]
    v = " ".join(x for x in [entry.get("venue", ""), f"({entry['city']})" if entry.get("city") else ""] if x)
    if v:
        meta.append(v)
    L.append(" · ".join(x for x in meta if x))
    src = f"[출처]({entry['source_url']})" if entry.get("source_url") else ""
    conf = {"high": "", "medium": " · 신뢰도 보통", "low": " · 신뢰도 낮음 (팬 기록)"}.get(entry.get("confidence", ""), "")
    note = f" · {entry['note']}" if entry.get("note") else ""
    L.append("")
    L.append(f"어디서부터 볼지 모르겠으면 이 셋리스트 순서대로 들어 보자. 곡명을 누르면 번역으로 간다. {src}{conf}{note}".rstrip())
    L += ["", "| 순서 | 곡 | 읽기 | 뜻 |", "|---:|---|---|---|"]
    hit = miss = 0
    i = e = 0
    for s in entry["songs"]:
        if s.get("encore"):
            e += 1; idx = f"EN{e}"
        else:
            i += 1; idx = str(i)
        if "repo_title" in s:
            r = match(s["repo_title"], rows) if s["repo_title"] else None
        else:
            r = match(ALIAS.get(s["title"], s["title"]), rows)
        if r:
            hit += 1
            L.append(f"| {idx} | [{esc(r['title'])}]({r['link']}) | {r['reading']} | {r['meaning']} |")
        else:
            miss += 1
            L.append(f"| {idx} | {esc(s['title'])} | — | 미수록 |")
    L.append("")
    return "\n".join(L), hit, miss

def apply(repo, entry, dry):
    p = os.path.join(repo, "translation", entry["folder"], "README.md")
    t = open(p, encoding="utf-8").read()
    rows = parse_tracks(t)
    sec, hit, miss = build(entry, rows)
    if HEAD in t:
        t2 = re.sub(re.escape(HEAD) + r".*?(?=^## |^\| # |\Z)", sec + "\n", t, flags=re.S | re.M)
    else:
        m = re.search(r"^## ", t, flags=re.M)
        if not m:
            m = re.search(r"^\| #", t, flags=re.M)
        t2 = t[:m.start()] + sec + "\n" + t[m.start():]
    if not dry:
        open(p, "w", encoding="utf-8").write(t2)
    return len(rows), hit, miss

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    repo = args[0]
    for jf in args[1:]:
        for entry in json.load(open(jf, encoding="utf-8")):
            if entry.get("status") != "ok" or not entry.get("songs"):
                print(f"SKIP  {entry['folder']}: {entry.get('status')} {entry.get('note','')}")
                continue
            n, hit, miss = apply(repo, entry, dry)
            print(f"{'DRY ' if dry else 'OK  '} {entry['folder']}: tracks={n} setlist={hit+miss} matched={hit} miss={miss}")
