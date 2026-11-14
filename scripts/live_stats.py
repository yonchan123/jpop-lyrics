#!/usr/bin/env python3
"""Live-frequency stats from collected setlist history.

usage (from repo root):
  python3 scripts/live_stats.py . scripts/setlists/history/*.json --dry   # print summary only
  python3 scripts/live_stats.py . scripts/setlists/history/*.json         # write READMEs + LIVE_STATS.md

Input format: scripts/setlists/HISTORY_BRIEF.md.
For each '- ALL' folder it writes a '## 라이브 단골곡' section, placed after
'## 최근 공연 셋리스트' (or above the track table when that section is missing).
A song counts once per show, even when it is played twice in that show.
It also writes LIVE_STATS.md at the repo root, a cross-artist summary.
Song matching reuses scripts/setlist_apply.py (normalized titles + ALIAS + repo_title).
"""
import sys, os, re, json, urllib.parse as up
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setlist_apply import parse_tracks, match, esc, ALIAS, norm

HEAD = "## 라이브 단골곡"
TOP = 15
TYPE_KO = {"oneman": "원맨", "tour": "투어", "fes": "페스", "event": "이벤트"}

def resolve(song, rows):
    if "repo_title" in song:
        return match(song["repo_title"], rows) if song["repo_title"] else None
    t = ALIAS.get(song["title"], song["title"])
    r = match(t, rows)
    if not r:
        bare = re.sub(r"\s*[\[［(（][^\]］)）]*[\]］)）]\s*$", "", t)
        if bare and bare != t:
            r = match(ALIAS.get(bare, bare), rows)
    return r

def dedupe(shows):
    seen, out = set(), []
    for s in sorted(shows, key=lambda x: x.get("date", "")):
        k = (s.get("date"), norm(s.get("venue") or ""), norm(s.get("event") or ""))
        if k in seen or not s.get("songs"):
            continue
        seen.add(k); out.append(s)
    return out

def stats(entry, rows):
    shows = dedupe(entry["shows"])
    cnt, last = defaultdict(int), {}
    miss = defaultdict(int)
    for sh in shows:
        played = {}
        for s in sh["songs"]:
            r = resolve(s, rows)
            key = ("R", r["num"]) if r else ("M", s["title"])
            played[key] = r
        for key, r in played.items():
            if r:
                cnt[r["num"]] += 1; last[r["num"]] = sh["date"]
            elif not re.match(r"^[(（]", key[1]):   # skip placeholders like (新曲)
                miss[key[1]] += 1
    return shows, cnt, last, miss

def section(entry, rows, shows, cnt, last, miss):
    n = len(shows)
    types = defaultdict(int)
    for s in shows:
        types[s.get("type", "event")] += 1
    tdesc = " · ".join(f"{TYPE_KO.get(k,k)} {v}" for k, v in sorted(types.items(), key=lambda x: -x[1]))
    byn = {r["num"]: r for r in rows}
    ranked = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    if len(ranked) > TOP:
        cut = ranked[TOP - 1][1]
        ranked = [x for x in ranked if x[1] >= cut][:TOP + 5]
    L = [HEAD, "",
         f"공연 {n}회 기준 ({shows[0]['date']} ~ {shows[-1]['date']}, {tdesc}). 많이 부른 순서다. 같은 공연에서 두 번 부른 곡은 1회로 센다.",
         "", "| 순위 | 곡 | 뜻 | 공연 수 | 비율 | 마지막 |", "|---:|---|---|---:|---:|---|"]
    rank, prev = 0, None
    for i, (num, c) in enumerate(ranked, 1):
        if c != prev:
            rank, prev = i, c
        r = byn[num]
        L.append(f"| {rank} | [{esc(r['title'])}]({r['link']}) | {r['meaning']} | {c} | {round(100*c/n)}% | {last[num]} |")
    never = len(rows) - len(cnt)
    L.append("")
    extra = [f"수록곡 {len(rows)}곡 중 {len(cnt)}곡을 이 기간에 불렀고, {never}곡은 한 번도 부르지 않았다."]
    top_miss = sorted(miss.items(), key=lambda x: -x[1])[:5]
    if top_miss:
        extra.append("번역이 없는데 자주 부른 곡: " + ", ".join(f"{esc(t)} ({c}회)" for t, c in top_miss) + ".")
    if entry.get("note"):
        extra.append(f"참고: {entry['note']}")
    L.append(" ".join(extra))
    L.append("")
    return "\n".join(L)

def insert(t, sec):
    if HEAD in t:
        return re.sub(re.escape(HEAD) + r".*?(?=^## |^\| # |\Z)", sec + "\n", t, flags=re.S | re.M)
    m = re.search(r"^## 최근 공연 셋리스트.*?(?=^## |^\| # |\Z)", t, flags=re.S | re.M)
    if m:
        pos = m.end()
    else:
        m = re.search(r"^## |^\| # ", t, flags=re.M); pos = m.start()
    return t[:pos] + sec + "\n" + t[pos:]

def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    repo, files = args[0], args[1:]
    summary = []
    for jf in files:
        for entry in json.load(open(jf, encoding="utf-8")):
            p = os.path.join(repo, "translation", entry["folder"], "README.md")
            if entry.get("status") != "ok" or not entry.get("shows"):
                print(f"SKIP {entry['folder']}: {entry.get('status')}"); continue
            t = open(p, encoding="utf-8").read()
            rows = parse_tracks(t)
            shows, cnt, last, miss = stats(entry, rows)
            if len(shows) < 3:
                print(f"SKIP {entry['folder']}: only {len(shows)} shows"); continue
            sec = section(entry, rows, shows, cnt, last, miss)
            if not dry:
                open(p, "w", encoding="utf-8").write(insert(t, sec))
            top = sorted(cnt.items(), key=lambda x: -x[1])[:3]
            byn = {r["num"]: r for r in rows}
            summary.append((entry["folder"], len(shows), shows[0]["date"], shows[-1]["date"],
                            [(byn[k], v) for k, v in top], len(cnt), len(rows)))
            print(f"{'DRY' if dry else 'OK '} {entry['folder']}: shows={len(shows)} songs_played={len(cnt)}/{len(rows)} unmatched={sum(miss.values())}")
    if not dry and summary:
        L = ["# 라이브 통계", "",
             "아티스트별로 최근 공연 셋리스트를 모아 어떤 곡을 라이브에서 많이 부르는지 센 결과다. 곡이 너무 많아 어디서부터 들을지 모를 때 기준으로 쓴다.",
             "자세한 순위는 각 폴더 README의 `라이브 단골곡` 섹션에 있다. 데이터: `scripts/setlists/history/`, 생성: `scripts/live_stats.py`.", "",
             "| 아티스트 | 공연 수 | 기간 | 가장 많이 부른 곡 TOP 3 | 부른 곡 / 수록곡 |", "|---|---:|---|---|---:|"]
        for folder, n, d0, d1, top, played, total in sorted(summary, key=lambda x: x[0].lower()):
            base = "translation/" + up.quote(folder) + "/"
            tops = " · ".join(f"[{esc(r['title'])}]({base}{r['link']}) ({c})" for r, c in top)
            L.append(f"| [{esc(folder[:-6])}]({base}) | {n} | {d0} ~ {d1} | {tops} | {played} / {total} |")
        L.append("")
        open(os.path.join(repo, "LIVE_STATS.md"), "w", encoding="utf-8").write("\n".join(L))
        print("wrote LIVE_STATS.md")

if __name__ == "__main__":
    main()
